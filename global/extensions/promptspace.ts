/**
 * promptspace.ts — personal promptspace for stock omp. No fork, no patched dist.
 *
 * Runs against the official @oh-my-pi/pi-coding-agent package via documented
 * extension APIs only (`ctx.ui.setEditorComponent`, `ctx.getContextUsage`,
 * `ctx.models`, `pi.getThinkingLevel`, `pi.exec`). Auto-discovered from
 * ~/.omp/agent/extensions/ at startup; iterate by editing this file and
 * restarting omp. (Theme JSON edits hot-reload; editor replacement does not.)
 *
 *   Layout (colors come from the live theme, hot-reload friendly):
 *
 *                                          <- one air row separates transcript
 *   ▎ input text                           <- quarter-block rail, bare 1-cell
 *   ▎ wrapped continuation                    gutter; panel bg only while
 *   ▎                            2 ·       focused; right-aligned chips
 *
 *   ⠧  provider  Fable 5 · 󰪣 high ·  dir ·  main +1 *2 ?3 ⇡1   ▰▰▱▱ 42% · 4.20
 *
 * State signals:
 *   - no prompt marker: the rail color is the mode label (session accent /
 *     bash / python / thinking level / focus-proxy faint)
 *   - busy: theme spinner in the status-line indent; nothing in the card moves
 *   - status: icon-led clusters from theme.symbol() (nerd/unicode/ascii
 *     presets degrade together); git shows +staged *unstaged ?untracked ⇡⇣;
 *     ctx is an 8-cell block meter, amber ≥70 and red ≥90; provider drops
 *     <100 cols, folder <80
 *
 * Companion config (~/.omp/agent/config.yml):
 *   tui.chrome: plain            -> stock borderless composer + plain tool chrome
 *   statusLine.preset: custom
 *   statusLine.leftSegments: []  -> silences the built-in status line (this file
 *   statusLine.rightSegments: []    renders its own, below the input; hook
 *                                   statuses still render via StatusLineComponent)
 */

import * as path from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";
import { CustomEditor } from "@oh-my-pi/pi-coding-agent/modes/components/custom-editor";
import { truncateToWidth } from "@oh-my-pi/pi-tui";
import { type GitInfo, parseGitStatus } from "../lib/promptspace-git.ts";

const GIT_TTL_MS = 3_000;
const CONTEXT_TTL_MS = 1_000;
const AMBIENT_REFRESH_MS = 30_000;
const SPINNER_PERIOD_MS = 120;
/** Accent bar + one space of card padding. */
const BAR_WIDTH = 2;
/** Context meter width in cells. */
const CTX_CELLS = 8;

/** Rail glyph: quarter-block keeps the card marked without dominating tall
 *  states (autocomplete open, long prompts). */
const RAIL = "▎";

function width(text: string): number {
	return Bun.stringWidth(text, { countAnsiEscapeCodes: false });
}

function currentFolder(dir: string, home: string): string {
	if (dir === home) return "~";
	return path.basename(dir) || dir;
}


export default function (pi: ExtensionAPI) {
	// ── cached ambient data (renders must stay sync + O(1)) ────────────────
	let git: GitInfo | undefined;
	let gitCwd: string | undefined;
	let gitAt = 0;
	let gitInFlight = false;
	let ctxUsage: { tokens: number; contextWindow: number } | undefined;
	let ctxUsageAt = 0;
	let ambientTimer: Timer | undefined;
	let busyFrameTimer: Timer | undefined;

	function refreshGit(cwd: string): void {
		const now = Date.now();
		if (cwd !== gitCwd) {
			// Stale repo: drop the old branch immediately, force a refresh.
			git = undefined;
			gitCwd = cwd;
			gitAt = 0;
		}
		if (gitInFlight || now - gitAt < GIT_TTL_MS) return;
		gitInFlight = true;
		void (async () => {
			try {
				// One call: `## branch...upstream [ahead 2, behind 1]` header plus
				// one line per dirty path.
				const status = await pi.exec("git", ["-C", cwd, "status", "-b", "--porcelain"]);
				if (cwd !== gitCwd) return; // answer for a repo we already left
				git = parseGitStatus(status.stdout, status.code);
			} catch {
				git = undefined;
			} finally {
				gitInFlight = false;
				// A discarded stale answer must not TTL-block the new cwd.
				gitAt = cwd === gitCwd ? Date.now() : 0;
			}
		})();
	}

	pi.on("session_start", (_event, ctx: ExtensionContext) => {
		const home = process.env.HOME ?? "";

		function contextPercent(): number | undefined {
			const now = Date.now();
			if (now - ctxUsageAt > CONTEXT_TTL_MS) {
				ctxUsage = ctx.getContextUsage();
				ctxUsageAt = now;
			}
			if (!ctxUsage?.contextWindow) return undefined;
			return (ctxUsage.tokens / ctxUsage.contextWindow) * 100;
		}

		function spinnerFrame(): string {
			const theme = ctx.ui.theme;
			const frames: string[] = theme.getSpinnerFrames?.("status") ?? ["·"];
			const frame = frames[Math.floor(Date.now() / SPINNER_PERIOD_MS) % frames.length] ?? "·";
			// Gutter math assumes a 1-cell glyph; never let a wide frame skew it.
			return width(frame) === 1 ? frame : "·";
		}

		/** Theme symbol lookup; empty string when the key or API is missing. */
		function sym(key: string): string {
			const theme = ctx.ui.theme as { symbol?: (k: never) => string | undefined };
			return theme.symbol?.(key as never) ?? "";
		}

		/** Icon-prefixed label; plain label under the ascii preset. */
		function iconed(icon: string, text: string): string {
			return icon ? `${icon} ${text}` : text;
		}

		/** ` ▰▰▱▱▱▱▱▱ 42%` — block meter colored by compaction thresholds. */
		function contextMeter(): string | undefined {
			const theme = ctx.ui.theme;
			const pct = contextPercent();
			if (pct === undefined) return undefined;
			const clamped = Math.min(100, Math.max(0, pct));
			const color = clamped >= 90 ? "error" : clamped >= 70 ? "warning" : "statusLineContext";
			const filled = Math.round((clamped / 100) * CTX_CELLS);
			const icon = sym("icon.context");
			return (
				theme.fg(color, `${icon ? `${icon} ` : ""}${"▰".repeat(filled)}`) +
				theme.fg("statusLineSep", "▱".repeat(CTX_CELLS - filled)) +
				theme.fg(color, ` ${clamped.toFixed(0)}%`)
			);
		}

		function statusLine(cols: number, busy: boolean): string {
			const theme = ctx.ui.theme; // Re-read after live light/dark theme changes.
			refreshGit(ctx.cwd);
			const dot = theme.fg("statusLineSep", " · ");

			// left: identity + location. Icons lead each cluster; one muted
			// family, live git state gets the only saturated colors.
			const left: string[] = [];
			const model = ctx.models.current();
			if (model) {
				const name = model.name.startsWith("Claude ") ? model.name.slice(7) : model.name;
				const cluster = theme.fg("statusLineModel", iconed(sym("icon.model"), name));
				left.push(cols >= 100 ? `${theme.fg("statusLineSep", model.provider)} ${cluster}` : cluster);
				const level = pi.getThinkingLevel();
				if (level && level !== "off") {
					// Full per-level color ladder; every theme defines these keys.
					// Unknown levels (e.g. auto) fall back to the muted context tone.
					const ladder: Record<string, string> = {
						minimal: "thinkingMinimal",
						low: "thinkingLow",
						medium: "thinkingMedium",
						high: "thinkingHigh",
						xhigh: "thinkingXhigh",
						max: "thinkingMax",
					};
					// Thinking symbols carry their own label ("󰪣 high").
					left.push(theme.fg((ladder[level] ?? "statusLineContext") as never, sym(`thinking.${level}`) || level));
				}
			}
			if (cols >= 80) left.push(theme.fg("statusLinePath", iconed(sym("icon.folder"), currentFolder(ctx.cwd, home))));
			if (git) {
				const parts = [theme.fg("statusLinePath", iconed(sym("icon.branch"), git.branch))];
				if (git.staged > 0) parts.push(theme.fg("statusLineStaged", `+${git.staged}`));
				if (git.unstaged > 0) parts.push(theme.fg("statusLineDirty", `*${git.unstaged}`));
				if (git.untracked > 0) parts.push(theme.fg("statusLineUntracked", `?${git.untracked}`));
				if (git.ahead > 0 || git.behind > 0) {
					const arrows = `${git.ahead > 0 ? `⇡${git.ahead}` : ""}${git.behind > 0 ? `⇣${git.behind}` : ""}`;
					parts.push(theme.fg("statusLineSep", arrows));
				}
				left.push(parts.join(" "));
			}

			// right: only the two continuous meters that change decisions
			const right: string[] = [];
			const meter = contextMeter();
			if (meter) right.push(meter);
			const cost = ctx.sessionManager.getUsageStatistics?.().cost;
			if (cost) right.push(theme.fg("statusLineCost", `${sym("icon.cost") || "$"}${cost.toFixed(2)}`));

			// Assemble with a 2-col indent; the indent doubles as the busy
			// spinner slot so nothing jumps when the agent starts running.
			// Degrade right-to-left: cost, context, git, folder, effort;
			// model identity survives.
			const indent = busy ? `${theme.fg("accent", spinnerFrame())} ` : "  ";
			const assemble = (keepLeft: number, keepRight: number): string | undefined => {
				const leftText = `${indent}${left.slice(0, keepLeft).join(dot)}`;
				const rightText = right.slice(0, keepRight).join(dot);
				const gap = cols - width(leftText) - width(rightText) - 2;
				if (rightText && gap >= 3) return `${leftText}${" ".repeat(gap)}${rightText}`;
				if (!rightText && width(leftText) <= cols) return leftText;
				return undefined;
			};
			for (let keepRight = right.length; keepRight >= 0; keepRight--) {
				const fitted = assemble(left.length, keepRight);
				if (fitted) return fitted;
			}
			for (let keepLeft = left.length - 1; keepLeft >= 1; keepLeft--) {
				const fitted = assemble(keepLeft, 0);
				if (fitted) return fitted;
			}
			return truncateToWidth(`${indent}${left[0] ?? ""}`, cols);
		}

		class PromptspaceEditor extends CustomEditor {

			render(cols: number): readonly string[] {
				const theme = ctx.ui.theme;
				const busy = !ctx.isIdle();

				// Bare 1-cell gutter: no prompt marker, text column never moves.
				// The busy spinner rides the status-line indent instead, and the
				// rail color already carries mode/thinking state.
				this.setPromptGutter(" ");

				// Streaming renders arrive in bursts; a short self-tick keeps the
				// spinner advancing between them. One pending tick, ever; idle
				// clears it so an orphaned timer can't outlive the busy state.
				if (busy && busyFrameTimer === undefined) {
					busyFrameTimer = setTimeout(() => {
						busyFrameTimer = undefined;
						this.tui.requestRender();
					}, SPINNER_PERIOD_MS);
					busyFrameTimer.unref?.();
				} else if (!busy && busyFrameTimer !== undefined) {
					clearTimeout(busyFrameTimer);
					busyFrameTimer = undefined;
				}

				// Below ~8 cols there is no room for chrome: fall back to the raw
				// editor so the buffer stays usable.
				if (cols < BAR_WIDTH + 6) return super.render(cols);
				const innerWidth = cols - BAR_WIDTH;
				const bar = `${this.borderColor(RAIL)} `;
				// Panel background only while the composer owns focus; the accent
				// bar alone marks the card when a dialog or overlay has focus.
				const panel = (content: string): string =>
					this.focused ? theme.bg("userMessageBg", `${bar}${content}`) : `${bar}${content}`;
				const padRow = (content = ""): string => {
					const w = width(content);
					const fitted = w > innerWidth ? truncateToWidth(content, innerWidth) : content;
					return panel(fitted + " ".repeat(Math.max(0, innerWidth - width(fitted))));
				};

				// Footer row: right-aligned attachment/queue chips when present,
				// otherwise a blank padding row (bottom half of the card frame).
				const chips: string[] = [];
				const images = this.pendingImages?.length ?? 0;
				if (images > 0) chips.push(iconed(sym("icon.extensionContextFile"), String(images)));
				if (ctx.hasPendingMessages()) chips.push("queued");
				let footer = "";
				if (chips.length > 0) {
					const chipText = chips.join(" · ");
					const gap = innerWidth - width(chipText) - 1;
					if (gap >= 2) footer = `${" ".repeat(gap)}${theme.fg("dim", chipText)} `;
				}

				const body = super.render(innerWidth);
				return ["", padRow(), ...body.map(panel), padRow(footer), statusLine(cols, busy)];
			}
		}

		ctx.ui.setEditorComponent((tui, editorTheme, keybindings) => {
			const editor = new PromptspaceEditor(tui, editorTheme, keybindings);
			editor.setBorderVisible(false);
			// Refresh cached git/context/cost values while the editor is idle.
			clearInterval(ambientTimer);
			clearTimeout(busyFrameTimer);
			busyFrameTimer = undefined;
			ambientTimer = setInterval(() => tui.requestRender(), AMBIENT_REFRESH_MS);
			ambientTimer.unref?.();
			return editor;
		});
	});
}
