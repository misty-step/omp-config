import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";
import { OPTMEM_ENTRY_BYTES, OptMemRuntime, type OptMemAction } from "../lib/optmem-runtime.ts";


export default function (pi: ExtensionAPI): void {
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
	let taskChild = false;
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
			if (taskChild) {
				return {
					content: [{ type: "text" as const, text: "OptMem is unavailable in task children." }],
					isError: true,
					details: {},
				};
			}
			const result = await runtime.execute(params as OptMemAction, signal);
			return {
				content: [{ type: "text" as const, text: result.text }],
				isError: result.isError === true,
				details: {},
			};
		},
	});

	pi.on("session_start", async () => {
		const activeTools = pi.getActiveTools();
		taskChild = activeTools.includes("yield");
		if (taskChild) {
			if (activeTools.includes("optmem")) {
				await pi.setActiveTools(activeTools.filter(name => name !== "optmem"));
			}
			return;
		}
		runtime.reset();
		await runtime.start();
	});

	pi.on("before_agent_start", async event => {
		if (taskChild) return;
		await runtime.start();
		const material = runtime.wakePrompt();
		if (!material) return;
		return { systemPrompt: [...event.systemPrompt, material] };
	});

	pi.on("tool_call", async event => {
		if (taskChild) return;
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
