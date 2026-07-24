import { once } from "node:events";
import { mkdir, mkdtemp, readFile, realpath, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  parseAdapterInput,
  runRecipeAdapter,
  stageLiveTaskProjection,
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
    expect(() => parseAdapterInput([...argv, "--unknown", "value"])).toThrow(/invalid Hatchet runner arguments/);
  });

  it("stages live Task agents without changing the parent recipe composition", async () => {
    const scratch = await mkdtemp(join(tmpdir(), "hatchet-live-projection-"));
    const cwd = join(scratch, "worktree");
    const agentDir = join(scratch, "agent");
    try {
      await mkdir(join(cwd, "global", "agents"), { recursive: true });
      await mkdir(join(cwd, "global", "skills", "deliver"), { recursive: true });
      await mkdir(join(agentDir, "skills", "ci"), { recursive: true });
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
        model: { provider: "openrouter", id: "qwen/qwen3.7-max", reasoning: "high" },
      };
      const modelBefore = structuredClone(descriptor.model);

      await stageLiveTaskProjection(descriptor);

      expect(await realpath(join(agentDir, "agents"))).toBe(await realpath(join(cwd, "global", "agents")));
      expect(await realpath(join(agentDir, "skills", "deliver")))
        .toBe(await realpath(join(cwd, "global", "skills", "deliver")));
      expect(await readFile(join(agentDir, "skills", "ci", "SKILL.md"), "utf8")).toBe("recipe ci");
      for (const [name, content] of preserved) {
        expect(await readFile(join(agentDir, name), "utf8")).toBe(content);
      }
      expect(descriptor.model).toEqual(modelBefore);
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
