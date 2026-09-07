#!/usr/bin/env bun
import { chmod, lstat, mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { parseArgs } from "node:util";

const { values } = parseArgs({
	options: {
		source: { type: "string" },
		dest: { type: "string" },
		check: { type: "boolean", default: false },
	},
	strict: true,
});
if (!values.source || !values.dest) {
	throw new Error("--source and --dest are required");
}

const sourcePath = resolve(values.source);
const destPath = resolve(values.dest);
const YAML_BOOLISH = /^(?:true|false|null|yes|no|on|off|~)$/i;

type Yaml = null | boolean | number | string | Yaml[] | { [key: string]: Yaml };

function parseMapping(path: string, text: string): { [key: string]: Yaml } {
	const parsed = Bun.YAML.parse(text) as Yaml;
	if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
		throw new Error(`Expected a YAML mapping: ${path}`);
	}
	return parsed;
}

function overlay(source: Yaml, live: Yaml): Yaml {
	if (
		source && typeof source === "object" && !Array.isArray(source) &&
		live && typeof live === "object" && !Array.isArray(live)
	) {
		const result: { [key: string]: Yaml } = {};
		for (const key of Object.keys(source)) result[key] = overlay(source[key], live[key]);
		for (const key of Object.keys(live)) {
			if (!(key in source)) result[key] = live[key];
		}
		return result;
	}
	return source;
}

function formatString(value: string): string {
	if (
		value === "" ||
		YAML_BOOLISH.test(value) ||
		/[\n\r#{}[\],&*!|>'"`]/.test(value) ||
		/:\s/.test(value) ||
		/^[-?@`]/.test(value) ||
		/^-?[0-9]+(?:\.[0-9]+)?$/.test(value)
	) {
		return JSON.stringify(value);
	}
	if (/^[@A-Za-z0-9_./:+-]+$/.test(value)) return value;
	return JSON.stringify(value);
}


function dump(value: Yaml, indent = 0): string {
	const pad = "  ".repeat(indent);
	if (value === null) return "null";
	if (typeof value === "boolean" || typeof value === "number") return String(value);
	if (typeof value === "string") return formatString(value);
	if (Array.isArray(value)) {
		if (value.length === 0) return "[]";
		return value.map((item) => `${pad}- ${dump(item, indent + 1)}`).join("\n");
	}
	const keys = Object.keys(value);
	if (keys.length === 0) return "{}";
	return keys.map((key) => {
		const child = value[key];
		const rendered = dump(child, indent + 1);
		if (child && typeof child === "object" && !Array.isArray(child)) {
			return rendered === "{}" ? `${pad}${key}: {}` : `${pad}${key}:\n${rendered}`;
		}
		if (Array.isArray(child)) {
			return child.length === 0 ? `${pad}${key}: []` : `${pad}${key}:\n${rendered}`;
		}
		return `${pad}${key}: ${rendered}`;
	}).join("\n");
}

const sourceText = await readFile(sourcePath, "utf8");
if (!sourceText.trim()) throw new Error(`Missing or empty source: ${sourcePath}`);
const source = parseMapping(sourcePath, sourceText);

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

if (values.check) process.exit(0);

await mkdir(dirname(destPath), { recursive: true, mode: 0o700 });
const body = live === null ? sourceText.endsWith("\n") ? sourceText : `${sourceText}\n` : `${dump(overlay(source, live))}\n`;
const temporary = `${destPath}.${process.pid}.tmp`;
try {
	await writeFile(temporary, body, { mode: 0o600, flag: "wx" });
	await chmod(temporary, 0o600);
	await rename(temporary, destPath);
} finally {
	await rm(temporary, { force: true });
}
