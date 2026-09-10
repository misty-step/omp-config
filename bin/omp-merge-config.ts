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
const body = live === null && !values.key
	? sourceText.endsWith("\n") ? sourceText : `${sourceText}\n`
	: `${Bun.YAML.stringify(overlay(selected, live ?? {}))}\n`;
const temporary = `${destPath}.${process.pid}.tmp`;
try {
	await writeFile(temporary, body, { mode: 0o600, flag: "wx" });
	await chmod(temporary, 0o600);
	await rename(temporary, destPath);
} finally {
	await rm(temporary, { force: true });
}
