import { describe, expect, test } from "bun:test";
import recipeTaskExtension from "../global/extensions/recipe-task.ts";

describe("recipe_task extension entrypoint", () => {
	test("registers one essential recipe_task tool and never shadows task", () => {
		let registered: Record<string, unknown> | undefined;
		const stringSchema = {
			min() {
				return this;
			},
			describe() {
				return this;
			},
		};
		recipeTaskExtension({
			zod: {
				z: {
					string: () => stringSchema,
					object: (shape: Record<string, unknown>) => shape,
				},
			},
			registerTool(tool: Record<string, unknown>) {
				registered = tool;
			},
		} as never);

		expect(registered?.name).toBe("recipe_task");
		expect(registered?.name).not.toBe("task");
		expect(registered?.loadMode).toBe("essential");
		expect((registered?.execute as Function).length).toBe(5);
	});
});
