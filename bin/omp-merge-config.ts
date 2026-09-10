#!/usr/bin/env bun
import { chmod, lstat, mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { parseArgs } from "node:util";

const { values } = parseArgs({
	options: {
		source: { type: "string" },
		dest: { type: "string" },
		key: { type: "string", multiple: true },
		check: { type: "boolean", default: false },
	},
	strict: true,
});
if (!values.source || !values.dest) {
	throw new Error("--source and --dest are required");
}

const sourcePath = resolve(values.source);
const destPath = resolve(values.dest);

type Yaml = null | boolean | number | string | Yaml[] | { [key: string]: Yaml };

function parseMapping(path: string, text: string): { [key: string]: Yaml } {
	const parsed = Bun.YAML.parse(text) as Yaml;
	if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
		throw new Error(`Expected a YAML mapping: ${path}`);
	}
	return parsed;
}

function selectKeys(source: { [key: string]: Yaml }, keys: string[]): { [key: string]: Yaml } {
	const selected: { [key: string]: Yaml } = {};
	const seen = new Set<string>();
	for (const key of keys) {
		if (key !== "task.maxRecursionDepth") throw new Error(`Unsupported selected key: ${key}`);
		if (seen.has(key)) throw new Error(`Duplicate selected key: ${key}`);
		seen.add(key);
		const task = source.task;
		if (!task || typeof task !== "object" || Array.isArray(task) || !Object.hasOwn(task, "maxRecursionDepth")) {
			throw new Error(`Missing selected source key: ${key}`);
		}
		const depth = task.maxRecursionDepth;
		if (typeof depth !== "number" || !Number.isSafeInteger(depth)) {
			throw new Error(`Expected an integer for selected source key: ${key}`);
		}
		selected.task = { maxRecursionDepth: depth };
	}
	return selected;
}

function overlay(source: Yaml, live: Yaml): Yaml {
	if (
		source && typeof source === "object" && !Array.isArray(source) &&
		live && typeof live === "object" && !Array.isArray(live)
	) {
		const result: { [key: string]: Yaml } = Object.create(null);
		for (const key of Object.keys(source)) result[key] = overlay(source[key], live[key]);
		for (const key of Object.keys(live)) {
			if (!Object.hasOwn(source, key)) result[key] = live[key];
		}
		return result;
	}
	return source;
}

function pruneRetiredKeys(source: Yaml, merged: Yaml): void {
	// Retire only these owned leaves; other live-only config remains foreign.
	const paths = [
		["modelRoles", "designer"],
		["task", "agentModelOverrides", "designer"],
		["retry", "fallbackChains", "slow"],
		["retry", "fallbackChains", "extreme"],
		["retry", "fallbackChains", "plan"],
		["retry", "fallbackChains", "advisor"],
		["retry", "fallbackChains", "task"],
		["retry", "fallbackChains", "designer"],
		["retry", "fallbackChains", "reviewer"],
		["retry", "fallbackChains", "security-reviewer"],
	];
	for (const path of paths) {
		let sourceParent: Yaml | undefined = source;
		let mergedParent: Yaml | undefined = merged;
		for (let index = 0; index < path.length - 1; index++) {
			const key = path[index];
			sourceParent = sourceParent && typeof sourceParent === "object" && !Array.isArray(sourceParent)
				? sourceParent[key] : undefined;
			mergedParent = mergedParent && typeof mergedParent === "object" && !Array.isArray(mergedParent)
				? mergedParent[key] : undefined;
		}
		const leaf = path[path.length - 1];
		if (sourceParent && typeof sourceParent === "object" && !Array.isArray(sourceParent) &&
			Object.hasOwn(sourceParent, leaf)) continue;
		if (mergedParent && typeof mergedParent === "object" && !Array.isArray(mergedParent)) {
			delete mergedParent[leaf];
		}
	}
}


const sourceText = await readFile(sourcePath, "utf8");
if (!sourceText.trim()) throw new Error(`Missing or empty source: ${sourcePath}`);
const source = parseMapping(sourcePath, sourceText);
const selected = values.key ? selectKeys(source, values.key) : source;

let live: { [key: string]: Yaml } | null = null;
try {
	const destStat = await lstat(destPath);
	if (!destStat.isFile() || destStat.isSymbolicLink()) {
		throw new Error(`Refusing non-file or symlinked configuration: ${destPath}`);
	}
	const liveText = await readFile(destPath, "utf8");
	live = liveText.trim() ? parseMapping(destPath, liveText) : {};
} catch (error) {
	if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
}

if (values.key && live && Object.hasOwn(live, "task")) {
	const task = live.task;
	if (!task || typeof task !== "object" || Array.isArray(task)) {
		throw new Error(`Cannot select task.maxRecursionDepth through a non-mapping task value: ${destPath}`);
	}
}

if (values.check) process.exit(0);

await mkdir(dirname(destPath), { recursive: true, mode: 0o700 });
let body: string;
if (live === null && !values.key) {
	body = sourceText.endsWith("\n") ? sourceText : `${sourceText}\n`;
} else {
	const merged = overlay(selected, live ?? {});
	if (!values.key) pruneRetiredKeys(source, merged);
	body = `${Bun.YAML.stringify(merged)}\n`;
}
const temporary = `${destPath}.${process.pid}.tmp`;
try {
	await writeFile(temporary, body, { mode: 0o600, flag: "wx" });
	await chmod(temporary, 0o600);
	await rename(temporary, destPath);
} finally {
	await rm(temporary, { force: true });
}
