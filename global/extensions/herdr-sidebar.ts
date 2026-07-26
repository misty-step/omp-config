/**
 * herdr-sidebar.ts — report lane identity to herdr sidebar via custom tokens.
 *
 * Auto-discovered from ~/.omp/agent/extensions/ at startup.
 * Requires herdr 0.7.5+ with $model and $summary tokens in sidebar config.
 *
 * On session_start, if running inside herdr (HERDR_PANE_ID set), reports:
 *   --token model=<provider/name:effort>
 *   --token summary=<repo|task one-liner>
 */

import { spawn } from "node:child_process";
import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";

function runHercli(args: string[]): Promise<void> {
	const socket = process.env.HERDR_SOCKET_PATH;
	if (!socket) return Promise.resolve();
	const { promise, resolve } = Promise.withResolvers<void>();
	const child = spawn("herdr", ["--socket", socket, ...args], {
		stdio: "ignore",
	});
	child.on("exit", resolve);
	child.on("error", resolve);
	return promise;
}

function shortRepo(cwd: string): string {
	const home = process.env.HOME ?? "";
	let rel = cwd;
	if (cwd.startsWith(home)) rel = "~" + cwd.slice(home.length);
	const parts = rel.split("/").filter(Boolean);
	if (parts.length <= 2) return rel;
	return "…/" + parts.slice(-2).join("/");
}

export default function (pi: ExtensionAPI): void {
	pi.on("session_start", async (_event, ctx: ExtensionContext) => {
		const paneId = process.env.HERDR_PANE_ID;
		if (!paneId) return; // not running inside herdr

		// Model identity
		const model = ctx.models.current();
		let modelToken = "unknown";
		if (model) {
			const name = model.name.startsWith("Claude ") ? model.name.slice(7) : model.name;
			modelToken = `${model.provider}/${name}`;
			const level = pi.getThinkingLevel?.();
			if (level && level !== "off" && level !== "auto") modelToken += `:${level}`;
		}

		// One-line summary: repo + first task hint
		const summary = shortRepo(ctx.cwd);

		// Report to herdr sidebar tokens
		await runHercli([
			"pane",
			"report-metadata",
			paneId,
			"--source",
			"omp-extension",
			"--token",
			`model=${modelToken}`,
			"--token",
			`summary=${summary}`,
		]);
	});
}
