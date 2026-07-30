import { createHash } from "node:crypto";
import { lstatSync, readFileSync } from "node:fs";
import { lstat, readdir, readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";

interface OptMemPolicy {
	repository: string;
	source: { commit: string; url: string; sha256: string };
	schemas: { installation: string; backup: string };
	record_sizes: { log: number; tree: number };
}

function exactKeys(value: Record<string, unknown>, expected: string[]): boolean {
	const actual = Object.keys(value).sort();
	const wanted = [...expected].sort();
	return actual.length === wanted.length && actual.every((key, index) => key === wanted[index]);
}

function loadPolicy(): OptMemPolicy {
	const policyUrl = new URL("../optmem-policy.json", import.meta.url);
	const stats = lstatSync(policyUrl);
	const owner = process.getuid?.();
	if (!stats.isFile() || stats.isSymbolicLink() || (owner !== undefined && stats.uid !== owner) || (stats.mode & 0o777) !== 0o644) {
		throw new Error("OptMem policy path is not an owner-controlled 0644 regular file");
	}
	const value: unknown = JSON.parse(readFileSync(policyUrl, "utf8"));
	if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error("OptMem policy is not an object");
	const policy = value as Record<string, unknown>;
	if (!exactKeys(policy, ["repository", "source", "schemas", "record_sizes"])) throw new Error("OptMem policy schema is invalid");
	const source = policy.source;
	const schemas = policy.schemas;
	const recordSizes = policy.record_sizes;
	if (
		typeof policy.repository !== "string" ||
		source === null ||
		typeof source !== "object" ||
		Array.isArray(source) ||
		schemas === null ||
		typeof schemas !== "object" ||
		Array.isArray(schemas) ||
		recordSizes === null ||
		typeof recordSizes !== "object" ||
		Array.isArray(recordSizes)
	) {
		throw new Error("OptMem policy fields are invalid");
	}
	const sourceValue = source as Record<string, unknown>;
	const schemaValue = schemas as Record<string, unknown>;
	const sizeValue = recordSizes as Record<string, unknown>;
	if (
		!exactKeys(sourceValue, ["commit", "url", "sha256"]) ||
		!exactKeys(schemaValue, ["installation", "backup"]) ||
		!exactKeys(sizeValue, ["log", "tree"])
	) {
		throw new Error("OptMem policy nested schema is invalid");
	}
	const expectedUrl = `https://raw.githubusercontent.com/${policy.repository}/${sourceValue.commit}/memo`;
	if (
		typeof sourceValue.commit !== "string" ||
		!/^[0-9a-f]{40}$/.test(sourceValue.commit) ||
		sourceValue.url !== expectedUrl ||
		typeof sourceValue.sha256 !== "string" ||
		!/^[0-9a-f]{64}$/.test(sourceValue.sha256) ||
		typeof schemaValue.installation !== "string" ||
		!/^omp\.optmem\.installation\.v[0-9]+$/.test(schemaValue.installation) ||
		typeof schemaValue.backup !== "string" ||
		!/^omp\.optmem\.backup\.v[0-9]+$/.test(schemaValue.backup) ||
		!Number.isSafeInteger(sizeValue.log) ||
		(sizeValue.log as number) <= 0 ||
		!Number.isSafeInteger(sizeValue.tree) ||
		(sizeValue.tree as number) <= 0
	) {
		throw new Error("OptMem policy values are invalid");
	}
	return value as OptMemPolicy;
}

const OPTMEM_POLICY = loadPolicy();
export const OPTMEM_SCHEMA = OPTMEM_POLICY.schemas.installation;
export const OPTMEM_REPOSITORY = OPTMEM_POLICY.repository;
export const OPTMEM_COMMIT = OPTMEM_POLICY.source.commit;
export const OPTMEM_URL = OPTMEM_POLICY.source.url;
export const OPTMEM_SHA256 = OPTMEM_POLICY.source.sha256;

export const OPTMEM_HOME = join(homedir(), ".optmem");
export const OPTMEM_EXECUTABLE = join(OPTMEM_HOME, "memo");
export const OPTMEM_STORE = join(OPTMEM_HOME, "memory");
export const OPTMEM_RECEIPT = join(OPTMEM_HOME, "installation.json");

const MAX_COMMAND_OUTPUT_BYTES = 8 * 1024 * 1024;
const MAX_WAKE_PAGES = 4096;
const MAX_RECALL_BYTES = 4096;
const MAX_RANGE_BYTES = 64;
export const OPTMEM_ENTRY_BYTES = 280;
const MODE_MASK = 0o777;
const RESTRICTED_LAUNCH = ["/bin/sh", "-c", 'umask 077; exec "$@"', "optmem"] as const;

export type OptMemState = "cold" | "waking" | "nap_required" | "ready" | "blocked";

export type OptMemAction =
	| { action: "note"; text: string }
	| { action: "recall"; regex: string }
	| { action: "zoom"; range: string }
	| { action: "nap"; range: string; summary: string }
	| { action: "status" };

export interface OptMemReceipt {
	schema: typeof OPTMEM_SCHEMA;
	repository: typeof OPTMEM_REPOSITORY;
	commit: typeof OPTMEM_COMMIT;
	url: typeof OPTMEM_URL;
	sha256: typeof OPTMEM_SHA256;
	installed_at: string;
	installer: "omp-config";
}

export interface OptMemActionResult {
	text: string;
	isError?: boolean;
}

interface MemoRun {
	code: number;
	stdout: string;
	stderr: string;
}

type MemoSpawn = typeof Bun.spawn;

interface BlockRange {
	lo: number;
	hi: number;
}

class OptMemError extends Error {
	readonly blocked: boolean;

	constructor(message: string, blocked = false) {
		super(message);
		this.name = "OptMemError";
		this.blocked = blocked;
	}
}

function modeOf(mode: number): number {
	return mode & MODE_MASK;
}

async function checkedPath(path: string, kind: "directory" | "file", expectedMode: number) {
	let stats;
	try {
		stats = await lstat(path);
	} catch {
		throw new OptMemError(`OptMem ${kind} is missing: ${path}`, true);
	}
	const owner = process.getuid?.();
	if (stats.isSymbolicLink()) throw new OptMemError(`OptMem authority path is a symlink: ${path}`, true);
	if (owner !== undefined && stats.uid !== owner) throw new OptMemError(`OptMem path has the wrong owner: ${path}`, true);
	if (kind === "directory" && !stats.isDirectory()) throw new OptMemError(`OptMem path is not a directory: ${path}`, true);
	if (kind === "file" && !stats.isFile()) throw new OptMemError(`OptMem path is not a regular file: ${path}`, true);
	if (modeOf(stats.mode) !== expectedMode) {
		throw new OptMemError(`OptMem path has unsafe permissions: ${path}`, true);
	}
	return stats;
}

async function verifyTree(path: string): Promise<void> {
	let entries;
	try {
		entries = await readdir(path, { withFileTypes: true });
	} catch {
		throw new OptMemError(`OptMem TREE cannot be read: ${path}`, true);
	}
	for (const entry of entries) {
		const child = join(path, entry.name);
		if (entry.isSymbolicLink()) throw new OptMemError(`OptMem TREE contains a symlink: ${child}`, true);
		if (entry.isDirectory()) {
			await checkedPath(child, "directory", 0o700);
			await verifyTree(child);
			continue;
		}
		if (!entry.isFile()) throw new OptMemError(`OptMem TREE contains an unsupported path: ${child}`, true);
		const stats = await checkedPath(child, "file", 0o600);
		if (stats.size % OPTMEM_POLICY.record_sizes.tree !== 0) {
			throw new OptMemError(
				`OptMem TREE file ${entry.name} is not aligned to ${OPTMEM_POLICY.record_sizes.tree}-byte records`,
				true,
			);
		}
	}
}

async function verifyStoreFiles(path: string): Promise<void> {
	let entries;
	try {
		entries = await readdir(path, { withFileTypes: true });
	} catch {
		throw new OptMemError(`OptMem store cannot be read: ${path}`, true);
	}
	const allowed: Record<string, true> = { config: true, "LOG.txt": true, TREE: true, ".lock": true };
	for (const entry of entries) {
		if (!Object.hasOwn(allowed, entry.name)) throw new OptMemError(`unexpected OptMem store path: ${entry.name}`, true);
		if (entry.isSymbolicLink()) throw new OptMemError(`OptMem store contains a symlink: ${join(path, entry.name)}`, true);
	}
	await checkedPath(join(path, "config"), "file", 0o600);
	const logStats = await checkedPath(join(path, "LOG.txt"), "file", 0o600);
	if (logStats.size % OPTMEM_POLICY.record_sizes.log !== 0) {
		throw new OptMemError(`OptMem LOG.txt is not aligned to ${OPTMEM_POLICY.record_sizes.log}-byte records`, true);
	}
	const tree = join(path, "TREE");
	await checkedPath(tree, "directory", 0o700);
	await verifyTree(tree);
	if (entries.some((entry) => entry.name === ".lock")) await checkedPath(join(path, ".lock"), "file", 0o600);
}

async function sha256(path: string): Promise<string> {
	const bytes = await readFile(path);
	return createHash("sha256").update(bytes).digest("hex");
}

function parseReceipt(value: unknown): OptMemReceipt {
	if (value === null || typeof value !== "object" || Array.isArray(value)) {
		throw new OptMemError("OptMem installation receipt is not an object", true);
	}
	const receipt = value as Record<string, unknown>;
	const expected = ["schema", "repository", "commit", "url", "sha256", "installed_at", "installer"];
	const actual = Object.keys(receipt).sort();
	if (actual.length !== expected.length || actual.some((key, index) => key !== expected.slice().sort()[index])) {
		throw new OptMemError("OptMem installation receipt has an unexpected schema", true);
	}
	if (
		receipt.schema !== OPTMEM_SCHEMA ||
		receipt.repository !== OPTMEM_REPOSITORY ||
		receipt.commit !== OPTMEM_COMMIT ||
		receipt.url !== OPTMEM_URL ||
		receipt.sha256 !== OPTMEM_SHA256 ||
		receipt.installer !== "omp-config" ||
		typeof receipt.installed_at !== "string" ||
		!Number.isFinite(Date.parse(receipt.installed_at))
	) {
		throw new OptMemError("OptMem installation receipt does not match the pinned contract", true);
	}
	return receipt as OptMemReceipt;
}

function decodeOutput(bytes: ArrayBuffer, label: string): string {
	if (bytes.byteLength > MAX_COMMAND_OUTPUT_BYTES) throw new OptMemError(`OptMem ${label} output is too large`, true);
	try {
		return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
	} catch {
		throw new OptMemError(`OptMem ${label} output is not valid UTF-8`, true);
	}
}

function outputText(run: MemoRun): string {
	return run.stdout.trimEnd() || run.stderr.trimEnd();
}

function safeInteger(value: string): number | undefined {
	if (!/^\d+$/.test(value)) return undefined;
	const parsed = Number(value);
	return Number.isSafeInteger(parsed) ? parsed : undefined;
}

function parseRange(value: string): BlockRange {
	if (Buffer.byteLength(value, "utf8") > MAX_RANGE_BYTES || !/^\d+-\d+$/.test(value)) {
		throw new OptMemError("OptMem range must be an aligned inclusive lo-hi identifier");
	}
	const [loText, hiText] = value.split("-");
	const lo = safeInteger(loText);
	const hi = safeInteger(hiText);
	if (lo === undefined || hi === undefined || lo > hi) {
		throw new OptMemError("OptMem range must be an aligned inclusive lo-hi identifier");
	}
	return { lo, hi };
}

function normalizeRange(value: string): string {
	const range = parseRange(value);
	return `${range.lo}-${range.hi}`;
}

function validateOneLine(value: string, label: string): string {
	if (typeof value !== "string") throw new OptMemError(`OptMem ${label} must be text`);
	const normalized = value.normalize("NFC");
	if (normalized.length === 0 || normalized.includes("\n") || normalized.includes("\r") || normalized.includes("\0")) {
		throw new OptMemError(`OptMem ${label} must be one non-empty line`);
	}
	if (Buffer.byteLength(normalized, "utf8") > OPTMEM_ENTRY_BYTES) {
		throw new OptMemError(`OptMem ${label} exceeds the ${OPTMEM_ENTRY_BYTES}-byte UTF-8 limit`);
	}
	if (
		/-----BEGIN [A-Z0-9 ]+-----/i.test(normalized) ||
		/\b(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]{12,}/i.test(normalized) ||
		/\b(?:sk|rk|ghp|gho|xox[baprs])[-_][A-Za-z0-9._-]{8,}/i.test(normalized) ||
		/\bAKIA[0-9A-Z]{16}\b/.test(normalized) ||
		/https?:\/\/[^\s/@:]+:[^\s/@]+@/i.test(normalized) ||
		/\b(?:TOKEN|SECRET|PASSWORD|PRIVATE[_-]?KEY|API[_-]?KEY)\s*=/i.test(normalized)
	) {
		throw new OptMemError(`OptMem ${label} matches the secret-redaction policy`);
	}
	return normalized;
}

function validateRecall(value: string): string {
	if (typeof value !== "string" || value.length === 0 || Buffer.byteLength(value, "utf8") > MAX_RECALL_BYTES) {
		throw new OptMemError("OptMem recall regex is empty or too large");
	}
	if (value.includes("\n") || value.includes("\r") || value.includes("\0")) {
		throw new OptMemError("OptMem recall regex must not contain newline or NUL");
	}
	try {
		new RegExp(value, "i");
	} catch {
		throw new OptMemError("OptMem recall regex is invalid");
	}
	return value;
}

function parseWakeContinuation(text: string): { part: number; snapshot: number } | undefined {
	const matches = [...text.matchAll(/^Not awake yet\. Run:\s+[^\r\n]*\bwake\s+(\d+)\s+(\d+)\s*$/gm)];
	if (matches.length === 0) return undefined;
	if (matches.length !== 1) throw new OptMemError("OptMem wake emitted ambiguous pagination", true);
	const part = safeInteger(matches[0][1]);
	const snapshot = safeInteger(matches[0][2]);
	if (part === undefined || snapshot === undefined || part < 1) {
		throw new OptMemError("OptMem wake emitted malformed pagination", true);
	}
	return { part, snapshot };
}

function parseNapDirective(text: string): BlockRange | undefined {
	const matches = [...text.matchAll(/Compress\s+#?(\d+)-(\d+)\s+by running:\s+[^\r\n]*\bnap\s+(\d+)-(\d+)\s+"[^"\r\n]*"/g)];
	if (matches.length === 0) return undefined;
	if (matches.length !== 1) throw new OptMemError("OptMem emitted ambiguous nap work", true);
	const firstLo = safeInteger(matches[0][1]);
	const firstHi = safeInteger(matches[0][2]);
	const commandLo = safeInteger(matches[0][3]);
	const commandHi = safeInteger(matches[0][4]);
	if (
		firstLo === undefined ||
		firstHi === undefined ||
		commandLo === undefined ||
		commandHi === undefined ||
		firstLo !== commandLo ||
		firstHi !== commandHi ||
		firstLo > firstHi
	) {
		throw new OptMemError("OptMem emitted malformed nap work", true);
	}
	return { lo: firstLo, hi: firstHi };
}

function hasAwakeMarker(text: string): boolean {
	return /^You are awake\.\s*$/m.test(text);
}

function hasExpectedReadOutput(action: "recall" | "zoom", text: string): boolean {
	if (action === "recall") return text.includes("No match.") || /(?:^|\n)#\d+(?:-\d+)?\s/.test(text) || /\bmatch(?:es)?\.?$/m.test(text);
	return /(?:^|\n)#\d+(?:-\d+)?\s/.test(text) || text.includes("not compressed yet");
}

export class OptMemRuntime {
	#state: OptMemState = "cold";
	#blockedReason: string | undefined;
	#pendingNap: BlockRange | undefined;
	#wakeMaterial = "";
	#startPromise: Promise<void> | undefined;
	#receipt: OptMemReceipt | undefined;
	#spawnProcess: MemoSpawn;

	constructor(spawnProcess: MemoSpawn = Bun.spawn) {
		this.#spawnProcess = spawnProcess;
	}

	get state(): OptMemState {
		return this.#state;
	}

	get pendingNap(): string | undefined {
		return this.#pendingNap ? `${this.#pendingNap.lo}-${this.#pendingNap.hi}` : undefined;
	}

	reset(): void {
		this.#state = "cold";
		this.#blockedReason = undefined;
		this.#pendingNap = undefined;
		this.#wakeMaterial = "";
		this.#startPromise = undefined;
		this.#receipt = undefined;
	}

	async start(): Promise<void> {
		if (this.#startPromise) return this.#startPromise;
		this.#startPromise = this.#startInternal();
		return this.#startPromise;
	}

	private async #startInternal(): Promise<void> {
		this.#state = "waking";
		try {
			this.#receipt = await this.verifyInstallation();
			await this.#wake();
		} catch (error) {
			this.#block(error);
		}
	}

	async verifyInstallation(): Promise<OptMemReceipt> {
		await checkedPath(OPTMEM_HOME, "directory", 0o700);
		await checkedPath(OPTMEM_STORE, "directory", 0o700);
		await checkedPath(OPTMEM_EXECUTABLE, "file", 0o700);
		await checkedPath(OPTMEM_RECEIPT, "file", 0o600);
		await verifyStoreFiles(OPTMEM_STORE);
		let receiptValue: unknown;
		try {
			receiptValue = JSON.parse(await readFile(OPTMEM_RECEIPT, "utf8"));
		} catch {
			throw new OptMemError("OptMem installation receipt is unreadable", true);
		}
		const receipt = parseReceipt(receiptValue);
		const actualHash = await sha256(OPTMEM_EXECUTABLE);
		if (actualHash !== OPTMEM_SHA256 || receipt.sha256 !== actualHash) {
			throw new OptMemError("OptMem executable hash does not match the pinned receipt", true);
		}
		return receipt;
	}

	wakePrompt(): string {
		if (this.#state === "blocked") return `OptMem is blocked: ${this.#blockedReason ?? "installation or memory state is unsafe"}.`;
		if (this.#state === "nap_required") {
			return `${this.#wakeMaterial}\n\nOptMem requires the next nap block ${this.pendingNap}. Call optmem with action nap and a one-line summary before using any other tool.`;
		}
		return this.#wakeMaterial;
	}

	statusText(): string {
		return JSON.stringify({
			state: this.#state,
			verified: this.#receipt !== undefined,
			commit: this.#receipt?.commit ?? OPTMEM_COMMIT,
			sha256: this.#receipt?.sha256 ?? OPTMEM_SHA256,
			pendingNap: this.pendingNap ?? null,
			blockedReason: this.#blockedReason ?? null,
		});
	}

	async execute(action: OptMemAction, signal?: AbortSignal): Promise<OptMemActionResult> {
		try {
			if (action.action === "status") {
				try {
					this.#receipt = await this.verifyInstallation();
				} catch (error) {
					this.#block(error);
				}
				return { text: this.statusText(), isError: this.#state === "blocked" };
			}
			await this.start();
			if (this.#state === "blocked") return { text: this.statusText(), isError: true };
			if (action.action === "nap") return await this.#nap(action.range, action.summary, signal);
			if (this.#state !== "ready") {
				return { text: `OptMem is not ready; complete the required nap block ${this.pendingNap ?? ""}.`, isError: true };
			}
			switch (action.action) {
				case "note":
					return await this.#note(action.text, signal);
				case "recall":
					return await this.#read("recall", ["recall", validateRecall(action.regex)], signal);
				case "zoom":
					return await this.#read("zoom", ["zoom", normalizeRange(action.range)], signal);
			}
		} catch (error) {
			if (error instanceof OptMemError && error.blocked) this.#block(error);
			return { text: error instanceof Error ? error.message : "OptMem action failed", isError: true };
		}
	}

	private async #note(text: string, signal?: AbortSignal): Promise<OptMemActionResult> {
		const normalized = validateOneLine(text, "note");
		const run = await this.#spawn(["note", normalized], true, signal);
		const output = outputText(run);
		if (run.code !== 0) return { text: output || "OptMem note failed", isError: true };
		if (!/^Saved as #\d+\.$/m.test(output)) {
			this.#block(new OptMemError("OptMem note returned an unrecognized success response", true));
			return { text: this.statusText(), isError: true };
		}
		await this.#wake();
		return { text: output, isError: this.#state === "blocked" };
	}

	private async #nap(rangeText: string, summary: string, signal?: AbortSignal): Promise<OptMemActionResult> {
		if (this.#state !== "nap_required" || !this.#pendingNap) {
			return { text: "OptMem has no pending nap work.", isError: true };
		}
		const range = normalizeRange(rangeText);
		const expected = `${this.#pendingNap.lo}-${this.#pendingNap.hi}`;
		if (range !== expected) return { text: `OptMem requires nap block ${expected} next.`, isError: true };
		const normalized = validateOneLine(summary, "nap summary");
		const run = await this.#spawn(["nap", range, normalized], true, signal);
		const output = outputText(run);
		if (run.code !== 0) return { text: output || "OptMem nap failed", isError: true };
		if (!new RegExp(`(?:^|\\n)${range.replace("-", "\\-")} (?:saved\\.|was settled or forgotten meanwhile\\.)`, "m").test(output) && !output.includes("Nothing left to compress.") && !output.includes("is already settled.")) {
			this.#block(new OptMemError("OptMem nap returned an unrecognized success response", true));
			return { text: this.statusText(), isError: true };
		}
		await this.#wake();
		return { text: output, isError: this.#state === "blocked" };
	}

	private async #read(action: "recall" | "zoom", args: string[], signal?: AbortSignal): Promise<OptMemActionResult> {
		const run = await this.#spawn(args, false, signal);
		const output = outputText(run);
		if (run.code !== 0) return { text: output || `OptMem ${action} failed`, isError: true };
		if (!hasExpectedReadOutput(action, output)) {
			this.#block(new OptMemError(`OptMem ${action} returned an unrecognized response`, true));
			return { text: this.statusText(), isError: true };
		}
		return { text: output };
	}

	private async #wake(): Promise<void> {
		this.#state = "waking";
		this.#pendingNap = undefined;
		const pages: string[] = [];
		let args = ["wake"];
		for (let page = 0; page < MAX_WAKE_PAGES; page += 1) {
			const run = await this.#spawn(args, false);
			const output = outputText(run);
			pages.push(output);
			this.#wakeMaterial = pages.filter(Boolean).join("\n\n");
			const continuation = parseWakeContinuation(output);
			if (continuation) {
				if (run.code !== 0) throw new OptMemError("OptMem wake pagination failed", true);
				args = ["wake", String(continuation.part), String(continuation.snapshot)];
				continue;
			}
			const nap = parseNapDirective(output);
			if (nap) {
				if (run.code !== 0 && !output.includes("Cannot wake:")) throw new OptMemError("OptMem wake failed before its nap gate", true);
				this.#pendingNap = nap;
				this.#state = "nap_required";
				return;
			}
			if (run.code !== 0) throw new OptMemError(output || "OptMem wake failed", true);
			if (!hasAwakeMarker(output)) throw new OptMemError("OptMem wake ended without the final awake marker", true);
			this.#state = "ready";
			return;
		}
		throw new OptMemError("OptMem wake exceeded the pagination limit", true);
	}

	private async #spawn(args: string[], write: boolean, signal?: AbortSignal): Promise<MemoRun> {
		let child: ReturnType<typeof Bun.spawn>;
		try {
			child = this.#spawnProcess([...RESTRICTED_LAUNCH, OPTMEM_EXECUTABLE, ...args], {
				env: {
					HOME: process.env.HOME ?? homedir(),
					MEMORY_DIR: OPTMEM_STORE,
					PATH: process.env.PATH ?? "",
				},
				stdout: "pipe",
				stderr: "pipe",
			});
		} catch {
			throw new OptMemError("OptMem executable could not be started", true);
		}
		let aborted = false;
		const abort = (): void => {
			aborted = true;
			child.kill();
		};
		if (signal?.aborted) abort();
		signal?.addEventListener("abort", abort, { once: true });
		try {
			const [stdoutBytes, stderrBytes, code] = await Promise.all([
				new Response(child.stdout).arrayBuffer(),
				new Response(child.stderr).arrayBuffer(),
				child.exited,
			]);
			if (aborted || signal?.aborted) {
				if (write) throw new OptMemError("OptMem write outcome is ambiguous; read back before retrying", true);
				throw new OptMemError("OptMem read was interrupted");
			}
			return {
				code,
				stdout: decodeOutput(stdoutBytes, "stdout"),
				stderr: decodeOutput(stderrBytes, "stderr"),
			};
		} finally {
			signal?.removeEventListener("abort", abort);
		}
	}

	#block(error: unknown): void {
		this.#state = "blocked";
		this.#blockedReason = error instanceof Error ? error.message : "unknown OptMem failure";
	}
}
