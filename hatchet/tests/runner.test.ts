import { access } from "node:fs/promises";
import { setTimeout as delay } from "node:timers/promises";
import { describe, expect, it } from "vitest";
import { invokeRunner, invokeRunnerWithRetry, runnerEnvironment } from "../src/runner.js";
import type { StageName } from "../src/contracts.js";
import { DeterministicInputError, RunnerCancelledError } from "../src/errors.js";

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
});
