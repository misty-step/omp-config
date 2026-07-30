import { describe, expect, test } from "bun:test";
import optmemExtension from "../global/extensions/optmem.ts";

type Handler = (event: Record<string, unknown>) => Promise<unknown> | unknown;

function buildHarness(activeTools: string[]) {
	const handlers = new Map<string, Handler>();
	const state = {
		activeTools: [...activeTools],
		initialized: false,
		getActiveToolsCalls: 0,
		registeredTool: undefined as Record<string, unknown> | undefined,
	};
	const schema = {
		min() {
			return this;
		},
		max() {
			return this;
		},
		refine() {
			return this;
		},
		regex() {
			return this;
		},
	};
	const api = {
		zod: {
			z: {
				string: () => schema,
				literal: () => schema,
				object: () => schema,
				discriminatedUnion: () => schema,
			},
		},
		registerTool(tool: Record<string, unknown>) {
			state.registeredTool = tool;
		},
		on(name: string, handler: Handler) {
			handlers.set(name, handler);
		},
		getActiveTools() {
			state.getActiveToolsCalls += 1;
			if (!state.initialized) {
				throw new Error("Extension runtime not initialized. Action methods cannot be called during extension loading.");
			}
			return [...state.activeTools];
		},
		async setActiveTools(toolNames: string[]) {
			state.activeTools = [...toolNames];
		},
	};
	return { api, handlers, state };
}

describe("optmem extension lifecycle", () => {
	test("does not call runtime actions during extension loading", () => {
		const harness = buildHarness(["read", "optmem"]);

		expect(() => optmemExtension(harness.api as never)).not.toThrow();
		expect(harness.state.getActiveToolsCalls).toBe(0);
		expect(harness.state.registeredTool?.name).toBe("optmem");
		expect(harness.handlers.has("session_start")).toBe(true);
	});

	test("removes optmem and disables its hooks in task children", async () => {
		const harness = buildHarness(["read", "yield", "optmem"]);
		optmemExtension(harness.api as never);
		harness.state.initialized = true;

		await harness.handlers.get("session_start")?.({ type: "session_start" });

		expect(harness.state.activeTools).toEqual(["read", "yield"]);
		expect(harness.state.getActiveToolsCalls).toBe(1);
		expect(
			await harness.handlers.get("before_agent_start")?.({ type: "before_agent_start", systemPrompt: [] }),
		).toBeUndefined();
		expect(await harness.handlers.get("tool_call")?.({ type: "tool_call", toolName: "read" })).toBeUndefined();
	});
});
