import { describe, expect, test } from "bun:test";
import { join } from "node:path";
import skillComposer, {
	composeProviderRequest,
	compositionManifest,
	readSkillCatalog,
} from "../global/extensions/skill-composer.ts";

const catalog = readSkillCatalog(join(import.meta.dir, "../global"));
const basePrompt = (agent: string): string =>
	`ROLE\n\n<!-- omp-composition-agent: ${agent} -->\n\nRUNTIME\n\n# Skills & Rules\n<skills>\n- research: ${catalog.research}\n- dispatch: ${catalog.dispatch}\n- project-engineering: ${catalog["project-engineering"]}\n- powder: ${catalog.powder}\n</skills>\n\nTOOLS`;

function request(agent: string): { systemPrompt: string[] } {
	return { systemPrompt: [basePrompt(agent)] };
}

describe("strict per-agent skill composition", () => {
	test("proves orchestrator=A+B, laneC=C only, and laneBD=B+D from real declarations", () => {
		const orchestrator = composeProviderRequest(
			request("orchestrator"),
			compositionManifest,
			catalog,
		);
		const laneC = composeProviderRequest(
			request("magellan"),
			compositionManifest,
			catalog,
		);
		const laneBD = composeProviderRequest(
			request("builder"),
			compositionManifest,
			catalog,
		);

		expect(orchestrator.changed).toBe(true);
		expect(orchestrator.payload).toEqual({
			systemPrompt: [
				expect.stringContaining(`- research: ${catalog.research}`),
			],
		});
		expect(
			(orchestrator.payload as { systemPrompt: string[] }).systemPrompt[0],
		).toContain(`- dispatch: ${catalog.dispatch}`);
		const laneCPrompt = (laneC.payload as { systemPrompt: string[] })
			.systemPrompt[0];
		expect(laneCPrompt).toContain(
			`- project-engineering: ${catalog["project-engineering"]}`,
		);
		expect(laneCPrompt).not.toContain(`- research: ${catalog.research}`);
		expect(laneCPrompt).not.toContain(`- dispatch: ${catalog.dispatch}`);
		expect(laneCPrompt).not.toContain(`- powder: ${catalog.powder}`);
		expect(
			(laneBD.payload as { systemPrompt: string[] }).systemPrompt[0],
		).toContain(`- dispatch: ${catalog.dispatch}`);
		expect(
			(laneBD.payload as { systemPrompt: string[] }).systemPrompt[0],
		).toContain(`- powder: ${catalog.powder}`);
		expect(
			(laneBD.payload as { systemPrompt: string[] }).systemPrompt[0],
		).not.toContain(`- research: ${catalog.research}`);
	});

	test.each([
		["unknown agent", request("not-declared"), compositionManifest],
		["absent manifest", request("orchestrator"), undefined],
		[
			"prompt-shape drift",
			{
				systemPrompt: [
					"<!-- omp-composition-agent: orchestrator -->\n<skills>drift",
				],
			},
			compositionManifest,
		],
	])(
		"preserves the request byte-for-byte for %s",
		(_label, payload, manifest) => {
			const before = JSON.stringify(payload);
			const result = composeProviderRequest(payload, manifest, catalog);
			expect(JSON.stringify(result.payload)).toBe(before);
			expect(result.changed).toBe(false);
			if (_label === "prompt-shape drift")
				expect(result.error).toContain("prompt-shape drift");
		},
	);

	test("measures prompt-cache impact with and without rewriting", () => {
		const original = request("orchestrator");
		const rewritten = composeProviderRequest(
			original,
			compositionManifest,
			catalog,
		);
		expect(rewritten.beforeBytes).toBe(
			Buffer.byteLength(JSON.stringify(original)),
		);
		expect(rewritten.afterBytes).toBe(
			Buffer.byteLength(JSON.stringify(rewritten.payload)),
		);
		expect(rewritten.afterBytes).toBeLessThan(rewritten.beforeBytes!);
		expect(rewritten.beforeBytes! - rewritten.afterBytes!).toBeGreaterThan(0);
	});
	test("reports drift through the live provider hook without changing bytes", () => {
		let hook: ((event: { payload: unknown }) => unknown) | undefined;
		const errors: string[] = [];
		skillComposer({
			logger: { error: (message: string) => errors.push(message) },
			on(event: string, handler: (value: { payload: unknown }) => unknown) {
				if (event === "before_provider_request") hook = handler;
			},
		} as never);
		const payload = {
			systemPrompt: [
				"<!-- omp-composition-agent: orchestrator -->\n<skills>drift",
			],
		};
		const before = JSON.stringify(payload);
		expect(hook?.({ payload })).toEqual(payload);
		expect(JSON.stringify(payload)).toBe(before);
		expect(errors[0]).toContain("skill composer: prompt-shape drift");
	});
});
