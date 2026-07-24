import { once } from "node:events";
import { describe, expect, it } from "vitest";
import { parseAdapterInput, runRecipeAdapter } from "../src/recipe-runner-adapter.js";

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
