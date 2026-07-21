/**
 * promptspace.ts — personal promptspace for stock omp. No fork, no patched dist.
 *
 * Runs against the official @oh-my-pi/pi-coding-agent package via documented
 * extension APIs only (`ctx.ui.setEditorComponent`, `ctx.getContextUsage`,
 * `ctx.models`, `pi.getThinkingLevel`, `pi.exec`). Auto-discovered from
 * ~/.omp/agent/extensions/ at startup; iterate by editing this file and
 * restarting omp. (Theme JSON edits hot-reload; editor replacement does not.)
 *
 * Layout (kanagawa colors come from the live theme, hot-reload friendly):
 *
 *                                       <- pure air separates transcript
 *
 *   ❯ input text                        <- bare prompt, marker tracks the live
 *                                          border color (session accent / bash /
 *                                          python / thinking level)
 *
 *     model · effort · folder ·  git *n              ctx 42% · $cost
 *                                       <- quiet status, then trailing air
 *
 * Companion config (~/.omp/agent/config.yml):
 *   tui.chrome: plain            -> stock borderless composer + plain tool chrome
 *   statusLine.preset: custom
 *   statusLine.leftSegments: []  -> silences the built-in status line (this file
 *   statusLine.rightSegments: []    renders its own, below the input)
 */

import * as path from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";
import { CustomEditor } from "@oh-my-pi/pi-coding-agent/modes/components/custom-editor";
import { truncateToWidth } from "@oh-my-pi/pi-tui";

const GIT_TTL_MS = 3_000;
const CONTEXT_TTL_MS = 1_000;
const AMBIENT_REFRESH_MS = 30_000;

function width(text: string): number {
	return Bun.stringWidth(text, { countAnsiEscapeCodes: false });
}

function currentFolder(dir: string, home: string): string {
	if (dir === home) return "~";
	return path.basename(dir) || dir;
}


export default function (pi: ExtensionAPI) {
	// ── cached ambient data (renders must stay sync + O(1)) ────────────────
	let git: { branch: string; dirty: number } | undefined;
	let gitAt = 0;
	let gitInFlight = false;
	let ctxUsage: { tokens: number; contextWindow: number } | undefined;
	let ctxUsageAt = 0;
	let ambientTimer: Timer | undefined;

	function refreshGit(cwd: string): void {
		const now = Date.now();
		if (gitInFlight || now - gitAt < GIT_TTL_MS) return;
		gitInFlight = true;
		void (async () => {
			try {
				const [branch, status] = await Promise.all([
					pi.exec("git", ["-C", cwd, "branch", "--show-current"]),
					pi.exec("git", ["-C", cwd, "status", "--porcelain"]),
				]);
				const name = branch.stdout.trim();
				git = name
					? {
							branch: name,
							dirty: status.stdout.split("\n").filter(Boolean).length,
						}
					: undefined;
			} catch {
				git = undefined;
			} finally {
				gitAt = Date.now();
				gitInFlight = false;
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

		function statusLine(cols: number): string {
			const theme = ctx.ui.theme; // Re-read after live light/dark theme changes.
			refreshGit(ctx.cwd);
			const dot = theme.fg("statusLineSep", " · ");

			// left: identity + location
			const left: string[] = [];
			const model = ctx.models.current();
			if (model) {
				const name = model.name.startsWith("Claude ") ? model.name.slice(7) : model.name;
				left.push(
					`${theme.fg("statusLineModel", model.provider)}${theme.fg("statusLineSep", "/")}${theme.fg("statusLineModel", name)}`,
				);
				const level = pi.getThinkingLevel();
				if (level && level !== "off")
					left.push(theme.fg("statusLineContext", level));
			}
			left.push(theme.fg("statusLinePath", currentFolder(ctx.cwd, home)));
			if (git) {
				const branch = theme.fg("statusLinePath", ` ${git.branch}`);
				if (git.dirty > 0) {
					left.push(
						`${branch} ${theme.fg("statusLineGitDirty", `*${git.dirty}`)}`,
					);
				} else {
					left.push(branch);
				}
			}

			// right: only the two continuous meters that change decisions
			const right: string[] = [];
			const pct = contextPercent();
			if (pct !== undefined) {
				const color =
					pct >= 90 ? "error" : pct >= 70 ? "warning" : "statusLineContext";
				right.push(theme.fg(color, `ctx ${pct.toFixed(0)}%`));
			}
			const cost = ctx.sessionManager.getUsageStatistics?.().cost;
			if (cost) right.push(theme.fg("statusLineCost", `$${cost.toFixed(2)}`));

			// Assemble with a 2-col indent. Degrade right-to-left: cost,
			// context, git, folder, effort; provider/model identity survives.
			const assemble = (keepLeft: number, keepRight: number): string | undefined => {
				const leftText = `  ${left.slice(0, keepLeft).join(dot)}`;
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
			return truncateToWidth(`  ${left[0] ?? ""}`, cols);
		}

		class PromptspaceEditor extends CustomEditor {
			render(cols: number): readonly string[] {
				// Marker inherits the live border color: session accent, bash/python
				// mode, thinking level, focus-proxy faint all keep their signal.
				this.setPromptGutter(`${this.borderColor("❯")} `);
				const theme = ctx.ui.theme;
				const panelBg = (line: string): string =>
					theme.bg("userMessageBg", line);
				const inputLines = [
					panelBg(" ".repeat(cols)),
					...super.render(cols).map(panelBg),
					panelBg(" ".repeat(cols)),
				];
				return ["", "", ...inputLines, "", statusLine(cols), ""];
			}
		}

		ctx.ui.setEditorComponent((tui, editorTheme, keybindings) => {
			const editor = new PromptspaceEditor(tui, editorTheme, keybindings);
			editor.setBorderVisible(false);
			// Refresh cached git/context/cost values while the editor is idle.
			clearInterval(ambientTimer);
			ambientTimer = setInterval(() => tui.requestRender(), AMBIENT_REFRESH_MS);
			ambientTimer.unref?.();
			return editor;
		});
	});
}
