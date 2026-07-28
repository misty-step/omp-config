import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";
import { OPTMEM_ENTRY_BYTES, OptMemRuntime, type OptMemAction } from "../lib/optmem-runtime.ts";

const CHILD_BOUNDARY = "You are a subagent. Don't run memo.";

function isTaskChild(pi: Pick<ExtensionAPI, "getActiveTools">): boolean {
	return pi.getActiveTools().includes("yield") || process.env.PI_SUBAGENT_CHILD === "1";
}


export default function (pi: ExtensionAPI): void {
	// Native OMP task sessions carry the task-only `yield` contract. They do not
	// register this extension, invoke memo, or touch the shared store.
	if (isTaskChild(pi)) return;

	const { z } = pi.zod;
	const memoText = z
		.string()
		.min(1)
		.max(OPTMEM_ENTRY_BYTES)
		.refine(
			(value) => Buffer.byteLength(value, "utf8") <= OPTMEM_ENTRY_BYTES,
			`OptMem entries must be at most ${OPTMEM_ENTRY_BYTES} UTF-8 bytes`,
		);
	const runtime = new OptMemRuntime();
	const parameters = z.discriminatedUnion("action", [
		z.object({ action: z.literal("note"), text: memoText }),
		z.object({ action: z.literal("recall"), regex: z.string().min(1).max(4096) }),
		z.object({ action: z.literal("zoom"), range: z.string().regex(/^\d+-\d+$/) }),
		z.object({ action: z.literal("nap"), range: z.string().regex(/^\d+-\d+$/), summary: memoText }),
		z.object({ action: z.literal("status") }),
	]);

	pi.registerTool({
		name: "optmem",
		label: "OptMem",
		loadMode: "essential",
		approval: "write",
		description:
			"Use the one durable OptMem identity. Actions: note, recall, zoom, nap (only when required), and status. Never use this from a subagent.",
		parameters,
		async execute(_toolCallId, params, signal, _onUpdate, _ctx: ExtensionContext) {
			const result = await runtime.execute(params as OptMemAction, signal);
			return {
				content: [{ type: "text" as const, text: result.text }],
				isError: result.isError === true,
				details: {},
			};
		},
	});

	pi.on("session_start", async () => {
		runtime.reset();
		await runtime.start();
	});

	pi.on("before_agent_start", async event => {
		await runtime.start();
		const material = runtime.wakePrompt();
		if (!material) return;
		return { systemPrompt: [...event.systemPrompt, material] };
	});

	pi.on("tool_call", async event => {
		if (event.toolName === "optmem") return;
		await runtime.start();
		if (runtime.state === "ready") return;
		const reason =
			runtime.state === "nap_required"
				? `OptMem requires nap block ${runtime.pendingNap ?? "next"}; call optmem nap before ordinary tools.`
				: `OptMem is ${runtime.state}; ordinary tools are blocked until the durable memory authority is ready.`;
		return { block: true, reason };
	});
}

export { CHILD_BOUNDARY, isTaskChild };
