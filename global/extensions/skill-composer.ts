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
	// Count raw prefix occurrences. If the prefix appears more times than the
	// valid pattern matches, a malformed marker is present. A malformed marker
	// must be drift even when one valid marker also exists — otherwise a stale
	// `<!-- omp-composition-agent: bad name! -->` next to a valid marker
	// silently composes the valid allowlist.
	let prefixCount = 0;
	for (let from = 0; ; prefixCount++) {
		const idx = promptText.indexOf(IDENTITY_PREFIX, from);
		if (idx < 0) break;
		from = idx + IDENTITY_PREFIX.length;
	}
	if (prefixCount !== markers.length) {
		return {
			error:
				"skill composer: prompt-shape drift: malformed agent identity marker (prefix present but pattern unmatched)",
		};
	}
	if (markers.length === 1) return { agent: markers[0]?.[1] };
	if (markers.length > 1) {
		return {
			error:
				"skill composer: prompt-shape drift: expected exactly one agent identity marker",
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
 * Reject descriptions that could escape the <skills> metadata block or inject
 * fake roster entries. Closers are matched case- and whitespace-insensitively
 * so `</SKILLS>`, `</skills >`, and CRLF variants cannot splice outside the
 * block. A description containing a newline-led `- name: ...` line would
 * inject a subtracted skill back into the composed block, defeating the
 * allowlist — reject it as drift.
 */
function validateDescription(name: string, description: string): string | undefined {
	if (/<\/skills\s*>/i.test(description))
		return `skill composer: prompt-shape drift: skill ${name} description contains a </skills> closer`;
	if (/<\/skill\s*>/i.test(description))
		return `skill composer: prompt-shape drift: skill ${name} description contains a </skill> closer`;
	if (/^- [a-z][a-z0-9_-]*: /m.test(description))
		return `skill composer: prompt-shape drift: skill ${name} description contains a roster-entry line`;
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

	// Resolve descriptions: prefer the existing in-prompt description (which
	// is OMP's native folded-scalar render) so the composed block matches what
	// OMP would render, falling back to the catalog for added skills. This
	// avoids a single-line catalog reformat diverging from the native block.
	const missing = requested.filter(
		(name) => !existing.has(name) && !catalog[name],
	);
	if (missing.length > 0) {
		return {
			error: `skill composer: missing declared skill description(s): ${missing.join(", ")}`,
		};
	}
	for (const name of requested) {
		const description = existing.get(name) ?? catalog[name];
		const error = validateDescription(name, description);
		if (error) return { error };
	}
	const descriptions = requested.map(
		(name) => `- ${name}: ${existing.get(name) ?? catalog[name]}`,
	);
	const replacement = `<skills>\n${descriptions.join("\n")}\n</skills>`;
	// Replace the block on the original prompt text, then strip the identity
	// marker. Ordering matters: computing the replacement against promptText
	// (pre-strip) guarantees the block is found, so a no-op replace cannot
	// report changed:true.
	const replaced = promptText.replace(matches[0]?.[0] ?? "", () => replacement);
	return { prompt: replaced.replace(IDENTITY_PATTERN, "") };
}

/**
 * A provider system-prompt carrier: a single string field (`instructions`),
 * one element of a string/`{text}` array (`system`/`systemPrompt`), or one
 * part of a Gemini `systemInstruction.parts` array. OMP splits the system
 * prompt into multiple cache-breakpoint chunks, so the `system` carrier is a
 * multi-element array on Anthropic (each element `{text: chunk}` with no
 * `type` field). `replace` returns the new value for the carrier's field.
 */
interface Carrier {
	field: "systemPrompt" | "system" | "instructions" | "systemInstruction";
	text: string;
	replace: (newText: string) => unknown;
}

function collectCarriers(payload: Record<string, unknown>): Carrier[] {
	const candidates: Carrier[] = [];
	const instructions = payload.instructions;
	if (typeof instructions === "string") {
		candidates.push({ field: "instructions", text: instructions, replace: (t) => t });
	}
	for (const field of ["systemPrompt", "system"] as const) {
		const value = payload[field];
		if (typeof value === "string") {
			candidates.push({ field, text: value, replace: (t) => t });
		} else if (Array.isArray(value)) {
			value.forEach((element, index) => {
				if (typeof element === "string") {
					candidates.push({
						field,
						text: element,
						replace: (t) => {
							const next = [...value];
							next[index] = t;
							return next;
						},
					});
				} else if (isRecord(element) && typeof element.text === "string") {
					// Anthropic `{text}` (no type) and OpenAI `{type:"text", text}`.
					candidates.push({
						field,
						text: element.text,
						replace: (t) => {
							const next = [...value];
							next[index] = { ...element, text: t };
							return next;
						},
					});
				}
			});
		}
	}
	const systemInstruction = payload.systemInstruction;
	if (isRecord(systemInstruction) && Array.isArray(systemInstruction.parts)) {
		const parts = systemInstruction.parts;
		parts.forEach((part, index) => {
			if (isRecord(part) && typeof part.text === "string") {
				candidates.push({
					field: "systemInstruction",
					text: part.text,
					replace: (t) => {
						const nextParts = [...parts];
						nextParts[index] = { ...part, text: t };
						return { ...systemInstruction, parts: nextParts };
					},
				});
			}
		});
	}
	return candidates;
}

function findCarrier(payload: Record<string, unknown>): {
	carrier?: Carrier;
	error?: string;
} {
	const carriers = collectCarriers(payload);
	const marked = carriers.filter((c) => c.text.includes(IDENTITY_PREFIX));
	if (marked.length === 1) return { carrier: marked[0] };
	if (marked.length > 1) {
		return {
			error:
				"skill composer: prompt-shape drift: agent marker appears in multiple provider system-prompt carriers",
		};
	}
	// No marked carrier. If the marker prefix appears in a carrier but did not
	// match the identity pattern, that is drift. A marker appearing only in a
	// non-carrier field (e.g. a user message quoting AGENTS.md) is NOT drift —
	// scanning the whole payload would raise a permanent per-request error on
	// harmless user input, so the scan is scoped to carrier candidates only.
	if (carriers.some((c) => c.text.includes(IDENTITY_PREFIX))) {
		return {
			error:
				"skill composer: prompt-shape drift: identity marker present in carrier but unparseable",
		};
	}
	return {};
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
		// No carrier carries the marker. findCarrier already reported drift
		// if a carrier held an unparseable marker; reaching here means the
		// marker is absent from every carrier (e.g. an undeclared agent with
		// no marker), which is a silent skip — not drift.
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
		[located.carrier.field]: located.carrier.replace(rendered.prompt),
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
