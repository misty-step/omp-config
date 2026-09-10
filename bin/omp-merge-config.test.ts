import { afterEach, describe, expect, test } from "bun:test";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";

const cli = join(import.meta.dir, "omp-merge-config.ts");
const roots: string[] = [];

type Fixture = { source: string; dest: string };

function fixture(source: string, live?: string): Fixture {
	const root = mkdtempSync(join(tmpdir(), "omp-merge-config-test-"));
	roots.push(root);
	const files = { source: join(root, "source.yml"), dest: join(root, "live", "config.yml") };
	writeFileSync(files.source, source);
	if (live !== undefined) {
		mkdirSync(dirname(files.dest));
		writeFileSync(files.dest, live);
	}
	return files;
}

function invoke(files: Fixture, ...args: string[]) {
	return Bun.spawnSync({
		cmd: [process.execPath, cli, "--source", files.source, "--dest", files.dest, ...args],
		stdout: "pipe",
		stderr: "pipe",
	});
}

function parsed(files: Fixture): unknown {
	return Bun.YAML.parse(readFileSync(files.dest, "utf8"));
}

afterEach(() => {
	for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

describe("selected config keys", () => {
	test("overlays only the canonical leaf and preserves live mappings and sequences", () => {
		const files = fixture(
			"task:\n  maxRecursionDepth: 5\n  isolation:\n    enabled: false\nmodelRoles:\n  default: dirty/source-model\nsourceOnly: true\n",
			"task:\n  maxRecursionDepth: 1\n  isolation:\n    enabled: true\nmodelRoles:\n  default: live/model\nconstructor: foreign-constructor\n__proto__: {keep: true}\nidentifiers: ['1e3', '0x10', '+12', '0o10']\nforeign:\n  - name: keep\n    options:\n      'key: with space': true\n      nested:\n        - - one\n          - two\n  - name: also-keep\n    options: {}\n",
		);
		const result = invoke(files, "--key", "task.maxRecursionDepth");
		expect(result.stderr.toString()).toBe("");
		expect(result.exitCode).toBe(0);
		expect(parsed(files)).toEqual({
			task: { maxRecursionDepth: 5, isolation: { enabled: true } },
			modelRoles: { default: "live/model" },
			constructor: "foreign-constructor",
			["__proto__"]: { keep: true },
			identifiers: ["1e3", "0x10", "+12", "0o10"],
			foreign: [
				{ name: "keep", options: { "key: with space": true, nested: [["one", "two"]] } },
				{ name: "also-keep", options: {} },
			],
		});
	});

	test("check creates nothing and a fresh destination contains only the selected leaf", () => {
		const files = fixture("task:\n  maxRecursionDepth: 5\n  enableLsp: true\ntheme: dirty-source-theme\n");
		expect(invoke(files, "--key", "task.maxRecursionDepth", "--check").exitCode).toBe(0);
		expect(existsSync(dirname(files.dest))).toBe(false);
		expect(invoke(files, "--key", "task.maxRecursionDepth").exitCode).toBe(0);
		expect(parsed(files)).toEqual({ task: { maxRecursionDepth: 5 } });
	});

	test("rejects subtree selection rather than deploying unrelated source values", () => {
		const live = "task:\n  maxRecursionDepth: 1\n  enableLsp: false\n";
		const files = fixture("task:\n  maxRecursionDepth: 5\n  enableLsp: true\n", live);
		expect(invoke(files, "--key", "task").exitCode).not.toBe(0);
		expect(readFileSync(files.dest, "utf8")).toBe(live);
	});

	test("rejects an absent selected leaf without creating the destination", () => {
		const files = fixture("task:\n  enableLsp: true\n");
		expect(invoke(files, "--key", "task.maxRecursionDepth").exitCode).not.toBe(0);
		expect(existsSync(dirname(files.dest))).toBe(false);
	});

	test("rejects a noninteger source value without changing deployed policy", () => {
		const live = "task:\n  maxRecursionDepth: 1\n";
		const files = fixture("task:\n  maxRecursionDepth: '5'\n", live);
		expect(invoke(files, "--key", "task.maxRecursionDepth").exitCode).not.toBe(0);
		expect(readFileSync(files.dest, "utf8")).toBe(live);
	});

	test("refuses to erase an incompatible live ancestor while setting a leaf", () => {
		const live = "task:\n  - foreign-value\nother: keep\n";
		const files = fixture("task:\n  maxRecursionDepth: 5\n", live);
		expect(invoke(files, "--key", "task.maxRecursionDepth").exitCode).not.toBe(0);
		expect(readFileSync(files.dest, "utf8")).toBe(live);
	});
});

test("without selection the merger still overlays every source-owned key", () => {
	const files = fixture(
		"task:\n  maxRecursionDepth: 5\ntheme: source-theme\n",
		"task:\n  maxRecursionDepth: 1\n  enableLsp: true\ntheme: live-theme\nforeign: keep\n",
	);
	expect(invoke(files).exitCode).toBe(0);
	expect(parsed(files)).toEqual({
		task: { maxRecursionDepth: 5, enableLsp: true },
		theme: "source-theme",
		foreign: "keep",
	});
});
