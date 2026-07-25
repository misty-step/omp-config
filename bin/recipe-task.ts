#!/usr/bin/env bun
import { recipeTaskProgress, startRecipeTask, type RecipeTaskHandle } from "../global/lib/recipe-task-runner.ts";

async function main(argv: string[]): Promise<number> {
	const [recipe, ...taskParts] = argv;
	const task = taskParts.join(" ").trim();
	if (!recipe || !task) {
		console.error("usage: recipe-task <compiled-recipe> <task>");
		return 2;
	}

	const controller = new AbortController();
	let handle: RecipeTaskHandle | undefined;
	let streamed = false;
	const interrupt = (): void => {
		controller.abort(new Error("recipe task interrupted"));
		if (handle) void handle.stop();
	};
	process.once("SIGINT", interrupt);
	process.once("SIGTERM", interrupt);
	try {
		handle = await startRecipeTask({
			recipe,
			task,
			cwd: process.cwd(),
			signal: controller.signal,
			onEvent(event) {
				const progress = recipeTaskProgress(event);
				if (!progress) return;
				streamed = true;
				process.stdout.write(progress);
			},
		});
		const result = await handle.wait();
		if (!streamed) process.stdout.write(result.text);
		if (result.text && !result.text.endsWith("\n")) process.stdout.write("\n");
		return 0;
	} catch (error) {
		if (controller.signal.aborted) return 130;
		console.error(error instanceof Error ? error.message : String(error));
		return 1;
	} finally {
		process.off("SIGINT", interrupt);
		process.off("SIGTERM", interrupt);
		if (handle) await handle.stop();
	}
}

process.exitCode = await main(process.argv.slice(2));
