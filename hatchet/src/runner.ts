import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { chmod, cp, readFile, realpath, rm, stat, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, dirname, extname, join, resolve as pathResolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import type { CardFacts } from "./contracts.js";
import { runnerTerminalSchema, type RunnerTerminal, type StageName } from "./contracts.js";
import { DeterministicInputError, RunnerCancelledError, StageTimeoutError, TransientRunnerError, stageTimeoutExitCode } from "./errors.js";
import { renderRecipe } from "./recipe-template.js";

const stderrTailLimit = 2 * 1024;
const deterministicExitCodes: Record<number, true> = { 64: true, 65: true, 66: true, 78: true };
const outputLimit = 1024 * 1024;
const defaultRunnerPath = fileURLToPath(new URL("../scripts/recipe-runner", import.meta.url));
const cancellationGraceMs = 60_000;
const runnerEnvironmentKeys = [
  "PATH",
  "TMPDIR",
  "LANG",
  "LC_ALL",
  "TERM",
  "SSL_CERT_FILE",
  "SSL_CERT_DIR",
  "NO_PROXY",
  "OMP_RECIPE_COMPILER",
  "OMP_RECIPE_PYTHON",
  "OMP_RECIPE_OMP_SOURCE",
  "OMP_RECIPE_RPC_CLIENT_MODULE",
  "OMP_RECIPE_CLI_PATH",
  "OMP_RECIPE_SHARED_RUNNER_MODULE",
] as const;
// Written by recipe-runner-adapter.ts's `onPrepared` hook immediately after
// `global/lib/recipe-task-runner.ts` mints the runtime root — always
// `<realpath(tmpdir())>/omp-recipe-task-<uuid v4>`. `reclaimRuntimeRoot`
// checks a candidate against this exact shape before ever calling `rm
// --recursive`, so a corrupted or unexpected receipt can never widen the
// blast radius of this parent-owned cleanup past that one directory pattern.
const runtimeRootBasenamePattern = /^omp-recipe-task-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function runnerEnvironment(source: NodeJS.ProcessEnv = process.env): NodeJS.ProcessEnv {
  const environment: NodeJS.ProcessEnv = {};
  for (const key of runnerEnvironmentKeys) {
    const value = source[key];
    if (value !== undefined) environment[key] = value;
  }
  return environment;
}

export type RunnerRequest = {
  recipePath: string;
  task: string;
  cwd: string;
  stage: StageName;
  round: number;
  expectedHeadSha: string;
  card: CardFacts;
};

export type RunnerAttempt = {
  terminal: RunnerTerminal;
  attempts: number;
};

export type RetrySleeper = (milliseconds: number, signal: AbortSignal) => Promise<void>;

export const defaultSleeper: RetrySleeper = async (milliseconds, signal) => {
  try {
    await delay(milliseconds, undefined, { signal });
  } catch {
    throw new RunnerCancelledError("runner retry cancelled");
  }
};

function killProcessGroup(pid: number, signal: NodeJS.Signals): void {
  try {
    process.kill(-pid, signal);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ESRCH") {
      throw error;
    }
  }
}

function signalProcess(pid: number, signal: NodeJS.Signals): void {
  try {
    process.kill(pid, signal);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ESRCH") throw error;
  }
}

// Parent-owned defense against the adapter subprocess dying (OS SIGTERM,
// SIGKILL, crash) before its own async `cleanupRuntimeRoot` can run. This
// process pre-creates a private receipt file and hands the child only its
// path (see `invokeRunner`); the child writes its runtime root into it
// immediately after prepare, well before any RpcClient/model work begins.
// Once the spawned adapter is reaped — resolve or reject, it makes no
// difference — `invokeRunner` always re-reads the receipt and reclaims
// whatever it names, so a mid-flight kill can never leak a runtime root.
// The adapter's own graceful cleanup still runs in the common case; this is
// strictly additional and idempotent — a root the adapter already removed
// just yields ENOENT here and is skipped, not treated as an error.
async function reclaimRuntimeRoot(candidateRoot: string): Promise<void> {
  let resolvedRoot: string;
  let resolvedTmpdir: string;
  try {
    [resolvedRoot, resolvedTmpdir] = await Promise.all([realpath(candidateRoot), realpath(tmpdir())]);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return;
    throw error;
  }
  if (dirname(resolvedRoot) !== resolvedTmpdir || !runtimeRootBasenamePattern.test(basename(resolvedRoot))) {
    throw new Error(`refusing to reclaim runtime root receipt outside the expected shape: ${candidateRoot}`);
  }
  await rm(resolvedRoot, { recursive: true, force: true });
}

async function reclaimRuntimeReceipt(receiptPath: string): Promise<void> {
  let content: string;
  try {
    content = (await readFile(receiptPath, "utf8")).trim();
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return;
    throw error;
  }
  if (content.length > 0) await reclaimRuntimeRoot(content);
  await rm(receiptPath, { force: true });
}

export async function invokeRunner(request: RunnerRequest, signal: AbortSignal): Promise<RunnerTerminal> {
  const executable = process.env.OMP_RECIPE_RUNNER ?? defaultRunnerPath;
  if (signal.aborted) {
    throw new RunnerCancelledError("runner cancelled before start");
  }

  // Created before the child ever spawns, mode 0600, exclusive create so a
  // uuid collision fails loudly instead of silently reusing a stale receipt.
  // Only its path crosses into the child's env — never its own contents.
  const receiptPath = join(tmpdir(), `omp-recipe-receipt-${randomUUID()}`);
  await writeFile(receiptPath, "", { mode: 0o600, flag: "wx" });

  // request.recipePath is always a template, one way or another: a FILE is
  // read and rendered directly; a DIRECTORY is an already-compiled
  // omp.recipe.v1 bundle (skills/models/runtime baked in by
  // bin/omp_recipe.py's compile_recipe) whose `instructions.md` is the
  // actual stage prompt, so the whole bundle is copied to a fresh per-run
  // path first and only the COPY's instructions.md gets rendered — the
  // parent must never mutate a bundle another concurrent run may still be
  // reading. Either way, the result is a fresh path under tmpdir(), same
  // discipline as the receipt above (unique uuid name, exclusive create,
  // removed in the shared `finally` below) so a rendered prompt or bundle
  // copy can never leak across runs or survive a crash.
  let recipeArgPath = request.recipePath;
  let renderedRecipePath: string | undefined;
  const recipeContext = {
    card: request.card,
    stage: request.stage,
    round: request.round,
    headSha: request.expectedHeadSha,
    task: request.task,
  };

  try {
    const recipeStat = await stat(request.recipePath);
    if (recipeStat.isDirectory()) {
      renderedRecipePath = join(tmpdir(), `omp-recipe-bundle-${randomUUID()}`);
      // `dereference: true` guarantees the copy can never contain a
      // symlink even if the source somehow did — `load_recipe`/
      // `_regular_file` reject a symlinked bundle root or member outright,
      // and `.omp-recipe-owned` must stay a real file with exact content.
      await cp(request.recipePath, renderedRecipePath, {
        recursive: true,
        dereference: true,
        force: false,
        errorOnExist: true,
      });
      const instructionsPath = join(renderedRecipePath, "instructions.md");
      // The compiled bundle may ship its files read-only; preserve
      // whatever mode the copy inherited from the source once the render
      // is written back, rather than assuming a specific mode either way.
      const originalMode = (await stat(instructionsPath)).mode & 0o777;
      const template = await readFile(instructionsPath, "utf8");
      const renderedInstructions = renderRecipe(template, recipeContext);
      await chmod(instructionsPath, 0o600);
      await writeFile(instructionsPath, renderedInstructions, "utf8");
      await chmod(instructionsPath, originalMode);
      recipeArgPath = renderedRecipePath;
    } else {
      renderedRecipePath = join(
        tmpdir(),
        `omp-recipe-rendered-${randomUUID()}${extname(request.recipePath)}`,
      );
      const template = await readFile(request.recipePath, "utf8");
      const renderedRecipe = renderRecipe(template, recipeContext);
      await writeFile(renderedRecipePath, renderedRecipe, { mode: 0o600, flag: "wx" });
      recipeArgPath = renderedRecipePath;
    }

    return await new Promise<RunnerTerminal>((resolve, reject) => {
      const child = spawn(executable, [
        "--recipe", recipeArgPath,
      "--task", request.task,
      "--cwd", request.cwd,
      "--stage", request.stage,
      "--round", String(request.round),
      "--head-sha", request.expectedHeadSha,
    ], {
      cwd: request.cwd,
      detached: true,
      env: { ...runnerEnvironment(), OMP_RECIPE_RUNTIME_RECEIPT: receiptPath },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = Buffer.alloc(0);
    let stderrTail = Buffer.alloc(0);
    let stderrBytes = 0;
    let outputExceeded = false;
    let forceKillTimer: NodeJS.Timeout | undefined;
    let cancellationRequested = false;

    child.stdout.on("data", (chunk: Buffer) => {
      if (stdout.length + chunk.length > outputLimit) {
        outputExceeded = true;
        killProcessGroup(child.pid!, "SIGTERM");
        return;
      }
      stdout = Buffer.concat([stdout, chunk]);
    });
    child.stderr.on("data", (chunk: Buffer) => {
      stderrBytes += chunk.length;
      const combined = Buffer.concat([stderrTail, chunk]);
      stderrTail = combined.length > stderrTailLimit
        ? combined.subarray(combined.length - stderrTailLimit)
        : combined;
      if (stderrBytes > outputLimit) {
        outputExceeded = true;
        killProcessGroup(child.pid!, "SIGTERM");
      }
    });

    const abort = () => {
      cancellationRequested = true;
      if (child.pid !== undefined) {
        if (pathResolve(executable) === pathResolve(defaultRunnerPath)) signalProcess(child.pid, "SIGTERM");
        else killProcessGroup(child.pid, "SIGTERM");
        forceKillTimer = setTimeout(() => killProcessGroup(child.pid!, "SIGKILL"), cancellationGraceMs);
        forceKillTimer.unref();
      }
    };
    signal.addEventListener("abort", abort, { once: true });

    child.once("error", (error) => {
      signal.removeEventListener("abort", abort);
      clearTimeout(forceKillTimer);
      reject(new TransientRunnerError(`runner could not start: ${error.message}`));
    });

    child.once("close", (code, termSignal) => {
      signal.removeEventListener("abort", abort);
      clearTimeout(forceKillTimer);
      if (cancellationRequested || signal.aborted) {
        reject(new RunnerCancelledError(`runner cancelled and reaped (${termSignal ?? code ?? "unknown"})`));
        return;
      }
      if (outputExceeded) {
        reject(new DeterministicInputError(`runner output exceeded ${outputLimit} bytes`));
        return;
      }
      if (code !== 0) {
        const detail = [
          `runner exited ${code ?? "without code"}`,
          `stderr bytes=${stderrBytes}`,
          `stderr tail=${JSON.stringify(stderrTail.toString("utf8"))}`,
        ].join("; ");
        reject(code === stageTimeoutExitCode
          ? new StageTimeoutError(detail)
          : deterministicExitCodes[code ?? -1] === true
            ? new DeterministicInputError(detail)
            : new TransientRunnerError(detail));
        return;
      }
      try {
        const decoded: unknown = JSON.parse(stdout.toString("utf8"));
        resolve(runnerTerminalSchema.parse(decoded));
      } catch {
        reject(new DeterministicInputError("runner returned invalid terminal JSON"));
      }
    });
  });
  } finally {
    if (renderedRecipePath !== undefined) {
      await rm(renderedRecipePath, { recursive: true, force: true }).catch((error) => {
        process.stderr.write(
          `hatchet-runner: rendered recipe cleanup failed: ${error instanceof Error ? error.message : String(error)}\n`,
        );
      });
    }
    await reclaimRuntimeReceipt(receiptPath).catch((error) => {
      process.stderr.write(
        `hatchet-runner: runtime root receipt reclaim failed: ${error instanceof Error ? error.message : String(error)}\n`,
      );
    });
  }
}

// Attempts and backoff are sized for what actually makes a stage transient
// here: machine contention. A cold OMP start has a hardcoded 30s readiness cap
// in the rpc-client, and on a loaded box (measured: load average 9.8 with the
// factory, an operator session and review lanes all live) that cap is what
// trips, not anything slow in the stage - the bundle is 28K, prepare-runtime
// is 86ms and a bare `omp` starts in half a second.
//
// A load spike lasts minutes, so the retry window has to outlast one. Delays
// are 1s, 4s, 16s, 64s, 120s: ~3.4 minutes of backoff across six attempts,
// plus the ~30s each failed readiness attempt burns before giving up, for
// roughly six minutes of tolerance. The window is pinned by a test, because an
// earlier version of this capped at 60s yet never exceeded 2s in practice: the
// exponent ran out of attempts long before it reached its own ceiling.
const retryBaseMs = 1_000;
const retryFactor = 4;
const retryCeilingMs = 120_000;

export function retryDelayMs(attempt: number): number {
  return Math.min(retryBaseMs * retryFactor ** (attempt - 1), retryCeilingMs);
}

export async function invokeRunnerWithRetry(
  request: RunnerRequest,
  signal: AbortSignal,
  sleeper: RetrySleeper = defaultSleeper,
  maxAttempts = 6,
): Promise<RunnerAttempt> {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      return { terminal: await invokeRunner(request, signal), attempts: attempt };
    } catch (error) {
      if (!(error instanceof TransientRunnerError) || attempt === maxAttempts) {
        throw error;
      }
      await sleeper(retryDelayMs(attempt), signal);
    }
  }
  throw new Error("unreachable runner retry state");
}
