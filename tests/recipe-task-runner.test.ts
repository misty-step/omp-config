import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { startRecipeTask } from "../global/lib/recipe-task-runner.ts";

const ROOT = resolve(import.meta.dir, "..");
const FIXTURES = join(import.meta.dir, "fixtures/recipe-task");
const OMP_SOURCE = "/Users/phaedrus/Development/oh-my-pi";
const RPC_MODULE = join(OMP_SOURCE, "packages/coding-agent/src/modes/rpc/rpc-client.ts");
const FAKE_CLI = join(FIXTURES, "fake-rpc-cli.ts");
const COMPILER = join(ROOT, "bin/omp_recipe.py");
let scratch: string;
let alphaBundle: string;
let betaBundle: string;

function compileFixture(name: string, output: string): void {
	const source = join(FIXTURES, name, "recipe.json");
	const script = [
		"import sys",
		"from pathlib import Path",
		`sys.path.insert(0, ${JSON.stringify(join(ROOT, "bin"))})`,
		"from omp_recipe import compile_recipe",
		"compile_recipe(Path(sys.argv[1]), Path(sys.argv[2]))",
	].join(";");
	const result = Bun.spawnSync(["/usr/bin/python3", "-c", script, source, output]);
	if (result.exitCode !== 0) throw new Error(new TextDecoder().decode(result.stderr));
}

function pidIsAlive(pid: number): boolean {
	try {
		process.kill(pid, 0);
		return true;
	} catch {
		return false;
	}
}


function recipeOptions(recipe: string, task: string) {
	return {
		recipe,
		task,
		cwd: scratch,
		compilerPath: COMPILER,
		ompSourceRoot: OMP_SOURCE,
		rpcClientModule: RPC_MODULE,
		cliPath: FAKE_CLI,
		timeoutMs: 5_000,
	};
}

beforeAll(() => {
	scratch = mkdtempSync(join(tmpdir(), "recipe-task-runner-test-"));
	alphaBundle = join(scratch, "alpha-bundle");
	betaBundle = join(scratch, "beta-bundle");
	compileFixture("alpha", alphaBundle);
	compileFixture("beta", betaBundle);
});

afterAll(() => {
	rmSync(scratch, { recursive: true, force: true });
});

describe("recipe task runner", () => {
	test("uses the replacement descriptor and runs one fresh marked child", async () => {
		const prior = process.env.OMP_RECIPE_PARENT_ONLY;
		process.env.OMP_RECIPE_PARENT_ONLY = "PARENT_ONLY_SECRET_MARKER";
		const progress: string[] = [];
		let parentModel: Record<string, string> | undefined;
		try {
			const handle = await startRecipeTask({
				...recipeOptions("alpha-bundle", "report markers"),
				onEvent: event => progress.push(event.type),
				async beforeStart(descriptor) {
					parentModel = structuredClone(descriptor.model);
					mkdirSync(join(descriptor.agentDir, "agents"));
					writeFileSync(join(descriptor.agentDir, "agents", "hephaestus.md"), "hephaestus");
					writeFileSync(join(descriptor.agentDir, "agents", "cerberus.md"), "cerberus");
				},
				hostTools: [{
					name: "terminal_capture",
					label: "Terminal Capture",
					description: "Capture one typed terminal.",
					loadMode: "essential",
					parameters: { type: "object" },
					async execute() { return "accepted"; },
				}],
			});
			expect(handle.descriptor.env.OMP_RECIPE_PARENT_ONLY).toBeUndefined();
			expect(handle.descriptor.runtimeRoot).not.toBe(join(alphaBundle, "runtime"));
			const result = await handle.wait();
			expect(result.text).toContain("ALPHA_INSTRUCTION_MARKER");
			expect(result.text).toContain("skills=alpha-marker");
			expect(result.text).toContain("parent=absent");
			expect(result.text).not.toContain("PARENT_ONLY_SECRET_MARKER");
			expect(progress).toContain("message_update");
			const pid = Number(result.text.match(/^pid=(\d+)/)?.[1]);
			expect(pidIsAlive(pid)).toBeFalse();
			expect(result.text).toContain("hostTools=recipe_task,terminal_capture");
			expect(result.text).toContain("agents=cerberus,hephaestus");
			expect(result.text).toContain("ALPHA_INSTRUCTION_MARKER");
			expect(handle.descriptor.model).toEqual(parentModel);
			expect(existsSync(handle.descriptor.runtimeRoot)).toBeFalse();
			await handle.stop();
			expect(existsSync(handle.descriptor.runtimeRoot)).toBeFalse();
		} finally {
			if (prior === undefined) delete process.env.OMP_RECIPE_PARENT_ONLY;
			else process.env.OMP_RECIPE_PARENT_ONLY = prior;
		}
	});

	test("send steers an in-flight run and wait reaps it", async () => {
		const first = await startRecipeTask(recipeOptions("alpha-bundle", "HOLD for steering"));
		const second = await startRecipeTask(recipeOptions("alpha-bundle", "HOLD sibling"));
		expect(first.descriptor.runtimeRoot).not.toBe(second.descriptor.runtimeRoot);
		const firstPid = Number(readFileSync(join(first.descriptor.agentDir, "child.pid"), "utf8").trim());
		const secondPid = Number(readFileSync(join(second.descriptor.agentDir, "child.pid"), "utf8").trim());
		expect(firstPid).not.toBe(secondPid);
		await first.send("RELEASE_BY_STEER");
		const result = await first.wait();
		expect(result.text).toContain("steer=RELEASE_BY_STEER");
		await second.stop();
		expect(pidIsAlive(firstPid)).toBeFalse();
		expect(pidIsAlive(secondPid)).toBeFalse();
		expect(existsSync(first.descriptor.runtimeRoot)).toBeFalse();
		expect(existsSync(second.descriptor.runtimeRoot)).toBeFalse();
	});

	test("nested recipe_task launches a clean sibling runtime", async () => {
		const handle = await startRecipeTask(recipeOptions("alpha-bundle", "NEST beta-bundle inspect"));
		const result = await handle.wait();
		const nested = result.text.match(/nested=\[(.*)\]$/)?.[1];
		expect(nested).toBeDefined();
		expect(result.text).toContain("skills=alpha-marker");
		expect(nested).toContain("BETA_INSTRUCTION_MARKER");
		expect(nested).toContain("skills=beta-marker");
		expect(nested).not.toContain("alpha-marker");
		expect(nested).toContain("parent=absent");
		const outerPid = Number(result.text.match(/^pid=(\d+)/)?.[1]);
		const nestedPid = Number(nested?.match(/^pid=(\d+)/)?.[1]);
		const outerAgent = result.text.match(/agent=([^;]+)/)?.[1];
		const nestedAgent = nested?.match(/agent=([^;]+)/)?.[1];
		expect(outerPid).not.toBe(nestedPid);
		expect(outerAgent).not.toBe(nestedAgent);
		expect(pidIsAlive(outerPid)).toBeFalse();
		expect(pidIsAlive(nestedPid)).toBeFalse();
		expect(nested).toContain("hostTools=recipe_task");
		expect(existsSync(handle.descriptor.runtimeRoot)).toBeFalse();
		expect(existsSync(dirname(String(nestedAgent)))).toBeFalse();
	});

	test("nested recipe_task does not inherit the parent's beforeStart hook", async () => {
		let beforeStartCalls = 0;
		const handle = await startRecipeTask({
			...recipeOptions("alpha-bundle", "NEST beta-bundle inspect"),
			async beforeStart(descriptor) {
				beforeStartCalls += 1;
				mkdirSync(join(descriptor.agentDir, "agents"));
				writeFileSync(join(descriptor.agentDir, "agents", "hephaestus.md"), "hephaestus");
			},
		});
		const result = await handle.wait();
		const nested = result.text.match(/nested=\[(.*)\]$/)?.[1];
		expect(nested).toBeDefined();
		// beforeStart must fire exactly once, for the outer launch only — the
		// nested `recipe_task` tool call passes `beforeStart: undefined` for its
		// sibling runtime (global/lib/recipe-task-runner.ts's nested tool).
		expect(beforeStartCalls).toBe(1);
		expect(result.text).toContain("agents=hephaestus");
		expect(nested).toContain("agents=;");
	});

	test("onPrepared fires immediately after prepare, before RpcClient start, and is not inherited by nested recipe_task", async () => {
		let onPreparedCalls = 0;
		let capturedRuntimeRoot: string | undefined;
		let runtimeRootExistedAtCallTime = false;
		let childPidFileExistedAtCallTime = true;
		const handle = await startRecipeTask({
			...recipeOptions("alpha-bundle", "NEST beta-bundle inspect"),
			async onPrepared(descriptor) {
				onPreparedCalls += 1;
				capturedRuntimeRoot = descriptor.runtimeRoot;
				runtimeRootExistedAtCallTime = existsSync(descriptor.runtimeRoot);
				// The fake CLI writes agentDir/child.pid as its very first action
				// after RpcClient spawns it — absent here means onPrepared truly
				// ran before any RpcClient/child-process work began.
				childPidFileExistedAtCallTime = existsSync(join(descriptor.agentDir, "child.pid"));
			},
		});
		const result = await handle.wait();
		const nested = result.text.match(/nested=\[(.*)\]$/)?.[1];
		expect(nested).toBeDefined();
		// onPrepared must fire exactly once, for the outer launch only — mirrors
		// beforeStart's non-inheritance: the nested recipe_task tool call passes
		// onPrepared: undefined for its sibling runtime, so a nested launch's
		// shorter-lived runtime root can never overwrite the outer receipt.
		expect(onPreparedCalls).toBe(1);
		expect(capturedRuntimeRoot).toBe(handle.descriptor.runtimeRoot);
		expect(runtimeRootExistedAtCallTime).toBeTrue();
		expect(childPidFileExistedAtCallTime).toBeFalse();
	});

	test("OMP_RECIPE_MINT_ALIAS survives the prepare env filter into models.yml", async () => {
		// Billing evidence caught the regression this pins: a workload set the
		// variable at every hop and every run still billed the DEFAULT key,
		// because SAFE_PREPARE_ENV - the third allowlist in the chain - dropped
		// it before the compiler wrote the runtime's models.yml.
		process.env.OMP_RECIPE_MINT_ALIAS = "prepare-env-proof";
		// The alias only surfaces for openrouter models, and the shared alpha
		// fixture deliberately uses a non-network fixture provider - so this
		// test carries its own minimal bundle.
		const bundle = join(scratch, "openrouter-bundle");
		rmSync(bundle, { recursive: true, force: true });
		mkdirSync(bundle, { recursive: true });
		writeFileSync(join(bundle, "recipe.json"), JSON.stringify({
			schemaVersion: "omp.recipe.v1",
			instructions: "instructions.md",
			models: [{ provider: "openrouter", model: "z-ai/glm-5.2", reasoning: "high" }],
			skills: [],
			taskSkills: [],
			mcpServers: [],
		}));
		writeFileSync(join(bundle, "instructions.md"), "inspect and exit");
		writeFileSync(join(bundle, ".omp-recipe-owned"), "omp.recipe.v1\n");
		mkdirSync(join(bundle, "runtime"), { recursive: true });
		try {
			let modelsYml = "";
			const handle = await startRecipeTask({
				...recipeOptions(bundle, "inspect"),
				async onPrepared(descriptor) {
					modelsYml = readFileSync(join(descriptor.agentDir, "models.yml"), "utf8");
				},
			});
			await handle.wait();
			expect(modelsYml).toContain("__mint.openrouter.prepare-env-proof__");
		} finally {
			delete process.env.OMP_RECIPE_MINT_ALIAS;
		}
	});

	test("nested recipe_task stops before spawning past the depth cap", async () => {
		const auditFile = join(scratch, "fixture-processes.jsonl");
		rmSync(auditFile, { force: true });
		const handle = await startRecipeTask(recipeOptions("alpha-bundle", "DEPTH 5 alpha-bundle"));
		const result = await handle.wait();
		expect(result.text).toContain("recipe_task maximum nesting depth 4 exceeded");
		const launches = readFileSync(auditFile, "utf8")
			.trim()
			.split("\n")
			.map(line => JSON.parse(line) as { pid: number; agentDir: string });
		expect(launches).toHaveLength(5);
		expect(new Set(launches.map(launch => launch.pid)).size).toBe(5);
		expect(new Set(launches.map(launch => launch.agentDir)).size).toBe(5);
		for (const launch of launches) {
			expect(pidIsAlive(launch.pid)).toBeFalse();
			expect(existsSync(dirname(launch.agentDir))).toBeFalse();
		}
		expect(existsSync(handle.descriptor.runtimeRoot)).toBeFalse();
	});
});
