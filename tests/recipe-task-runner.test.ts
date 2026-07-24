import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
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

function fixtureLog(agentDir: string): Array<Record<string, unknown>> {
	return readFileSync(join(agentDir, "fixture-state.jsonl"), "utf8")
		.trim()
		.split("\n")
		.map(line => JSON.parse(line) as Record<string, unknown>);
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
		try {
			const handle = await startRecipeTask({
				...recipeOptions("alpha-bundle", "report markers"),
				onEvent: event => progress.push(event.type),
			});
			expect(handle.descriptor.env.OMP_RECIPE_PARENT_ONLY).toBeUndefined();
			expect(handle.descriptor.runtimeRoot).not.toBe(join(alphaBundle, "runtime"));
			const result = await handle.wait();
			expect(result.text).toContain("ALPHA_INSTRUCTION_MARKER");
			expect(result.text).toContain("skills=alpha-marker");
			expect(result.text).toContain("parent=absent");
			expect(result.text).not.toContain("PARENT_ONLY_SECRET_MARKER");
			expect(progress).toContain("message_update");
			const started = fixtureLog(handle.descriptor.agentDir).find(entry => entry.type === "started");
			const pid = Number(started?.pid);
			expect(pidIsAlive(pid)).toBeFalse();
			expect(fixtureLog(handle.descriptor.agentDir).find(entry => entry.type === "host_tools")?.tools).toEqual([
				"recipe_task",
			]);
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
		expect(fixtureLog(second.descriptor.agentDir).some(entry => entry.type === "abort")).toBeTrue();
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
		expect(fixtureLog(String(nestedAgent)).find(entry => entry.type === "host_tools")?.tools).toEqual([
			"recipe_task",
		]);
	});
});
