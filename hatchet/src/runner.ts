import { spawn } from "node:child_process";
import { resolve as pathResolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { runnerTerminalSchema, type RunnerTerminal, type StageName } from "./contracts.js";
import { DeterministicInputError, RunnerCancelledError, TransientRunnerError } from "./errors.js";

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

export async function invokeRunner(request: RunnerRequest, signal: AbortSignal): Promise<RunnerTerminal> {
  const executable = process.env.OMP_RECIPE_RUNNER ?? defaultRunnerPath;
  if (signal.aborted) {
    throw new RunnerCancelledError("runner cancelled before start");
  }

  return await new Promise<RunnerTerminal>((resolve, reject) => {
    const child = spawn(executable, [
      "--recipe", request.recipePath,
      "--task", request.task,
      "--cwd", request.cwd,
      "--stage", request.stage,
      "--round", String(request.round),
      "--head-sha", request.expectedHeadSha,
    ], {
      cwd: request.cwd,
      detached: true,
      env: runnerEnvironment(),
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = Buffer.alloc(0);
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
        const detail = `runner exited ${code ?? "without code"}; stderr bytes=${stderrBytes}`;
        reject(deterministicExitCodes[code ?? -1] === true
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
}

export async function invokeRunnerWithRetry(
  request: RunnerRequest,
  signal: AbortSignal,
  sleeper: RetrySleeper = defaultSleeper,
  maxAttempts = 3,
): Promise<RunnerAttempt> {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      return { terminal: await invokeRunner(request, signal), attempts: attempt };
    } catch (error) {
      if (!(error instanceof TransientRunnerError) || attempt === maxAttempts) {
        throw error;
      }
      await sleeper(Math.min(250 * 2 ** (attempt - 1), 2_000), signal);
    }
  }
  throw new Error("unreachable runner retry state");
}
