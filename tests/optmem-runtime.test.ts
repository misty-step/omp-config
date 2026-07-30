import { describe, expect, test } from "bun:test";
import {
	OPTMEM_COMMIT,
	OPTMEM_REPOSITORY,
	OPTMEM_SCHEMA,
	OPTMEM_SHA256,
	OPTMEM_STORE,
	OPTMEM_URL,
	OptMemRuntime,
} from "../global/lib/optmem-runtime.ts";

type SpawnOptions = { env?: Record<string, string> };

type CapturedSpawn = (command: string[], options: SpawnOptions) => unknown;

function fakeChild(output: string): unknown {
	return {
		stdout: new Response(`${output}\n`).body,
		stderr: new Response("").body,
		exited: Promise.resolve(0),
		kill() {},
	};
}

describe("OptMem subprocess contract", () => {
	test("passes only the memo launch environment", async () => {
		const originalHome = process.env.HOME;
		const originalPath = process.env.PATH;
		const originalSecret = process.env.OPTMEM_TEST_SECRET;
		process.env.HOME = "/tmp/optmem-test-home";
		process.env.PATH = "/tmp/optmem-test-path";
		process.env.OPTMEM_TEST_SECRET = "must-not-reach-memo";
		const environments: Record<string, string>[] = [];
		const spawn: CapturedSpawn = (command, options) => {
			if (!options.env) throw new Error(`missing environment for ${command.join(" ")}`);
			environments.push(options.env);
			return fakeChild(command.includes("wake") ? "You are awake." : "Saved as #1.");
		};
		const runtime = new OptMemRuntime(spawn as typeof Bun.spawn);
		runtime.verifyInstallation = async () => ({
			schema: OPTMEM_SCHEMA,
			repository: OPTMEM_REPOSITORY,
			commit: OPTMEM_COMMIT,
			url: OPTMEM_URL,
			sha256: OPTMEM_SHA256,
			installed_at: "2026-01-01T00:00:00Z",
			installer: "omp-config",
		});

		try {
			const result = await runtime.execute({ action: "note", text: "environment contract" });

			expect(result.isError).not.toBe(true);
			expect(environments).toHaveLength(3);
			for (const environment of environments) {
				expect(Object.keys(environment).sort()).toEqual(["HOME", "MEMORY_DIR", "PATH"]);
				expect(environment).toEqual({
					HOME: "/tmp/optmem-test-home",
					MEMORY_DIR: OPTMEM_STORE,
					PATH: "/tmp/optmem-test-path",
				});
				expect(environment.OPTMEM_TEST_SECRET).toBeUndefined();
			}
		} finally {
			if (originalHome === undefined) delete process.env.HOME;
			else process.env.HOME = originalHome;
			if (originalPath === undefined) delete process.env.PATH;
			else process.env.PATH = originalPath;
			if (originalSecret === undefined) delete process.env.OPTMEM_TEST_SECRET;
			else process.env.OPTMEM_TEST_SECRET = originalSecret;
		}
	});

});
