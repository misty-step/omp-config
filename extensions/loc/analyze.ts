#!/usr/bin/env bun
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { basename, extname, join } from "node:path";

export interface LanguageStats {
	files: number;
	total: number;
	code: number;
	comment: number;
	blank: number;
}

export interface LocStats {
	files: number;
	total: number;
	code: number;
	comment: number;
	blank: number;
	byLanguage: Record<string, LanguageStats>;
	source: "scc" | "tokei" | "builtin";
}

export interface CommitDelta {
	hash: string;
	subject: string;
	date: string;
	added: number;
	deleted: number;
	net: number;
}

export interface TrendPoint {
	label: string;
	ref: string;
	code: number;
	total: number;
	files: number;
	deltaCode?: number;
}

const EXT_TO_LANG: Record<string, string> = {
	".ts": "TypeScript", ".tsx": "TypeScript", ".mts": "TypeScript", ".cts": "TypeScript",
	".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
	".py": "Python", ".pyw": "Python", ".go": "Go", ".rs": "Rust", ".java": "Java",
	".kt": "Kotlin", ".kts": "Kotlin", ".c": "C", ".h": "C", ".cc": "C++", ".cpp": "C++",
	".cxx": "C++", ".hpp": "C++", ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
	".scala": "Scala", ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".fish": "Shell",
	".ps1": "PowerShell", ".sql": "SQL", ".md": "Markdown", ".markdown": "Markdown",
	".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML", ".xml": "XML",
	".html": "HTML", ".htm": "HTML", ".css": "CSS", ".scss": "SCSS", ".sass": "Sass",
	".less": "Less", ".vue": "Vue", ".svelte": "Svelte", ".lua": "Lua", ".r": "R", ".R": "R",
	".dart": "Dart", ".zig": "Zig", ".ex": "Elixir", ".exs": "Elixir", ".erl": "Erlang",
	".hs": "Haskell", ".ml": "OCaml", ".mli": "OCaml", ".clj": "Clojure", ".cljs": "Clojure",
	".tf": "Terraform", ".hcl": "HCL", ".dockerfile": "Dockerfile",
};

const BINARY_EXTENSIONS = new Set([
	".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".svg",
	".woff", ".woff2", ".ttf", ".eot", ".otf", ".pdf", ".zip", ".gz", ".bz2", ".xz", ".7z",
	".tar", ".rar", ".exe", ".dll", ".so", ".dylib", ".a", ".o", ".class", ".jar", ".wasm",
	".mp3", ".mp4", ".avi", ".mov", ".webm", ".lock", ".min.js", ".min.css", ".map",
]);

const SKIP_DIR_PARTS = new Set([
	"node_modules", ".git", "dist", "build", "coverage", ".next", ".nuxt", "vendor",
	"__pycache__", ".venv", "venv", ".tox", "target",
]);

function run(cmd: string, args: string[], cwd: string) {
	const result = spawnSync(cmd, args, { cwd, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
	return { ok: result.status === 0, stdout: result.stdout ?? "", stderr: result.stderr ?? "" };
}

function gitRoot(cwd: string): string | null {
	const result = run("git", ["rev-parse", "--show-toplevel"], cwd);
	return result.ok ? result.stdout.trim() || null : null;
}

function trackedFiles(cwd: string, ref = "HEAD"): string[] {
	const result = run("git", ["ls-tree", "-r", "--name-only", ref], cwd);
	if (!result.ok) return [];
	return result.stdout.split("\n").map((line) => line.trim()).filter(Boolean).filter((file) => !shouldSkipPath(file));
}

function shouldSkipPath(file: string): boolean {
	for (const part of file.split(/[/\\]/)) if (SKIP_DIR_PARTS.has(part)) return true;
	return BINARY_EXTENSIONS.has(extname(file).toLowerCase());
}

function languageForFile(file: string): string {
	const base = basename(file).toLowerCase();
	if (base === "dockerfile") return "Dockerfile";
	if (base === "makefile") return "Makefile";
	const ext = extname(file).toLowerCase();
	return EXT_TO_LANG[ext] ?? (ext ? ext.slice(1).toUpperCase() : "Other");
}

function emptyStats(): LocStats {
	return { files: 0, total: 0, code: 0, comment: 0, blank: 0, byLanguage: {}, source: "builtin" };
}

function addLanguage(stats: LocStats, language: string, fileStats: Omit<LanguageStats, "files"> & { files?: number }) {
	const bucket = stats.byLanguage[language] ?? { files: 0, total: 0, code: 0, comment: 0, blank: 0 };
	bucket.files += fileStats.files ?? 1;
	bucket.total += fileStats.total;
	bucket.code += fileStats.code;
	bucket.comment += fileStats.comment;
	bucket.blank += fileStats.blank;
	stats.byLanguage[language] = bucket;
	stats.files += fileStats.files ?? 1;
	stats.total += fileStats.total;
	stats.code += fileStats.code;
	stats.comment += fileStats.comment;
	stats.blank += fileStats.blank;
}

function parseScc(stdout: string): LocStats | null {
	try {
		const rows = JSON.parse(stdout) as Array<{ Name?: string; Count?: number; Blanks?: number; Code?: number; Comment?: number }>;
		if (!Array.isArray(rows)) return null;
		const stats = emptyStats();
		stats.source = "scc";
		for (const row of rows) {
			const language = row.Name?.trim();
			if (!language || language === "Total") continue;
			const files = Number(row.Count ?? 0);
			const blank = Number(row.Blanks ?? 0);
			const code = Number(row.Code ?? 0);
			const comment = Number(row.Comment ?? 0);
			addLanguage(stats, language, { files, total: code + comment + blank, code, comment, blank });
		}
		return stats.files > 0 ? stats : null;
	} catch { return null; }
}

function parseTokei(stdout: string): LocStats | null {
	try {
		const parsed = JSON.parse(stdout) as Record<string, Record<string, { blanks?: number; code?: number; comments?: number }>>;
		if (!parsed || typeof parsed !== "object") return null;
		const stats = emptyStats();
		stats.source = "tokei";
		for (const [language, reports] of Object.entries(parsed)) {
			if (language === "Total") continue;
			let files = 0, blank = 0, code = 0, comment = 0;
			for (const report of Object.values(reports)) {
				files += 1;
				blank += Number(report.blanks ?? 0);
				code += Number(report.code ?? 0);
				comment += Number(report.comments ?? 0);
			}
			if (!files) continue;
			addLanguage(stats, language, { files, total: code + comment + blank, code, comment, blank });
		}
		return stats.files > 0 ? stats : null;
	} catch { return null; }
}

function countFileLines(content: string, language: string): Omit<LanguageStats, "files"> {
	const lines = content.split(/\r?\n/);
	let code = 0, comment = 0, blank = 0;
	const block = new Set(["C", "C++", "Java", "JavaScript", "TypeScript", "Go", "Rust", "CSS", "SQL"]);
	const hash = new Set(["Python", "Shell", "Ruby", "YAML", "TOML", "Dockerfile", "R", "Terraform", "HCL"]);
	let inBlock = false;
	for (const raw of lines) {
		const line = raw.trim();
		if (!line) { blank += 1; continue; }
		if (block.has(language) && inBlock) { comment += 1; if (line.includes("*/")) inBlock = false; continue; }
		if (block.has(language) && line.startsWith("/*")) { comment += 1; if (!line.endsWith("*/")) inBlock = true; continue; }
		if (block.has(language) && (line.startsWith("//") || line.startsWith("///"))) { comment += 1; continue; }
		if (hash.has(language) && line.startsWith("#")) { comment += 1; continue; }
		if (language === "HTML" && line.startsWith("<!--")) { comment += 1; continue; }
		if (language === "SQL" && line.startsWith("--")) { comment += 1; continue; }
		code += 1;
	}
	return { total: code + comment + blank, code, comment, blank };
}

function readFileAtRef(root: string, ref: string, file: string): string | null {
	const result = run("git", ["show", `${ref}:${file}`], root);
	return result.ok ? result.stdout : null;
}

export function analyzeBuiltin(cwd: string, ref = "HEAD"): LocStats {
	const root = gitRoot(cwd) ?? cwd;
	const stats = emptyStats();
	for (const file of trackedFiles(root, ref)) {
		const content = readFileAtRef(root, ref, file);
		if (content == null) continue;
		addLanguage(stats, languageForFile(file), countFileLines(content, languageForFile(file)));
	}
	return stats;
}

export function analyzeWithExternalTools(cwd: string): LocStats | null {
	const root = gitRoot(cwd) ?? cwd;
	if (run("git", ["rev-parse", "--is-inside-work-tree"], root).stdout.trim() !== "true") return null;
	const scc = run("scc", ["-f", "json", "--exclude-dir", "node_modules", "--exclude-dir", ".git"], root);
	if (scc.ok) { const parsed = parseScc(scc.stdout); if (parsed) return parsed; }
	const tokei = run("tokei", ["-o", "json"], root);
	if (tokei.ok) { const parsed = parseTokei(tokei.stdout); if (parsed) return parsed; }
	return null;
}

export function analyzeRepo(cwd: string, options: { ref?: string; preferExternal?: boolean } = {}): LocStats {
	if (options.preferExternal !== false) {
		const external = analyzeWithExternalTools(cwd);
		if (external) return external;
	}
	return analyzeBuiltin(cwd, options.ref ?? "HEAD");
}

export function getCommitDeltas(cwd: string, count = 8): CommitDelta[] {
	const root = gitRoot(cwd) ?? cwd;
	const result = run("git", ["log", `-n${count}`, "--pretty=format:@@@%H%x09%ad%x09%s", "--date=short", "--numstat"], root);
	if (!result.ok) return [];
	const deltas: CommitDelta[] = [];
	let current: CommitDelta | null = null;
	for (const line of result.stdout.split("\n")) {
		if (line.startsWith("@@@")) {
			if (current) deltas.push(current);
			const [hash, date, ...subjectParts] = line.slice(3).split("\t");
			current = { hash: hash.slice(0, 8), date: date ?? "", subject: subjectParts.join("\t"), added: 0, deleted: 0, net: 0 };
			continue;
		}
		if (!current || !line.trim()) continue;
		const [added, deleted] = line.split("\t");
		if (added === "-" || deleted === "-") continue;
		current.added += Number(added) || 0;
		current.deleted += Number(deleted) || 0;
		current.net = current.added - current.deleted;
	}
	if (current) deltas.push(current);
	return deltas;
}

function listTrendRefs(root: string, count: number) {
	const tags = run("git", ["tag", "--sort=-creatordate"], root);
	const tagList = tags.ok ? tags.stdout.split("\n").map((l) => l.trim()).filter(Boolean).slice(0, count) : [];
	if (tagList.length >= Math.min(3, count)) return tagList.map((tag) => ({ label: tag, ref: tag }));
	const commits = run("git", ["log", "--pretty=format:%h %s", `-n${count}`], root);
	if (!commits.ok) return [];
	return commits.stdout.split("\n").map((l) => l.trim()).filter(Boolean).map((line) => {
		const space = line.indexOf(" ");
		const hash = space === -1 ? line : line.slice(0, space);
		const subject = space === -1 ? hash : line.slice(space + 1);
		return { label: `${hash} ${subject}`.slice(0, 48), ref: hash };
	});
}

export function getTrendPoints(cwd: string, count = 6): TrendPoint[] {
	const root = gitRoot(cwd) ?? cwd;
	const points: TrendPoint[] = [];
	let previousCode: number | undefined;
	for (const entry of listTrendRefs(root, count).reverse()) {
		const stats = analyzeBuiltin(root, entry.ref);
		const point: TrendPoint = { label: entry.label, ref: entry.ref, code: stats.code, total: stats.total, files: stats.files };
		if (previousCode !== undefined) point.deltaCode = point.code - previousCode;
		previousCode = point.code;
		points.push(point);
	}
	return points;
}

export function readLocCache(cwd: string): (LocStats & { updatedAt?: number }) | null {
	const cachePath = join(gitRoot(cwd) ?? cwd, ".git", "loc_cache");
	if (!existsSync(cachePath)) return null;
	try {
		const parsed = JSON.parse(readFileSync(cachePath, "utf8")) as LocStats & { updatedAt?: number };
		return typeof parsed.code === "number" ? parsed : null;
	} catch { return null; }
}

export function topLanguages(stats: LocStats, limit = 8) {
	return Object.entries(stats.byLanguage).sort((a, b) => b[1].code - a[1].code || b[1].files - a[1].files).slice(0, limit);
}

function pad(value: string, width: number) { return value.length >= width ? value.slice(0, width) : value.padEnd(width); }
function formatNumber(value: number) { return value.toLocaleString("en-US"); }

export function formatLocReport(stats: LocStats, deltas: CommitDelta[]): string {
	const lines = [
		"Lines of code", `Source: ${stats.source}`, "",
		`Files     ${formatNumber(stats.files)}`, `Total     ${formatNumber(stats.total)}`,
		`Code      ${formatNumber(stats.code)}`, `Comment   ${formatNumber(stats.comment)}`,
		`Blank     ${formatNumber(stats.blank)}`, "", "Top languages (files / code lines)",
	];
	for (const [language, bucket] of topLanguages(stats)) {
		lines.push(`  ${pad(language, 14)} ${pad(formatNumber(bucket.files), 6)}  ${formatNumber(bucket.code)}`);
	}
	if (deltas.length) {
		lines.push("", "Recent commit deltas (added / deleted / net)");
		for (const delta of deltas) {
			const sign = delta.net >= 0 ? "+" : "";
			lines.push(`  ${delta.hash}  ${pad(delta.date, 10)}  +${formatNumber(delta.added)} / -${formatNumber(delta.deleted)} / ${sign}${formatNumber(delta.net)}  ${delta.subject}`);
		}
	}
	return lines.join("\n");
}

export function formatTrendReport(points: TrendPoint[]): string {
	if (!points.length) return "No git tags or commits available for trend analysis.";
	const maxCode = Math.max(...points.map((p) => p.code), 1);
	const lines = ["LOC trend (code lines)", "", `${pad("ref", 20)} ${pad("code", 8)} ${pad("Δ code", 8)} chart`, `${"-".repeat(20)} ${"-".repeat(8)} ${"-".repeat(8)} ${"-".repeat(24)}`];
	for (const point of points) {
		const bar = "█".repeat(Math.max(1, Math.round((point.code / maxCode) * 20)));
		const delta = point.deltaCode == null ? "—" : `${point.deltaCode >= 0 ? "+" : ""}${formatNumber(point.deltaCode)}`;
		lines.push(`${pad(point.label, 20)} ${pad(formatNumber(point.code), 8)} ${pad(delta, 8)} ${bar}`);
	}
	return lines.join("\n");
}


function parseCliArgs(argv: string[]) {
	let command: "loc" | "trend" | "json" = "loc";
	let cwd = process.cwd();
	let count = 8;
	for (let i = 0; i < argv.length; i += 1) {
		const arg = argv[i];
		if (arg === "trend" || arg === "--trend") command = "trend";
		else if (arg === "--json") command = "json";
		else if (arg === "--cwd" && argv[i + 1]) { cwd = argv[++i]; }
		else if (arg === "--count" && argv[i + 1]) count = Number(argv[++i]) || count;
	}
	return { command, cwd, count };
}

export function runCli(argv = process.argv.slice(2)): number {
	const { command, cwd, count } = parseCliArgs(argv);
	try {
		if (command === "trend") { console.log(formatTrendReport(getTrendPoints(cwd, count))); return 0; }
		const stats = analyzeRepo(cwd);
		if (command === "json") { console.log(JSON.stringify({ ...stats, updatedAt: Math.floor(Date.now() / 1000) })); return 0; }
		console.log(formatLocReport(stats, getCommitDeltas(cwd, count)));
		return 0;
	} catch (error) {
		console.error(error instanceof Error ? error.message : String(error));
		return 1;
	}
}

if (import.meta.main) process.exit(runCli());
