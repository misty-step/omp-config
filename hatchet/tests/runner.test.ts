import { execFileSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { access, mkdir, readdir, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { describe, expect, it } from "vitest";
import { defaultSleeper, invokeRunner, invokeRunnerWithRetry, runnerEnvironment } from "../src/runner.js";
import type { StageName } from "../src/contracts.js";
import { DeterministicInputError, RunnerCancelledError, TransientRunnerError } from "../src/errors.js";

const fixtureRoot = new URL("../fixtures/", import.meta.url);
const runnerPath = new URL("recipe-runner.sh", fixtureRoot).pathname;
process.env.OMP_RECIPE_RUNNER = runnerPath;

function scenarioPath(name: string): string {
  return new URL(`scenarios/${name}.sh`, fixtureRoot).pathname;
}

async function gitInit(cwd: string): Promise<string> {
  const { rm, mkdir } = await import("node:fs/promises");
  await rm(cwd, { recursive: true, force: true });
  await mkdir(cwd, { recursive: true, mode: 0o700 });
  const { execFile } = await import("node:child_process");
  const { promisify } = await import("node:util");
  const exec = promisify(execFile);
  await exec("git", ["-C", cwd, "init", "-q"]);
  await exec("git", ["-C", cwd, "config", "user.email", "fixture@omp.test"]);
  await exec("git", ["-C", cwd, "config", "user.name", "OMP Fixture"]);
  await exec("git", ["-C", cwd, "commit", "--allow-empty", "-m", "fixture seed"]);
  const { stdout } = await exec("git", ["-C", cwd, "rev-parse", "HEAD"]);
  return stdout.trim();
}

function pidIsAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function findPidByCommandSubstring(substring: string): number | undefined {
  try {
    const output = execFileSync("pgrep", ["-f", substring], { encoding: "utf8" });
    const pid = Number(output.trim().split("\n")[0]);
    return Number.isInteger(pid) && pid > 0 ? pid : undefined;
  } catch {
    return undefined;
  }
}

function compileFixtureBundle(recipeJsonPath: string, output: string): void {
  const binDir = new URL("../../bin", import.meta.url).pathname;
  const script = [
    "import sys",
    "from pathlib import Path",
    `sys.path.insert(0, ${JSON.stringify(binDir)})`,
    "from omp_recipe import compile_recipe",
    "compile_recipe(Path(sys.argv[1]), Path(sys.argv[2]))",
  ].join(";");
  execFileSync("/usr/bin/python3", ["-c", script, recipeJsonPath, output]);
}

describe("runner adapter", () => {
  it("passes only the positive runner launch allowlist", () => {
    expect(runnerEnvironment({
      PATH: "/usr/bin",
      LANG: "en_US.UTF-8",
      OMP_RECIPE_CLI_PATH: "/opt/omp",
      HATCHET_CLIENT_TOKEN: "must-not-cross",
      RANDOM_WORKER_SECRET: "must-not-cross",
    })).toEqual({
      PATH: "/usr/bin",
      LANG: "en_US.UTF-8",
      OMP_RECIPE_CLI_PATH: "/opt/omp",
    });
  });

  it("parses a valid terminal JSON object", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-ok`;
    const headSha = await gitInit(cwd);
    const terminal = await invokeRunner({
      recipePath: scenarioPath("happy"),
      task: "runner test",
      cwd,
      stage: "implement",
      round: 1,
      expectedHeadSha: headSha,
    }, new AbortController().signal);
    expect(terminal.outcome).toBe("completed");
  });

  it("treats exit 64 as deterministic non-retryable", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-det`;
    const headSha = await gitInit(cwd);
    await expect(invokeRunner({
      recipePath: scenarioPath("happy"),
      task: "det",
      cwd,
      stage: "unknown" as unknown as StageName,
      round: 1,
      expectedHeadSha: headSha,
    }, new AbortController().signal)).rejects.toBeInstanceOf(DeterministicInputError);
  });

  it("retries transient exit 70 and eventually succeeds", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-transient`;
    const headSha = await gitInit(cwd);
    const attempt = await invokeRunnerWithRetry({
      recipePath: scenarioPath("transient"),
      task: "transient",
      cwd,
      stage: "implement",
      round: 1,
      expectedHeadSha: headSha,
    }, new AbortController().signal);
    expect(attempt.attempts).toBeGreaterThan(1);
    expect(attempt.terminal.outcome).toBe("completed");
  });

  it("aborts and reaps the child process", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-cancel`;
    const headSha = await gitInit(cwd);
    const controller = new AbortController();
    const run = invokeRunner({
      recipePath: scenarioPath("cancellation"),
      task: "cancel",
      cwd,
      stage: "implement",
      round: 1,
      expectedHeadSha: headSha,
    }, controller.signal);
    await new Promise((resolve) => setTimeout(resolve, 50));
    controller.abort();
    await expect(run).rejects.toBeInstanceOf(RunnerCancelledError);
  });

  it("awaits adapter stop and removes its runtime root on process cancellation", async () => {
    const cwd = `${fixtureRoot.pathname}runs/adapter-process-cancel`;
    const headSha = await gitInit(cwd);
    const runtimeRoot = `${cwd}/.adapter-runtime`;
    const previousRunner = process.env.OMP_RECIPE_RUNNER;
    const previousModule = process.env.OMP_RECIPE_SHARED_RUNNER_MODULE;
    process.env.OMP_RECIPE_RUNNER = new URL("../scripts/recipe-runner", import.meta.url).pathname;
    process.env.OMP_RECIPE_SHARED_RUNNER_MODULE = new URL(
      "../fixtures/cancellation-recipe-task.ts",
      import.meta.url,
    ).href;
    try {
      const controller = new AbortController();
      const run = invokeRunner({
        recipePath: "/unused/compiled-recipe",
        task: "cancel adapter process",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: headSha,
      }, controller.signal);
      for (let attempt = 0; attempt < 100; attempt += 1) {
        try {
          await access(runtimeRoot);
          break;
        } catch {
          await delay(20);
        }
      }
      await expect(access(runtimeRoot)).resolves.toBeUndefined();
      controller.abort();
      await expect(run).rejects.toBeInstanceOf(RunnerCancelledError);
      await expect(access(runtimeRoot)).rejects.toMatchObject({ code: "ENOENT" });
    } finally {
      if (previousRunner === undefined) delete process.env.OMP_RECIPE_RUNNER;
      else process.env.OMP_RECIPE_RUNNER = previousRunner;
      if (previousModule === undefined) delete process.env.OMP_RECIPE_SHARED_RUNNER_MODULE;
      else process.env.OMP_RECIPE_SHARED_RUNNER_MODULE = previousModule;
    }
  });

  it("SIGTERM to a real held adapter still reclaims its runtime root and receipt via the parent", async () => {
    const runId = randomUUID();
    const cwd = `${fixtureRoot.pathname}runs/sigterm-reclaim-${runId}`;
    const bundleDir = `${cwd}-bundle`;
    await rm(cwd, { recursive: true, force: true });
    await mkdir(cwd, { recursive: true, mode: 0o700 });
    const ompSourceRoot = "/Users/phaedrus/Development/oh-my-pi";
    compileFixtureBundle(
      new URL("../../tests/fixtures/recipe-task/alpha/recipe.json", import.meta.url).pathname,
      bundleDir,
    );
    const previousEnv = {
      runner: process.env.OMP_RECIPE_RUNNER,
      module: process.env.OMP_RECIPE_SHARED_RUNNER_MODULE,
      rpc: process.env.OMP_RECIPE_RPC_CLIENT_MODULE,
      cli: process.env.OMP_RECIPE_CLI_PATH,
      compiler: process.env.OMP_RECIPE_COMPILER,
      ompSource: process.env.OMP_RECIPE_OMP_SOURCE,
    };
    process.env.OMP_RECIPE_RUNNER = new URL("../scripts/recipe-runner", import.meta.url).pathname;
    delete process.env.OMP_RECIPE_SHARED_RUNNER_MODULE; // exercise the real shared runner, not a fixture double
    process.env.OMP_RECIPE_RPC_CLIENT_MODULE = join(ompSourceRoot, "packages/coding-agent/src/modes/rpc/rpc-client.ts");
    process.env.OMP_RECIPE_CLI_PATH = new URL("../../tests/fixtures/recipe-task/fake-rpc-cli.ts", import.meta.url).pathname;
    process.env.OMP_RECIPE_COMPILER = new URL("../../bin/omp_recipe.py", import.meta.url).pathname;
    process.env.OMP_RECIPE_OMP_SOURCE = ompSourceRoot;
    try {
      const tmpBefore = new Set(await readdir(tmpdir()));
      const run = invokeRunner({
        recipePath: bundleDir,
        task: `HOLD sigterm-reclaim-${runId}`,
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: "a".repeat(40),
      }, new AbortController().signal);
      // invokeRunner's own outcome for an externally-killed child is not
      // this test's concern (that is what the abort-driven tests above
      // already cover) — only that it settles without an unhandled rejection.
      run.catch(() => {});

      let runtimeRoot: string | undefined;
      for (let attempt = 0; attempt < 200 && !runtimeRoot; attempt += 1) {
        const found = (await readdir(tmpdir())).find(
          entry => entry.startsWith("omp-recipe-task-") && !tmpBefore.has(entry),
        );
        if (found) runtimeRoot = join(tmpdir(), found);
        else await delay(25);
      }
      if (!runtimeRoot) throw new Error("adapter never created a runtime root");
      // Let onPrepared's receipt write and the real RpcClient spawn/hold the
      // fake CLI settle before killing — this is well past prepare, mid-flight.
      await delay(300);

      const adapterPid = findPidByCommandSubstring(bundleDir);
      if (adapterPid === undefined) throw new Error("could not find the real adapter process by its --recipe path");
      process.kill(adapterPid, "SIGTERM");

      const killDeadline = Date.now() + 8_000;
      while (Date.now() < killDeadline && pidIsAlive(adapterPid)) await delay(50);
      if (pidIsAlive(adapterPid)) {
        // Safety net only — SIGTERM ignoring outright would be a distinct bug
        // from the one this test targets. Keeps the suite from ever hanging.
        process.kill(adapterPid, "SIGKILL");
        for (let attempt = 0; attempt < 100 && pidIsAlive(adapterPid); attempt += 1) await delay(25);
      }
      expect(pidIsAlive(adapterPid)).toBe(false);

      // Give invokeRunner's child 'close' handler + finally-driven reclaim a
      // moment to run once the OS has actually reaped the process.
      for (let attempt = 0; attempt < 200; attempt += 1) {
        try {
          await access(runtimeRoot);
          await delay(25);
        } catch {
          break;
        }
      }
      await expect(access(runtimeRoot)).rejects.toMatchObject({ code: "ENOENT" });

      // No leftover receipt from THIS test either. This machine's /tmp is
      // shared with other concurrent agent sessions that also exercise the
      // real shared runner, so a bare "no new omp-recipe-receipt-* filename"
      // check is contaminated by their unrelated, legitimately-in-flight
      // receipts. Identify OUR OWN leftover precisely instead: a receipt
      // whose content is exactly this test's runtimeRoot. Any candidate
      // that vanishes while we check it (already reclaimed, by us or
      // whoever else raced it) or whose content differs is not ours.
      const candidateReceipts = (await readdir(tmpdir())).filter(
        name => name.startsWith("omp-recipe-receipt-") && !tmpBefore.has(name),
      );
      const ownLeftoverReceipts: string[] = [];
      for (const name of candidateReceipts) {
        try {
          const content = (await readFile(join(tmpdir(), name), "utf8")).trim();
          if (content === runtimeRoot) ownLeftoverReceipts.push(name);
        } catch {
          // Removed between listing and reading — not a leftover.
        }
      }
      expect(ownLeftoverReceipts).toEqual([]);
    } finally {
      if (previousEnv.runner === undefined) delete process.env.OMP_RECIPE_RUNNER;
      else process.env.OMP_RECIPE_RUNNER = previousEnv.runner;
      if (previousEnv.module === undefined) delete process.env.OMP_RECIPE_SHARED_RUNNER_MODULE;
      else process.env.OMP_RECIPE_SHARED_RUNNER_MODULE = previousEnv.module;
      if (previousEnv.rpc === undefined) delete process.env.OMP_RECIPE_RPC_CLIENT_MODULE;
      else process.env.OMP_RECIPE_RPC_CLIENT_MODULE = previousEnv.rpc;
      if (previousEnv.cli === undefined) delete process.env.OMP_RECIPE_CLI_PATH;
      else process.env.OMP_RECIPE_CLI_PATH = previousEnv.cli;
      if (previousEnv.compiler === undefined) delete process.env.OMP_RECIPE_COMPILER;
      else process.env.OMP_RECIPE_COMPILER = previousEnv.compiler;
      if (previousEnv.ompSource === undefined) delete process.env.OMP_RECIPE_OMP_SOURCE;
      else process.env.OMP_RECIPE_OMP_SOURCE = previousEnv.ompSource;
      await rm(cwd, { recursive: true, force: true });
      await rm(bundleDir, { recursive: true, force: true });
    }
  }, 20_000);

  it("treats schema-invalid typed terminal arguments as transient and retries to recovery", async () => {
    const singleAttemptCwd = `${fixtureRoot.pathname}runs/adapter-malformed-terminal-single`;
    const retryCwd = `${fixtureRoot.pathname}runs/adapter-malformed-terminal-retry`;
    const singleHeadSha = await gitInit(singleAttemptCwd);
    const retryHeadSha = await gitInit(retryCwd);
    const previousRunner = process.env.OMP_RECIPE_RUNNER;
    const previousModule = process.env.OMP_RECIPE_SHARED_RUNNER_MODULE;
    process.env.OMP_RECIPE_RUNNER = new URL("../scripts/recipe-runner", import.meta.url).pathname;
    process.env.OMP_RECIPE_SHARED_RUNNER_MODULE = new URL(
      "../fixtures/malformed-terminal-recipe-task.ts",
      import.meta.url,
    ).href;
    try {
      await expect(invokeRunner({
        recipePath: "/unused/compiled-recipe",
        task: "first attempt has schema-invalid terminal arguments",
        cwd: singleAttemptCwd,
        stage: "adversarial_review",
        round: 1,
        expectedHeadSha: singleHeadSha,
      }, new AbortController().signal)).rejects.toBeInstanceOf(TransientRunnerError);

      const attempt = await invokeRunnerWithRetry({
        recipePath: "/unused/compiled-recipe",
        task: "invalid terminal arguments on attempt one, valid on attempt two",
        cwd: retryCwd,
        stage: "adversarial_review",
        round: 1,
        expectedHeadSha: retryHeadSha,
      }, new AbortController().signal, defaultSleeper);
      expect(attempt.attempts).toBe(2);
      expect(attempt.terminal.headSha).toBe("a".repeat(40));
    } finally {
      if (previousRunner === undefined) delete process.env.OMP_RECIPE_RUNNER;
      else process.env.OMP_RECIPE_RUNNER = previousRunner;
      if (previousModule === undefined) delete process.env.OMP_RECIPE_SHARED_RUNNER_MODULE;
      else process.env.OMP_RECIPE_SHARED_RUNNER_MODULE = previousModule;
    }
  });
});
