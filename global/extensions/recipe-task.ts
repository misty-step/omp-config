import { resolve } from "node:path";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import {
	recipeTaskProgress,
	startRecipeTask,
	type RecipeTaskHandle,
} from "../lib/recipe-task-runner.ts";

export default function (pi: ExtensionAPI): void {
	const { z } = pi.zod;
	pi.registerTool({
		name: "recipe_task",
		label: "Recipe Task",
		loadMode: "essential",
		description: "Run a task in a fresh OMP process prepared from a compiled omp.recipe.v1 bundle.",
		parameters: z.object({
			recipe: z.string().min(1).describe("Compiled recipe path, relative to the current cwd."),
			task: z.string().min(1).describe("Task for the fresh recipe process."),
		}),
		async execute(_toolCallId, params, signal, onUpdate, ctx) {
			let handle: RecipeTaskHandle | undefined;
			let streamed = "";
			const stop = (): void => {
				if (handle) void handle.stop();
			};
			signal?.addEventListener("abort", stop, { once: true });
			try {
				handle = await startRecipeTask({
					recipe: resolve(ctx.cwd, params.recipe),
					task: params.task,
					cwd: ctx.cwd,
					signal,
					onEvent(event) {
						const progress = recipeTaskProgress(event);
						if (!progress) return;
						streamed += progress;
						onUpdate?.({ content: [{ type: "text", text: streamed }], details: {} });
					},
				});
				const result = await handle.wait();
				return {
					content: [{ type: "text", text: result.text }],
					details: {},
				};
			} finally {
				signal?.removeEventListener("abort", stop);
				if (handle) await handle.stop();
			}
		},
	});
}
