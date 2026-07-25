import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import rawManifest from "../skill-composer-manifest.json" with { type: "json" };

export interface SkillComposerManifest {
	version: 1;
	agents: Record<string, readonly string[]>;
}

export type SkillCatalog = Readonly<Record<string, string>>;

export interface CompositionResult {
	payload: unknown;
	changed: boolean;
	error?: string;
	agent?: string;
	beforeBytes?: number;
	afterBytes?: number;
}

const IDENTITY_PREFIX = "<!-- omp-composition-agent:";
const IDENTITY_PATTERN = /<!-- omp-composition-agent: ([a-z][a-z0-9_-]*) -->/g;
const SKILL_NAME_PATTERN = /^[a-z][a-z0-9_-]*$/;

/**
 * Match a canonical <skills> block. OMP renders skills with multi-line
 * descriptions (folded YAML scalars) and blank lines between entries, so the
 * pattern must accept arbitrary content between the tags. Captured OMP payloads
 * confirm the real shape: `<skills>\n- name: multi-line\ndesc\n\n- name2: ...\n</skills>`.
 */
const SKILLS_BLOCK_PATTERN = /<skills>\n([\s\S]*?)\n<\/skills>/g;

/**
 * Entry start in the default template: `- name: ` at the beginning of a line.
 * Descriptions may span multiple lines until the next entry or block end.
 */
const DEFAULT_ENTRY_START = /^- ([a-z][a-z0-9_-]*): /gm;

/**
 * Entry in the custom template: `<skill name="name">\ndesc\n</skill>`.
 */
const CUSTOM_ENTRY_PATTERN = /<skill name="([a-z][a-z0-9_-]*)">\n([\s\S]*?)\n<\/skill>/g;

export const compositionManifest = rawManifest as SkillComposerManifest;

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * Parse a `description:` frontmatter value from a SKILL.md file. Handles
 * inline scalars (`description: foo`), literal block scalars (`description: |`),
 * and folded block scalars (`description: >`). Returns a single-line string.
 */
function parseDescription(file: string): string | undefined {
	let source: string;
	try {
		source = readFileSync(file, "utf8");
	} catch {
		return undefined;
	}
	const frontmatter = source.match(/^---\n([\s\S]*?)\n---\n/);
	if (!frontmatter) return undefined;
	const lines = frontmatter[1]?.split("\n") ?? [];
	const start = lines.findIndex((line) => /^description:\s*/.test(line));
	if (start < 0) return undefined;
	const first = lines[start]?.replace(/^description:\s*/, "").trim() ?? "";
	if (first && first !== "|" && first !== ">")
		return first.replace(/^['"]|['"]$/g, "");
	// Block scalar (| or >): collect indented body lines.
	const body: string[] = [];
	for (const line of lines.slice(start + 1)) {
		if (/^[A-Za-z][A-Za-z0-9_-]*:\s*/.test(line)) break;
		if (line.trim()) body.push(line.trim());
	}
	return body.length > 0 ? body.join(" ") : undefined;
}

export function readSkillCatalog(
	root = process.env.PI_CODING_AGENT_DIR,
): SkillCatalog {
	if (!root) return {};
	const skillsDir = join(root, "skills");
	let entries: string[];
	try {
		entries = readdirSync(skillsDir);
	} catch {
		return {};
	}
	const catalog: Record<string, string> = {};
	for (const name of entries) {
		const skillFile = join(skillsDir, name, "SKILL.md");
		try {
			if (!statSync(skillFile).isFile()) continue;
		} catch {
			continue;
		}
		const description = parseDescription(skillFile);
		if (description) catalog[name] = description;
	}
	return catalog;
}

function identityFromPrompt(promptText: string): {
	agent?: string;
	error?: string;
} {
	const markers = [...promptText.matchAll(IDENTITY_PATTERN)];
	if (markers.length === 1) return { agent: markers[0]?.[1] };
	if (promptText.includes(IDENTITY_PREFIX)) {
		return {
			error:
				"skill composer: prompt-shape drift: expected exactly one valid agent identity marker",
		};
	}
	return {};
}

/**
 * Parse skill entries from a <skills> block body. Supports both OMP template
 * formats:
 * - Default: `- name: multi-line description` entries separated by blank lines
 * - Custom:  `<skill name="name">description</skill>` entries
 *
 * Returns a map of name → description, or an error if the block is malformed.
 */
function parseSkillsBlock(
	blockContent: string,
): Map<string, string> | { error: string } {
	// Try custom template format first: <skill name="...">desc</skill>
	const customMatches = [...blockContent.matchAll(CUSTOM_ENTRY_PATTERN)];
	if (customMatches.length > 0) {
		const entries = new Map<string, string>();
		for (const match of customMatches) {
			const name = match[1];
			const description = match[2]?.trim() ?? "";
			if (!description)
				return {
					error: `skill composer: prompt-shape drift: empty description for skill ${name}`,
				};
			entries.set(name, description);
		}
		return entries;
	}

	// Default template format: `- name: description` (possibly multi-line)
	const starts = [...blockContent.matchAll(DEFAULT_ENTRY_START)];
	if (starts.length === 0) {
		return {
			error:
				"skill composer: prompt-shape drift: no skill entries in <skills> block",
		};
	}
	const entries = new Map<string, string>();
	for (let i = 0; i < starts.length; i++) {
		const match = starts[i];
		const name = match[1];
		const descStart = (match.index ?? 0) + match[0].length;
		const descEnd =
			i + 1 < starts.length
				? (starts[i + 1]?.index ?? descStart)
				: blockContent.length;
		const description = blockContent
			.slice(descStart, descEnd)
			.replace(/\n+$/, "")
			.trim();
		if (!description)
			return {
				error: `skill composer: prompt-shape drift: empty description for skill ${name}`,
			};
		entries.set(name, description);
	}
	return entries;
}

/**
 * Reject descriptions that could escape the <skills> metadata block. A
 * description containing `</skills>` would inject top-level prompt content;
 * `</skill>` breaks the custom template. Both are reject-and-drift errors.
 */
function validateDescription(name: string, description: string): string | undefined {
	if (description.includes("</skills>"))
		return `skill composer: prompt-shape drift: skill ${name} description contains </skills>`;
	if (description.includes("</skill>"))
		return `skill composer: prompt-shape drift: skill ${name} description contains </skill>`;
	return undefined;
}

function renderSkillsBlock(
	promptText: string,
	agent: string,
	manifest: SkillComposerManifest,
	catalog: SkillCatalog,
): { prompt?: string; error?: string } {
	const requested = manifest.agents[agent];
	if (!requested) return {};
	if (
		!Array.isArray(requested) ||
		requested.length === 0 ||
		requested.some((name) => !SKILL_NAME_PATTERN.test(name))
	) {
		return {
			error: `skill composer: invalid composition manifest for declared agent ${agent}`,
		};
	}
	const names = new Set(requested);
	if (names.size !== requested.length) {
		return {
			error: `skill composer: invalid composition manifest for declared agent ${agent}: duplicate skills`,
		};
	}
	const matches = [...promptText.matchAll(SKILLS_BLOCK_PATTERN)];
	if (matches.length !== 1) {
		return {
			error:
				"skill composer: prompt-shape drift: expected exactly one canonical <skills> block",
		};
	}
	const block = matches[0]?.[1] ?? "";
	const parsed = parseSkillsBlock(block);
	if ("error" in parsed) return { error: parsed.error };
	const existing = parsed;

	// Resolve descriptions: prefer catalog, fall back to existing block.
	const descriptions = requested.map((name) => {
		const description = catalog[name] ?? existing.get(name);
		if (!description) return undefined;
		const error = validateDescription(name, description);
		if (error) return undefined;
		return `- ${name}: ${description}`;
	});
	if (descriptions.some((line) => line === undefined)) {
		const missing = requested.filter(
			(name) => !catalog[name] && !existing.has(name),
		);
		if (missing.length > 0) {
			return {
				error: `skill composer: missing declared skill description(s): ${missing.join(", ")}`,
			};
		}
		// A description existed but failed validation.
		for (const name of requested) {
			const desc = catalog[name] ?? existing.get(name);
			if (desc) {
				const error = validateDescription(name, desc);
				if (error) return { error };
			}
		}
		return {
			error: `skill composer: description validation failed for agent ${agent}`,
		};
	}
	const replacement = `<skills>\n${descriptions.join("\n")}\n</skills>`;
	const markerlessPrompt = promptText.replace(IDENTITY_PATTERN, "");
	// Use a replacer function to avoid String.replace interpreting $&, $`, $'
	// in the replacement string.
	return {
		prompt: markerlessPrompt.replace(matches[0]?.[0] ?? "", () => replacement),
	};
}

interface Carrier {
	kind: "string" | "string-array" | "text-array" | "gemini";
	key: "systemPrompt" | "system" | "instructions" | "systemInstruction";
	value: unknown;
	text: string;
}

function findCarrier(payload: Record<string, unknown>): {
	carrier?: Carrier;
	error?: string;
} {
	const candidates: Carrier[] = [];
	for (const key of ["systemPrompt", "system", "instructions"] as const) {
		const value = payload[key];
		if (typeof value === "string")
			candidates.push({ kind: "string", key, value, text: value });
		else if (Array.isArray(value) && value.length === 1) {
			const first = value[0];
			if (typeof first === "string") {
				candidates.push({ kind: "string-array", key, value, text: first });
			} else if (
				isRecord(first) &&
				first.type === "text" &&
				typeof first.text === "string"
			) {
				candidates.push({ kind: "text-array", key, value, text: first.text });
			}
		}
	}
	const systemInstruction = payload.systemInstruction;
	if (
		isRecord(systemInstruction) &&
		Array.isArray(systemInstruction.parts) &&
		systemInstruction.parts.length === 1
	) {
		const part = systemInstruction.parts[0];
		if (isRecord(part) && typeof part.text === "string") {
			candidates.push({
				kind: "gemini",
				key: "systemInstruction",
				value: systemInstruction,
				text: part.text,
			});
		}
	}
	const marked = candidates.filter((candidate) =>
		candidate.text.includes(IDENTITY_PREFIX),
	);
	if (marked.length === 1) return { carrier: marked[0] };
	if (marked.length > 1)
		return {
			error:
				"skill composer: prompt-shape drift: agent marker appears in multiple provider fields",
		};
	return {};
}

function replaceCarrier(carrier: Carrier, text: string): unknown {
	if (carrier.kind === "string") return text;
	if (carrier.kind === "string-array") return [text];
	if (carrier.kind === "text-array") {
		if (!Array.isArray(carrier.value) || carrier.value.length !== 1)
			return carrier.value;
		const item = carrier.value[0];
		return isRecord(item) ? [{ ...item, text }] : carrier.value;
	}
	if (
		!isRecord(carrier.value) ||
		!Array.isArray(carrier.value.parts) ||
		carrier.value.parts.length !== 1
	)
		return carrier.value;
	const part = carrier.value.parts[0];
	return isRecord(part)
		? { ...carrier.value, parts: [{ ...part, text }] }
		: carrier.value;
}

export function composeProviderRequest(
	payload: unknown,
	manifest: SkillComposerManifest | undefined,
	catalog: SkillCatalog = {},
): CompositionResult {
	if (!isRecord(payload) || !manifest || manifest.version !== 1) {
		let bytes: number | undefined;
		try {
			bytes = Buffer.byteLength(JSON.stringify(payload));
		} catch {
			bytes = undefined;
		}
		return { payload, changed: false, beforeBytes: bytes, afterBytes: bytes };
	}
	let originalBytes: number;
	try {
		originalBytes = Buffer.byteLength(JSON.stringify(payload));
	} catch {
		// Cyclic or non-serializable payload: fail closed, preserve bytes.
		return { payload, changed: false };
	}
	const located = findCarrier(payload);
	if (located.error)
		return {
			payload,
			changed: false,
			error: located.error,
			beforeBytes: originalBytes,
			afterBytes: originalBytes,
		};
	if (!located.carrier) {
		if (JSON.stringify(payload).includes(IDENTITY_PREFIX)) {
			return {
				payload,
				changed: false,
				error:
					"skill composer: prompt-shape drift: no supported provider system-prompt carrier",
				beforeBytes: originalBytes,
				afterBytes: originalBytes,
			};
		}
		return { payload, changed: false };
	}
	const identity = identityFromPrompt(located.carrier.text);
	if (identity.error)
		return {
			payload,
			changed: false,
			error: identity.error,
			beforeBytes: originalBytes,
			afterBytes: originalBytes,
		};
	if (!identity.agent) {
		// No marker in a marked carrier: drift, not a silent skip.
		return {
			payload,
			changed: false,
			error:
				"skill composer: prompt-shape drift: identity marker present but unparseable",
			beforeBytes: originalBytes,
			afterBytes: originalBytes,
		};
	}
	if (!manifest.agents[identity.agent]) {
		// Stale marker resolving to a manifest-absent agent: fail loud.
		return {
			payload,
			changed: false,
			agent: identity.agent,
			error: `skill composer: unknown declared agent ${identity.agent}: no composition manifest entry; preserving payload unchanged`,
			beforeBytes: originalBytes,
			afterBytes: originalBytes,
		};
	}
	const rendered = renderSkillsBlock(
		located.carrier.text,
		identity.agent,
		manifest,
		catalog,
	);
	if (rendered.error || !rendered.prompt) {
		return {
			payload,
			changed: false,
			error: rendered.error,
			agent: identity.agent,
			beforeBytes: originalBytes,
			afterBytes: originalBytes,
		};
	}
	const next = {
		...payload,
		[located.carrier.key]: replaceCarrier(located.carrier, rendered.prompt),
	};
	const afterBytes = Buffer.byteLength(JSON.stringify(next));
	return {
		payload: next,
		changed: true,
		agent: identity.agent,
		beforeBytes: originalBytes,
		afterBytes,
	};
}

export default function skillComposer(pi: ExtensionAPI): void {
	let catalog = readSkillCatalog();
	pi.on("session_start", () => {
		catalog = readSkillCatalog();
	});
	pi.on("before_provider_request", (event) => {
		try {
			const result = composeProviderRequest(
				event.payload,
				compositionManifest,
				catalog,
			);
			if (result.error) pi.logger.error(result.error);
			return result.payload;
		} catch (err) {
			// Unexpected throw: fail closed, preserve the original payload.
			pi.logger.error(
				`skill composer: unexpected error, preserving payload: ${err instanceof Error ? err.message : String(err)}`,
			);
			return event.payload;
		}
	});
}
