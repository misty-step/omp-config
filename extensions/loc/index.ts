import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import {
	analyzeRepo,
	formatLocReport,
	formatTrendReport,
	getCommitDeltas,
	getTrendPoints,
	readLocCache,
	topLanguages,
	type CommitDelta,
	type LocStats,
} from "./analyze.ts";

const RESULT_TYPE = "loc/report";

function formatNumber(value: number): string {
	return value.toLocaleString("en-US");
}

function formatNativeStatusLine(
	stats: LocStats,
	lastDelta: CommitDelta | undefined,
	theme: ExtensionContext["ui"]["theme"],
): string {
	// setStatus trims ordinary leading whitespace; U+2800 retains one blank terminal cell.
	const statusIndent = "\u2800";
	const separator = theme.fg("dim", ` ${theme.sep.dot} `);
	const parts = [
		statusIndent,
		theme.fg("accent", theme.cmd.stats),
		` ${theme.bold(formatNumber(stats.code))}`,
		theme.fg("dim", " lines"),
		separator,
		formatNumber(stats.files),
		theme.fg("dim", " files"),
	];
	const [top] = topLanguages(stats, 1);
	if (top) {
		const icon = theme.getLangIconStyled(top[0]);
		parts.push(
			separator,
			icon ? `${icon} ` : "",
			top[0],
			theme.fg("muted", ` ${formatNumber(top[1].code)}`),
		);
	}
	if (lastDelta) {
		const delta = `${lastDelta.net >= 0 ? "+" : ""}${formatNumber(lastDelta.net)}`;
		parts.push(
			separator,
			theme.fg("dim", "Δ "),
			theme.fg(lastDelta.net === 0 ? "muted" : "accent", delta),
		);
	}
	return parts.join("");
}

function sendText(pi: ExtensionAPI, text: string): void {
	pi.sendMessage({ customType: RESULT_TYPE, content: text, display: true });
}

async function resolveStats(ctx: ExtensionContext): Promise<LocStats> {
	const cached = readLocCache(ctx.cwd);
	if (cached) return cached;
	return analyzeRepo(ctx.cwd);
}

async function refreshStatus(ctx: ExtensionContext, stats?: LocStats): Promise<void> {
	if (!ctx.hasUI) return;
	const resolved = stats ?? readLocCache(ctx.cwd) ?? (await analyzeRepo(ctx.cwd));
	if (!resolved) return;
	const [lastDelta] = getCommitDeltas(ctx.cwd, 1);
	ctx.ui.setStatus("loc", formatNativeStatusLine(resolved, lastDelta, ctx.ui.theme));
}

export default function registerLocExtension(pi: ExtensionAPI): void {
	pi.registerCommand("loc", {
		description: "Show codebase LOC totals, language breakdown, and recent commit deltas",
		handler: async (_args, ctx) => {
			if (ctx.hasUI) ctx.ui.setStatus("loc", "Counting lines…");
			try {
				const stats = await resolveStats(ctx);
				const deltas = getCommitDeltas(ctx.cwd, 8);
				sendText(pi, formatLocReport(stats, deltas));
				await refreshStatus(ctx, stats);
			} catch (error) {
				ctx.ui.notify(error instanceof Error ? error.message : String(error), "error");
			}
		},
	});

	pi.registerCommand("loc-trend", {
		description: "Show a concise LOC trend across recent git tags or commits",
		getArgumentCompletions: (prefix) => {
			const trimmed = prefix.trim();
			if (!trimmed || /^\d+$/.test(trimmed)) {
				return [
					{ value: "5", label: "last 5 points" },
					{ value: "8", label: "last 8 points" },
					{ value: "10", label: "last 10 points" },
				];
			}
			return null;
		},
		handler: async (args, ctx) => {
			const count = Math.min(20, Math.max(3, Number(args.trim()) || 6));
			if (ctx.hasUI) ctx.ui.setStatus("loc", "Building trend…");
			try {
				sendText(pi, formatTrendReport(getTrendPoints(ctx.cwd, count)));
			} catch (error) {
				ctx.ui.notify(error instanceof Error ? error.message : String(error), "error");
			} finally {
				await refreshStatus(ctx);
			}
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		await refreshStatus(ctx);
	});

	pi.on("turn_end", async (_event, ctx) => {
		await refreshStatus(ctx);
	});

	pi.on("session_shutdown", (_event, ctx) => {
		if (!ctx.hasUI) return;
		try {
			ctx.ui.setStatus("loc", undefined);
		} catch {
			// Extension context may already be inactive during shutdown.
		}
	});
}
