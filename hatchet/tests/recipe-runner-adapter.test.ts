import { once } from "node:events";
import { lstat, mkdir, mkdtemp, readFile, realpath, rm, stat, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  parseAdapterInput,
  runRecipeAdapter,
  stageLiveTaskProjection,
  writeRuntimeReceipt,
} from "../src/recipe-runner-adapter.js";

const headSha = "a".repeat(40);
const terminal = { version: 1 as const, outcome: "completed" as const, headSha, artifactRefs: ["gate: pass"] };
const argv = [
  "--recipe", "/compiled/implement",
  "--task", "fix the card",
  "--cwd", "/worktree",
  "--stage", "implement",
  "--round", "1",
  "--head-sha", headSha,
];

const hostContext = {
  signal: new AbortController().signal,
  sendUpdate() {},
};

describe("shared-runner Hatchet adapter", () => {
  it("accepts the exact current Hatchet flags", () => {
    expect(parseAdapterInput(argv)).toEqual({
      recipe: "/compiled/implement",
      task: "fix the card",
      cwd: "/worktree",
      stage: "implement",
      round: 1,
      headSha,
    });
  });

  it("stages a copied agent catalog at the isolated HOME discovery root, not agentDir", async () => {
    const scratch = await mkdtemp(join(tmpdir(), "hatchet-live-projection-"));
    const cwd = join(scratch, "worktree");
    const agentDir = join(scratch, "agent");
    const home = join(scratch, "home");
    try {
      await mkdir(join(cwd, "global", "agents"), { recursive: true });
      await mkdir(join(cwd, "global", "skills", "deliver"), { recursive: true });
      await mkdir(join(agentDir, "skills", "ci"), { recursive: true });
      await mkdir(home, { recursive: true });
      await writeFile(join(cwd, "global", "agents", "hephaestus.md"), "hephaestus");
      await writeFile(join(cwd, "global", "agents", "cerberus.md"), "cerberus");
      await writeFile(join(cwd, "global", "skills", "deliver", "SKILL.md"), "deliver");
      await writeFile(join(agentDir, "skills", "ci", "SKILL.md"), "recipe ci");
      const preserved = new Map([
        ["AGENTS.md", "recipe instructions"],
        ["config.yml", "recipe config"],
        ["models.yml", "recipe models"],
      ]);
      for (const [name, content] of preserved) await writeFile(join(agentDir, name), content);
      const descriptor = {
        cwd,
        agentDir,
        home,
        runtimeRoot: join(scratch, "runtime"),
        model: { provider: "openrouter", id: "qwen/qwen3.7-max", reasoning: "high" },
      };
      const modelBefore = structuredClone(descriptor.model);

      await stageLiveTaskProjection(descriptor);

      // Exact discovery root: oh-my-pi task/discovery.ts resolves user-level
      // agents from `$HOME/.omp/agent/agents`, independent of
      // PI_CODING_AGENT_DIR. `descriptor.home` is the child process's HOME.
      const stagedAgentsDir = join(home, ".omp", "agent", "agents");
      expect(await readFile(join(stagedAgentsDir, "hephaestus.md"), "utf8")).toBe("hephaestus");
      expect(await readFile(join(stagedAgentsDir, "cerberus.md"), "utf8")).toBe("cerberus");

      // A real, independent copy — not a symlink into the worktree.
      expect((await lstat(stagedAgentsDir)).isSymbolicLink()).toBe(false);
      expect(await realpath(stagedAgentsDir)).not.toBe(await realpath(join(cwd, "global", "agents")));

      // The old wrong location (PI_CODING_AGENT_DIR/agents) must stay untouched.
      await expect(stat(join(agentDir, "agents"))).rejects.toThrow();

      // The deliver skill projects under PI_CODING_AGENT_DIR/skills as a copy too.
      const stagedDeliverSkill = join(agentDir, "skills", "deliver", "SKILL.md");
      expect(await readFile(stagedDeliverSkill, "utf8")).toBe("deliver");
      expect((await lstat(join(agentDir, "skills", "deliver"))).isSymbolicLink()).toBe(false);

      expect(await readFile(join(agentDir, "skills", "ci", "SKILL.md"), "utf8")).toBe("recipe ci");
      for (const [name, content] of preserved) {
        expect(await readFile(join(agentDir, name), "utf8")).toBe(content);
      }
      expect(descriptor.model).toEqual(modelBefore);
    } finally {
      await rm(scratch, { recursive: true, force: true });
    }
  });

  it("freezes the staged snapshot against source mutations after staging", async () => {
    const scratch = await mkdtemp(join(tmpdir(), "hatchet-live-projection-isolation-"));
    const cwd = join(scratch, "worktree");
    const agentDir = join(scratch, "agent");
    const home = join(scratch, "home");
    try {
      await mkdir(join(cwd, "global", "agents"), { recursive: true });
      await mkdir(join(cwd, "global", "skills", "deliver"), { recursive: true });
      await mkdir(agentDir, { recursive: true });
      await mkdir(home, { recursive: true });
      await writeFile(join(cwd, "global", "agents", "hephaestus.md"), "before staging");
      await writeFile(join(cwd, "global", "skills", "deliver", "SKILL.md"), "before staging");
      for (const name of ["AGENTS.md", "config.yml", "models.yml"]) {
        await writeFile(join(agentDir, name), "recipe fixed content");
      }
      const descriptor = {
        cwd,
        agentDir,
        home,
        runtimeRoot: join(scratch, "runtime"),
        model: { provider: "openrouter", id: "qwen/qwen3.7-max", reasoning: "high" },
      };

      await stageLiveTaskProjection(descriptor);

      // Mutate the source *after* staging — the immutable snapshot must not move.
      await writeFile(join(cwd, "global", "agents", "hephaestus.md"), "after staging");
      await writeFile(join(cwd, "global", "skills", "deliver", "SKILL.md"), "after staging");

      const stagedAgentsDir = join(home, ".omp", "agent", "agents");
      expect(await readFile(join(stagedAgentsDir, "hephaestus.md"), "utf8")).toBe("before staging");
      expect(await readFile(join(agentDir, "skills", "deliver", "SKILL.md"), "utf8")).toBe("before staging");

      // Staged files are read-only: a direct write attempt against the
      // snapshot itself must fail too, not just be masked by a later re-copy.
      await expect(writeFile(join(stagedAgentsDir, "hephaestus.md"), "tampered")).rejects.toThrow();
    } finally {
      await rm(scratch, { recursive: true, force: true });
    }
  });

  it("wires pre-start projection only for live verification", async () => {
    const liveArgv = [...argv];
    liveArgv[liveArgv.indexOf("--stage") + 1] = "live_verify";
    let beforeStart: unknown;
    const result = await runRecipeAdapter(liveArgv, new AbortController().signal, async (options) => {
      beforeStart = options.beforeStart;
      return {
        async wait() {
          await options.hostTools[0]!.execute(terminal, hostContext);
          return { text: "" };
        },
        async stop() {},
      };
    });
    expect(beforeStart).toBe(stageLiveTaskProjection);
    expect(result).toEqual(terminal);
  });

  it("writes only runtimeRoot to the receipt path when OMP_RECIPE_RUNTIME_RECEIPT is set", async () => {
    const scratch = await mkdtemp(join(tmpdir(), "hatchet-runtime-receipt-"));
    const receiptPath = join(scratch, "receipt");
    await writeFile(receiptPath, "", { mode: 0o600 });
    const previousReceiptEnv = process.env.OMP_RECIPE_RUNTIME_RECEIPT;
    process.env.OMP_RECIPE_RUNTIME_RECEIPT = receiptPath;
    try {
      let onPrepared: unknown;
      const result = await runRecipeAdapter(argv, new AbortController().signal, async (options) => {
        onPrepared = options.onPrepared;
        await options.onPrepared?.({
          cwd: "/worktree",
          agentDir: "/worktree/.agent",
          home: "/worktree/.home",
          runtimeRoot: "/tmp/omp-recipe-task-fake-uuid",
          model: { provider: "openrouter", id: "qwen/qwen3.7-max", reasoning: "high" },
        });
        return {
          async wait() {
            await options.hostTools[0]!.execute(terminal, hostContext);
            return { text: "" };
          },
          async stop() {},
        };
      });
      expect(onPrepared).toBeDefined();
      expect(await readFile(receiptPath, "utf8")).toBe("/tmp/omp-recipe-task-fake-uuid");
      expect((await stat(receiptPath)).mode & 0o777).toBe(0o600);
      expect(result).toEqual(terminal);
    } finally {
      if (previousReceiptEnv === undefined) delete process.env.OMP_RECIPE_RUNTIME_RECEIPT;
      else process.env.OMP_RECIPE_RUNTIME_RECEIPT = previousReceiptEnv;
      await rm(scratch, { recursive: true, force: true });
    }
  });

  it("writeRuntimeReceipt writes exactly the runtime root, nothing else", async () => {
    const scratch = await mkdtemp(join(tmpdir(), "hatchet-runtime-receipt-direct-"));
    const receiptPath = join(scratch, "receipt");
    try {
      await writeRuntimeReceipt(receiptPath, "/tmp/omp-recipe-task-abc");
      expect(await readFile(receiptPath, "utf8")).toBe("/tmp/omp-recipe-task-abc");
      expect((await stat(receiptPath)).mode & 0o777).toBe(0o600);
    } finally {
      await rm(scratch, { recursive: true, force: true });
    }
  });

  it("captures one validated terminal through the explicit host tool", async () => {
    let stopped = false;
    let observedOptions: Record<string, unknown> | undefined;
    const result = await runRecipeAdapter(argv, new AbortController().signal, async (options) => {
      observedOptions = options;
      return {
        async wait() {
          expect(options.hostTools).toHaveLength(1);
          expect(options.hostTools[0]?.name).toBe("hatchet_terminal");
          await options.hostTools[0]!.execute(terminal, hostContext);
          return { text: "final assistant text is not the completion channel" };
        },
        async stop() { stopped = true; },
      };
    });
    expect(result).toEqual(terminal);
    expect(observedOptions).toMatchObject({
      recipe: "/compiled/implement",
      task: "fix the card",
      cwd: "/worktree",
      signal: expect.any(AbortSignal),
      timeoutMs: 8 * 60_000,
      hostTools: expect.any(Array),
    });
    expect(observedOptions?.beforeStart).toBeUndefined();
    expect(stopped).toBe(true);
  });

  it("rejects duplicate terminal tool calls", async () => {
    const running = runRecipeAdapter(argv, new AbortController().signal, async (options) => ({
      async wait() {
        const tool = options.hostTools[0]!;
        await tool.execute(terminal, hostContext);
        await expect(tool.execute(terminal, hostContext)).rejects.toThrow(/exactly once/);
        return { text: "" };
      },
      async stop() {},
    }));
    await expect(running).rejects.toThrow(/exactly once/);
  });

  it("rejects a missing terminal tool call even when assistant text contains valid JSON", async () => {
    const running = runRecipeAdapter(argv, new AbortController().signal, async () => ({
      async wait() { return { text: JSON.stringify(terminal) }; },
      async stop() {},
    }));
    await expect(running).rejects.toThrow(/did not call hatchet_terminal/);
  });

  it("rejects invalid terminal tool arguments", async () => {
    const running = runRecipeAdapter(argv, new AbortController().signal, async (options) => ({
      async wait() {
        await expect(options.hostTools[0]!.execute(
          { ...terminal, headSha: "not-a-sha" },
          hostContext,
        )).rejects.toThrow(/runnerTerminalSchema/);
        return { text: "" };
      },
      async stop() {},
    }));
    await expect(running).rejects.toThrow(/runnerTerminalSchema/);
  });

  it("propagates cancellation and still stops the shared runner", async () => {
    const controller = new AbortController();
    let stopped = false;
    const running = runRecipeAdapter(argv, controller.signal, async (options) => ({
      async wait() {
        if (!options.signal.aborted) await once(options.signal, "abort");
        throw options.signal.reason;
      },
      async stop() { stopped = true; },
    }));
    controller.abort(new Error("cancelled"));
    await expect(running).rejects.toThrow("cancelled");
    expect(stopped).toBe(true);
  });
});
