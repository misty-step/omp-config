import { once } from "node:events";
import { describe, expect, it } from "vitest";
import { extractTerminalObject, parseAdapterInput, runRecipeAdapter } from "../src/recipe-runner-adapter.js";

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

  it("extracts one strict terminal object from final assistant text", () => {
    expect(extractTerminalObject(`Final evidence:\n\`\`\`json\n${JSON.stringify(terminal)}\n\`\`\``)).toEqual(terminal);
    expect(() => extractTerminalObject(`${JSON.stringify(terminal)}\n${JSON.stringify(terminal)}`)).toThrow(/exactly one/);
    expect(() => extractTerminalObject(JSON.stringify({ ...terminal, unexpected: true }))).toThrow(/runnerTerminalSchema/);
  });

  it("invokes startRecipeTask directly without a progress callback and stops the handle", async () => {
    let stopped = false;
    let observedOptions: Record<string, unknown> | undefined;
    const result = await runRecipeAdapter(argv, new AbortController().signal, async (options) => {
      observedOptions = options;
      return {
        async wait() { return { text: JSON.stringify(terminal) }; },
        async stop() { stopped = true; },
      };
    });
    expect(result).toEqual(terminal);
    expect(observedOptions).toEqual({
      recipe: "/compiled/implement",
      task: "fix the card",
      cwd: "/worktree",
      signal: expect.any(AbortSignal),
    });
    expect(stopped).toBe(true);
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
