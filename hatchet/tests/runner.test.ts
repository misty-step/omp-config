import { execFileSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { access, mkdir, readdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { describe, expect, it } from "vitest";
import { defaultSleeper, invokeRunner, invokeRunnerWithRetry, runnerEnvironment } from "../src/runner.js";
import type { CardFacts, StageName } from "../src/contracts.js";
import { DeterministicInputError, RunnerCancelledError, StageTimeoutError, TransientRunnerError } from "../src/errors.js";

const fixtureRoot = new URL("../fixtures/", import.meta.url);
const runnerPath = new URL("recipe-runner.sh", fixtureRoot).pathname;
process.env.OMP_RECIPE_RUNNER = runnerPath;

function scenarioPath(name: string): string {
  return new URL(`scenarios/${name}.sh`, fixtureRoot).pathname;
}

const testCard: CardFacts = {
  title: "Fix the flaky retry loop",
  body: "The retry loop double-counts attempts under load.",
  criteria: ["Attempts are counted exactly once", "Existing retry tests stay green"],
  priority: "P1",
};

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

  it("spawns with no HOME in its environment, and the real scripts/recipe-runner still starts the adapter under it", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-no-home`;
    const headSha = await gitInit(cwd);
    const runtimeRoot = `${cwd}/.adapter-runtime`;
    // A minimal stand-in that reports whether the child process it received
    // saw a HOME variable at all — `${HOME+x}` is bash's classic
    // set-or-unset probe, distinct from HOME being merely empty.
    const echoRunnerPath = `${cwd}-home-echo-runner.sh`;
    await writeFile(echoRunnerPath, [
      "#!/usr/bin/env bash",
      "set -eu",
      `if [ -z "\${HOME+x}" ]; then printf 'unset' > "${cwd}/.observed-home"; else printf '%s' "$HOME" > "${cwd}/.observed-home"; fi`,
      `echo '{"version":1,"outcome":"completed","headSha":"${headSha}","artifactRefs":[]}'`,
      "",
    ].join("\n"), { mode: 0o755 });

    const previousRunner = process.env.OMP_RECIPE_RUNNER;
    const previousHome = process.env.HOME;
    // A real, believable HOME in the PARENT proves the allowlist — not mere
    // absence — is what keeps it out of the child: `runnerEnvironmentKeys`
    // (PATH/TMPDIR/etc.) never included HOME, and that stays true here.
    process.env.HOME = "/tmp/should-never-cross-into-a-recipe-run";
    try {
      process.env.OMP_RECIPE_RUNNER = echoRunnerPath;
      const terminal = await invokeRunner({
        recipePath: scenarioPath("happy"),
        task: "no-home isolation",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: headSha,
        card: testCard,
      }, new AbortController().signal);
      expect(terminal.outcome).toBe("completed");
      expect(await readFile(`${cwd}/.observed-home`, "utf8")).toBe("unset");

      // The real recipe-runner-adapter chain (not this echo stand-in) still
      // resolves bun and reaches a live HOLD state under that same
      // HOME-less env — the isolation property does not break it.
      const previousModule = process.env.OMP_RECIPE_SHARED_RUNNER_MODULE;
      process.env.OMP_RECIPE_RUNNER = new URL("../scripts/recipe-runner", import.meta.url).pathname;
      process.env.OMP_RECIPE_SHARED_RUNNER_MODULE = new URL(
        "../fixtures/cancellation-recipe-task.ts",
        import.meta.url,
      ).href;
      try {
        const controller = new AbortController();
        const run = invokeRunner({
          recipePath: scenarioPath("happy"),
          task: "no-home real adapter",
          cwd,
          stage: "implement",
          round: 1,
          expectedHeadSha: headSha,
          card: testCard,
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
      } finally {
        if (previousModule === undefined) delete process.env.OMP_RECIPE_SHARED_RUNNER_MODULE;
        else process.env.OMP_RECIPE_SHARED_RUNNER_MODULE = previousModule;
      }
    } finally {
      if (previousRunner === undefined) delete process.env.OMP_RECIPE_RUNNER;
      else process.env.OMP_RECIPE_RUNNER = previousRunner;
      if (previousHome === undefined) delete process.env.HOME;
      else process.env.HOME = previousHome;
      await rm(echoRunnerPath, { force: true });
    }
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
      card: testCard,
    }, new AbortController().signal);
    expect(terminal.outcome).toBe("completed");
  });

  it("includes a bounded stderr tail and total byte count on nonzero runner exit", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-stderr-tail`;
    const headSha = await gitInit(cwd);
    const runnerScript = `${cwd}-stderr-runner.sh`;
    const stderrPayload = `${"p".repeat(2_500)}TAIL_MARKER\n`;
    await writeFile(runnerScript, [
      "#!/usr/bin/env bash",
      "set -eu",
      `printf '%s' '${stderrPayload}' >&2`,
      "exit 1",
      "",
    ].join("\n"), { mode: 0o755 });
    const previousRunner = process.env.OMP_RECIPE_RUNNER;
    process.env.OMP_RECIPE_RUNNER = runnerScript;
    try {
      let error: unknown;
      try {
        await invokeRunner({
          recipePath: scenarioPath("happy"),
          task: "stderr tail",
          cwd,
          stage: "implement",
          round: 1,
          expectedHeadSha: headSha,
          card: testCard,
        }, new AbortController().signal);
      } catch (caught) {
        error = caught;
      }
      expect(error).toBeInstanceOf(TransientRunnerError);
      const message = error instanceof Error ? error.message : String(error);
      expect(message).toContain(`stderr bytes=${Buffer.byteLength(stderrPayload)}`);
      const match = message.match(/stderr tail=(.*)$/s);
      expect(match).not.toBeNull();
      const stderrTail = JSON.parse(match![1]!) as string;
      expect(Buffer.byteLength(stderrTail)).toBe(2 * 1024);
      expect(stderrTail).toContain("TAIL_MARKER");
      expect(stderrTail).not.toBe(stderrPayload);
    } finally {
      if (previousRunner === undefined) delete process.env.OMP_RECIPE_RUNNER;
      else process.env.OMP_RECIPE_RUNNER = previousRunner;
      await rm(runnerScript, { force: true });
    }
  });

  it("treats exit 64 as deterministic non-retryable", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-det`;
    const headSha = await gitInit(cwd);
    let error: unknown;
    try {
      await invokeRunner({
        recipePath: scenarioPath("happy"),
        task: "det",
        cwd,
        stage: "unknown" as unknown as StageName,
        round: 1,
        expectedHeadSha: headSha,
        card: testCard,
      }, new AbortController().signal);
    } catch (caught) {
      error = caught;
    }
    expect(error).toBeInstanceOf(DeterministicInputError);
    const message = error instanceof Error ? error.message : String(error);
    expect(message).toContain("stderr tail=\"fixture-runner: unknown stage: unknown\\n\"");
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
      card: testCard,
    }, new AbortController().signal);
    expect(attempt.attempts).toBeGreaterThan(1);
    expect(attempt.terminal.outcome).toBe("completed");
  });

  it("treats a stage-timeout exit as terminal — exactly one attempt, unlike a transient exit that retries", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-stage-timeout`;
    const headSha = await gitInit(cwd);
    let error: unknown;
    try {
      await invokeRunnerWithRetry({
        recipePath: scenarioPath("stage-timeout"),
        task: "stage-timeout",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: headSha,
        card: testCard,
      }, new AbortController().signal);
    } catch (caught) {
      error = caught;
    }
    expect(error).toBeInstanceOf(StageTimeoutError);
    expect(error).not.toBeInstanceOf(TransientRunnerError);
    // The fixture increments this counter on every invocation — exactly one
    // spawn proves invokeRunnerWithRetry never retried the wedged stage,
    // unlike the exit-70 scenario above which keeps going until it succeeds.
    const attemptCount = await readFile(join(cwd, ".fixture-attempt-count"), "utf8");
    expect(attemptCount.trim()).toBe("1");
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
      card: testCard,
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
        recipePath: scenarioPath("happy"),
        task: "cancel adapter process",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: headSha,
        card: testCard,
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
      const originalInstructions = await readFile(join(bundleDir, "instructions.md"), "utf8");
      const tmpBefore = new Set(await readdir(tmpdir()));
      const run = invokeRunner({
        recipePath: bundleDir,
        task: `HOLD sigterm-reclaim-${runId}`,
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: "a".repeat(40),
        card: testCard,
      }, new AbortController().signal);
      // invokeRunner's own outcome for an externally-killed child is not
      // this test's concern (that is what the abort-driven tests above
      // already cover) — only that it settles without an unhandled rejection.
      run.catch(() => {});

      // invokeRunner never spawns the real adapter against `bundleDir`
      // itself — it copies the compiled bundle to a fresh per-run path
      // first (see src/runner.ts) and renders only the copy's
      // instructions.md, so the adapter process's --recipe argv names
      // that copy, not `bundleDir`.
      let bundleCopyPath: string | undefined;
      for (let attempt = 0; attempt < 200 && !bundleCopyPath; attempt += 1) {
        const found = (await readdir(tmpdir())).find(
          entry => entry.startsWith("omp-recipe-bundle-") && !tmpBefore.has(entry),
        );
        if (found) bundleCopyPath = join(tmpdir(), found);
        else await delay(25);
      }
      if (!bundleCopyPath) throw new Error("invokeRunner never created a per-run bundle copy");

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

      const adapterPid = findPidByCommandSubstring(bundleCopyPath);
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

      // The parent's per-run bundle copy is gone once the run has settled...
      await expect(access(bundleCopyPath)).rejects.toMatchObject({ code: "ENOENT" });
      // ...and the ORIGINAL compiled bundle was never mutated in place —
      // only the copy's instructions.md was ever rendered.
      expect(await readFile(join(bundleDir, "instructions.md"), "utf8")).toBe(originalInstructions);
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
        recipePath: scenarioPath("happy"),
        task: "first attempt has schema-invalid terminal arguments",
        cwd: singleAttemptCwd,
        stage: "adversarial_review",
        round: 1,
        expectedHeadSha: singleHeadSha,
        card: testCard,
      }, new AbortController().signal)).rejects.toBeInstanceOf(TransientRunnerError);

      const attempt = await invokeRunnerWithRetry({
        recipePath: scenarioPath("happy"),
        task: "invalid terminal arguments on attempt one, valid on attempt two",
        cwd: retryCwd,
        stage: "adversarial_review",
        round: 1,
        expectedHeadSha: retryHeadSha,
        card: testCard,
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

  it("renders the card into the recipe template and passes a rendered path to --recipe", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-template-render`;
    const headSha = await gitInit(cwd);
    const templatePath = `${cwd}-template.sh`;
    // Sourced by the real fixture recipe-runner.sh (see its `. "$scenario_file"`
    // step) in the same shell, so `$recipe_path`/`$cwd` are already the argv
    // values it parsed — recording `$recipe_path` here captures the exact
    // --recipe value the child process received, and copying the file proves
    // what it contained at that moment, before invokeRunner's finally block
    // deletes it.
    await writeFile(templatePath, [
      "FIXTURE_SCENARIO=happy",
      "# rendered card title: {{card.title}}",
      "printf '%s' \"$recipe_path\" > \"$cwd/.observed-recipe-path\"",
      "cp \"$recipe_path\" \"$cwd/.observed-recipe-content\"",
      "",
    ].join("\n"), "utf8");
    try {
      const terminal = await invokeRunner({
        recipePath: templatePath,
        task: "render check",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: headSha,
        card: testCard,
      }, new AbortController().signal);
      expect(terminal.outcome).toBe("completed");

      const observedRecipePath = (await readFile(`${cwd}/.observed-recipe-path`, "utf8")).trim();
      expect(observedRecipePath).not.toBe(templatePath);
      expect(observedRecipePath).toMatch(/omp-recipe-rendered-.+\.sh$/);

      const observedRecipeContent = await readFile(`${cwd}/.observed-recipe-content`, "utf8");
      expect(observedRecipeContent).toContain(`rendered card title: ${testCard.title}`);
      expect(observedRecipeContent).not.toContain("{{card.title}}");
    } finally {
      await rm(templatePath, { force: true });
    }
  });

  it("throws before spawning when the recipe template has an unknown placeholder", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-template-unknown`;
    const headSha = await gitInit(cwd);
    const templatePath = `${cwd}-template.sh`;
    await writeFile(templatePath, "{{card.unknown}}\n", "utf8");
    try {
      await expect(invokeRunner({
        recipePath: templatePath,
        task: "should not spawn",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: headSha,
        card: testCard,
      }, new AbortController().signal)).rejects.toThrow(/unknown recipe placeholder/);
    } finally {
      await rm(templatePath, { force: true });
    }
  });

  it("cleans up the rendered temp file after the run settles", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-template-cleanup`;
    const headSha = await gitInit(cwd);
    const templatePath = `${cwd}-template.sh`;
    const scenario = await readFile(scenarioPath("happy"), "utf8");
    await writeFile(templatePath, scenario, "utf8");
    // Scan a temp dir this invocation OWNS. Scanning the shared `tmpdir()` for
    // `omp-recipe-rendered-*` made every concurrently-rendering test look like a
    // leak here, so the assertion failed on unrelated work rather than on a bug.
    // `os.tmpdir()` re-reads TMPDIR per call, and tests within a file run
    // sequentially, so scoping it is safe.
    const scratch = `${cwd}-tmp`;
    await mkdir(scratch, { recursive: true, mode: 0o700 });
    const priorTmpdir = process.env.TMPDIR;
    process.env.TMPDIR = scratch;
    try {
      await invokeRunner({
        recipePath: templatePath,
        task: "cleanup check",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: headSha,
        card: testCard,
      }, new AbortController().signal);
      const leftoverRendered = (await readdir(scratch)).filter(
        (name) => name.startsWith("omp-recipe-rendered-"),
      );
      expect(leftoverRendered).toEqual([]);
    } finally {
      if (priorTmpdir === undefined) delete process.env.TMPDIR;
      else process.env.TMPDIR = priorTmpdir;
      await rm(templatePath, { force: true });
      await rm(scratch, { recursive: true, force: true });
    }
  });

  it("copies a compiled recipe bundle directory to a per-run path and renders only the copy's instructions.md", async () => {
    const cwd = `${fixtureRoot.pathname}runs/runner-bundle-render`;
    await mkdir(cwd, { recursive: true, mode: 0o700 });
    const bundleDir = `${cwd}-bundle`;
    await mkdir(join(bundleDir, "runtime"), { recursive: true, mode: 0o700 });
    await writeFile(join(bundleDir, ".omp-recipe-owned"), "omp.recipe.v1\n", "utf8");
    await writeFile(join(bundleDir, "recipe.json"), JSON.stringify({ schemaVersion: "omp.recipe.v1" }), "utf8");
    const originalInstructions = "# stage prompt\ncard title: {{card.title}}\n";
    await writeFile(join(bundleDir, "instructions.md"), originalInstructions, "utf8");
    const echoRunnerPath = `${cwd}-echo-runner.sh`;
    // A minimal stand-in for the real recipe-runner-adapter: it only proves
    // what `--recipe` argv value invokeRunner passed and what the copy it
    // names actually contains, without needing the real compiled-bundle
    // compiler/RPC-client machinery the SIGTERM test above already
    // exercises end to end for the directory case.
    await writeFile(echoRunnerPath, [
      "#!/usr/bin/env bash",
      "set -eu",
      "recipe_path=\"\"",
      "while [ \"$#\" -gt 0 ]; do",
      "  case \"$1\" in",
      "    --recipe) recipe_path=\"$2\"; shift 2 ;;",
      "    *) shift ;;",
      "  esac",
      "done",
      `printf '%s' "$recipe_path" > "${cwd}/.observed-recipe-path"`,
      `cp "$recipe_path/instructions.md" "${cwd}/.observed-instructions"`,
      `cp "$recipe_path/.omp-recipe-owned" "${cwd}/.observed-owner"`,
      "if [ -f \"$recipe_path/.omp-recipe-owned\" ] && [ ! -L \"$recipe_path/.omp-recipe-owned\" ]; then",
      `  printf 'true' > "${cwd}/.observed-owner-is-regular"`,
      "else",
      `  printf 'false' > "${cwd}/.observed-owner-is-regular"`,
      "fi",
      "if [ -f \"$recipe_path/recipe.json\" ] && [ ! -L \"$recipe_path/recipe.json\" ]; then",
      `  printf 'true' > "${cwd}/.observed-recipejson-is-regular"`,
      "else",
      `  printf 'false' > "${cwd}/.observed-recipejson-is-regular"`,
      "fi",
      "if [ -d \"$recipe_path/runtime\" ] && [ ! -L \"$recipe_path/runtime\" ]; then",
      `  printf 'true' > "${cwd}/.observed-runtime-is-dir"`,
      "else",
      `  printf 'false' > "${cwd}/.observed-runtime-is-dir"`,
      "fi",
      `echo '{"version":1,"outcome":"completed","headSha":"${"a".repeat(40)}","artifactRefs":[]}'`,
      "",
    ].join("\n"), { mode: 0o755 });
    const previousRunner = process.env.OMP_RECIPE_RUNNER;
    process.env.OMP_RECIPE_RUNNER = echoRunnerPath;
    let observedRecipePath: string | undefined;
    try {
      const terminal = await invokeRunner({
        recipePath: bundleDir,
        task: "bundle render check",
        cwd,
        stage: "implement",
        round: 1,
        expectedHeadSha: "a".repeat(40),
        card: testCard,
      }, new AbortController().signal);
      expect(terminal.outcome).toBe("completed");

      observedRecipePath = (await readFile(`${cwd}/.observed-recipe-path`, "utf8")).trim();
      expect(observedRecipePath).not.toBe(bundleDir);
      expect(observedRecipePath).toMatch(/omp-recipe-bundle-.+$/);

      const observedInstructions = await readFile(`${cwd}/.observed-instructions`, "utf8");
      expect(observedInstructions).toContain(`card title: ${testCard.title}`);
      expect(observedInstructions).not.toContain("{{card.title}}");

      expect(await readFile(`${cwd}/.observed-owner`, "utf8")).toBe("omp.recipe.v1\n");
      expect(await readFile(`${cwd}/.observed-owner-is-regular`, "utf8")).toBe("true");
      expect(await readFile(`${cwd}/.observed-recipejson-is-regular`, "utf8")).toBe("true");
      expect(await readFile(`${cwd}/.observed-runtime-is-dir`, "utf8")).toBe("true");

      // The original bundle is never mutated in place — only the per-run
      // copy's instructions.md is rendered.
      expect(await readFile(join(bundleDir, "instructions.md"), "utf8")).toBe(originalInstructions);
    } finally {
      if (previousRunner === undefined) delete process.env.OMP_RECIPE_RUNNER;
      else process.env.OMP_RECIPE_RUNNER = previousRunner;
      await rm(bundleDir, { recursive: true, force: true });
      await rm(echoRunnerPath, { force: true });
      await rm(cwd, { recursive: true, force: true });
    }
    // The per-run bundle copy is gone once invokeRunner has returned.
    if (observedRecipePath !== undefined) {
      await expect(access(observedRecipePath)).rejects.toMatchObject({ code: "ENOENT" });
    }
  });
});
