import type { ExtensionAPI, ExtensionCommandContext, ExtensionContext } from "@oh-my-pi/pi-coding-agent";
import {
	discoverAgents,
	TASK_SUBAGENT_LIFECYCLE_CHANNEL,
	TASK_SUBAGENT_PROGRESS_CHANNEL,
} from "@oh-my-pi/pi-coding-agent/task";
import type {
	AgentDefinition,
	AgentProgress,
	SubagentLifecyclePayload,
	SubagentProgressPayload,
} from "@oh-my-pi/pi-coding-agent/task";
import { matchesKey, truncateToWidth, visibleWidth, wrapTextWithAnsi } from "@oh-my-pi/pi-tui";

interface HubAgent {
	id: string;
	agent: string;
	agentSource: string;
	description?: string;
	status: "started" | "running" | "completed" | "failed" | "aborted";
	parentToolCallId?: string;
	sessionFile?: string;
	progress?: AgentProgress;
	updatedAt: number;
}

const THINKING_LEVELS: Record<string, true> = {
	off: true,
	minimal: true,
	low: true,
	medium: true,
	high: true,
	xhigh: true,
	max: true,
};

function statusGlyph(status: HubAgent["status"]): string {
	if (status === "completed") return "✓";
	if (status === "failed" || status === "aborted") return "×";
	return status === "running" ? "●" : "○";
}

function splitModel(selector: string | undefined, definition: AgentDefinition | undefined): {
	provider: string;
	model: string;
	effort: string;
} {
	let value = selector ?? definition?.model?.[0] ?? "unresolved";
	let effort = definition?.thinkingLevel ?? "auto";
	const colon = value.lastIndexOf(":");
	if (colon > value.indexOf("/") && THINKING_LEVELS[value.slice(colon + 1)]) {
		effort = value.slice(colon + 1) as typeof effort;
		value = value.slice(0, colon);
	}
	const slash = value.indexOf("/");
	return slash < 0
		? { provider: "unknown", model: value, effort }
		: { provider: value.slice(0, slash), model: value.slice(slash + 1), effort };
}

function list(values: readonly string[] | undefined, empty = "none"): string {
	return values?.length ? values.join(", ") : empty;
}

function pad(line: string, width: number): string {
	const clipped = truncateToWidth(line, width);
	return clipped + " ".repeat(Math.max(0, width - visibleWidth(clipped)));
}

export default function (pi: ExtensionAPI): void {
	const agents = new Map<string, HubAgent>();
	let definitions = new Map<string, AgentDefinition>();
	let subscribed = false;
	let overlayTui: { requestRender(): void } | undefined;

	const update = (agent: HubAgent): void => {
		agents.set(agent.id, agent);
		overlayTui?.requestRender();
	};

	const subscribe = (): void => {
		if (subscribed) return;
		subscribed = true;
		pi.events.on(TASK_SUBAGENT_LIFECYCLE_CHANNEL, data => {
			const event = data as SubagentLifecyclePayload;
			const prior = agents.get(event.id);
			update({
				id: event.id,
				agent: event.agent,
				agentSource: event.agentSource,
				description: event.description ?? prior?.description,
				status: event.status,
				parentToolCallId: event.parentToolCallId,
				sessionFile: event.sessionFile,
				progress: prior?.progress,
				updatedAt: Date.now(),
			});
		});
		pi.events.on(TASK_SUBAGENT_PROGRESS_CHANNEL, data => {
			const event = data as SubagentProgressPayload;
			const progress = event.progress;
			const prior = agents.get(progress.id);
			update({
				id: progress.id,
				agent: event.agent,
				agentSource: event.agentSource,
				description: progress.description ?? prior?.description,
				status: progress.status === "pending" ? "started" : progress.status,
				parentToolCallId: event.parentToolCallId,
				sessionFile: event.sessionFile,
				progress,
				updatedAt: Date.now(),
			});
		});
	};

	pi.on("session_start", async (_event, ctx: ExtensionContext) => {
		if (!ctx.hasUI) return;
		agents.clear();
		subscribe();
		const discovered = await discoverAgents(ctx.cwd);
		definitions = new Map(discovered.agents.map(agent => [agent.name, agent]));
	});

	async function showHub(ctx: ExtensionCommandContext): Promise<void> {
		if (!ctx.hasUI) return;
		const ordered = (): HubAgent[] =>
			[...agents.values()].sort((a, b) => {
				const activeA = a.status === "running" || a.status === "started" ? 0 : 1;
				const activeB = b.status === "running" || b.status === "started" ? 0 : 1;
				return activeA - activeB || a.updatedAt - b.updatedAt;
			});
		if (ordered().length === 0) {
			ctx.ui.notify("Agent Hub has no subagent activity in this session.", "info");
			return;
		}

		await ctx.ui.custom<void>(
			(tui, theme, _keybindings, done) => {
				overlayTui = tui;
				let selected = 0;
				let detailScroll = 0;

				const detailLines = (agent: HubAgent, width: number): string[] => {
					const progress = agent.progress;
					const definition = definitions.get(agent.agent);
					const route = splitModel(progress?.resolvedModel, definition);
					const heading = (label: string): string => theme.fg("accent", label.toUpperCase());
					const value = (label: string, text: string): string =>
						`${theme.fg("dim", `${label.padEnd(10)} `)}${text}`;
					const wrappedValue = (label: string, text: string): string[] => {
						const prefix = theme.fg("dim", `${label.padEnd(10)} `);
						const continuation = " ".repeat(11);
						const wrapped = wrapTextWithAnsi(text, Math.max(12, width - 11));
						return wrapped.map((line, index) => `${index === 0 ? prefix : continuation}${line}`);
					};
					const lines = [
						heading("identity / route"),
						value("agent", `${agent.agent} · ${agent.agentSource}`),
						value(
							"model",
							`${theme.fg("statusLineModel", route.provider)}/${theme.fg("statusLineModel", route.model)} · ${theme.fg("statusLineContext", route.effort)}`,
						),
						value("state", `${agent.status}${agent.parentToolCallId ? " · nested" : " · root"}`),
						"",
						heading("declared composition"),
						...wrappedValue("models", list(definition?.model)),
						...wrappedValue("tools", list(definition?.tools, "default toolset")),
						...wrappedValue("skills", list(definition?.autoloadSkills)),
						...wrappedValue("spawns", definition?.spawns === "*" ? "any" : list(definition?.spawns)),
						...wrappedValue(
							"policies",
							`read=${definition?.readSummarize === false ? "verbatim" : "summarized"} · prewalk=${definition?.prewalk ?? "off"}`,
						),
						"",
						heading("live state"),
						value("activity", progress?.lastIntent ?? progress?.currentTool ?? "waiting for progress"),
						value(
							"usage",
							`${progress?.requests ?? 0} req · ${progress?.tokens ?? 0} tok · $${(progress?.cost ?? 0).toFixed(4)}`,
						),
					];
					if (progress?.currentTool) lines.push(value("tool", `${progress.currentTool} ${progress.currentToolArgs ?? ""}`));
					if (progress?.retryState) {
						lines.push(theme.fg("warning", `retry ${progress.retryState.attempt}/${progress.retryState.maxAttempts}: ${progress.retryState.errorMessage}`));
					}
					lines.push("", heading("dispatched prompt"));
					const prompt = progress?.assignment ?? progress?.task ?? agent.description ?? "unavailable";
					for (const paragraph of prompt.split("\n")) {
						lines.push(...wrapTextWithAnsi(paragraph || " ", Math.max(12, width)));
					}
					return lines;
				};

				return {
					render(width: number): readonly string[] {
						const entries = ordered();
						if (selected >= entries.length) selected = Math.max(0, entries.length - 1);
						const current = entries[selected];
						if (!current) return [theme.fg("dim", "Agent Hub · no activity")];
						const rows = Math.max(12, (process.stdout.rows ?? 30) - 4);
						const header = `${theme.fg("accent", "Agent Hub")} ${theme.fg("dim", `· ${entries.length} session agent${entries.length === 1 ? "" : "s"}`)}`;
						const footer = theme.fg("dim", "↑↓ select · pgup/pgdn prompt · esc close");

						if (width < 90) {
							const rosterHeight = Math.min(5, entries.length);
							const start = Math.max(0, Math.min(selected - rosterHeight + 1, entries.length - rosterHeight));
							const roster = entries.slice(start, start + rosterHeight).map((entry, offset) => {
								const index = start + offset;
								const marker = index === selected ? theme.fg("accent", "›") : " ";
								return truncateToWidth(`${marker} ${statusGlyph(entry.status)} ${entry.id} · ${entry.description ?? entry.agent}`, width);
							});
							const available = Math.max(4, rows - roster.length - 3);
							const details = detailLines(current, width - 2);
							const maxScroll = Math.max(0, details.length - available);
							detailScroll = Math.min(detailScroll, maxScroll);
							return [header, ...roster, theme.fg("dim", "─".repeat(width)), ...details.slice(detailScroll, detailScroll + available), footer];
						}

						const leftWidth = Math.max(28, Math.floor(width * 0.34));
						const rightWidth = width - leftWidth - 3;
						const details = detailLines(current, rightWidth);
						const bodyHeight = rows - 2;
						const maxScroll = Math.max(0, details.length - bodyHeight);
						detailScroll = Math.min(detailScroll, maxScroll);
						const lines = [header];
						for (let row = 0; row < bodyHeight; row++) {
							const entry = entries[row];
							const left = entry
								? `${row === selected ? theme.fg("accent", "›") : " "} ${statusGlyph(entry.status)} ${entry.id} · ${entry.description ?? entry.agent}`
								: "";
							const right = details[detailScroll + row] ?? "";
							lines.push(`${pad(left, leftWidth)}${theme.fg("dim", " │ ")}${truncateToWidth(right, rightWidth)}`);
						}
						lines.push(footer);
						return lines;
					},
					handleInput(data: string): void {
						const entries = ordered();
						if (matchesKey(data, "escape") || matchesKey(data, "esc") || data === "q") {
							done(undefined);
							return;
						}
						if (matchesKey(data, "up") || data === "k") {
							selected = Math.max(0, selected - 1);
							detailScroll = 0;
						} else if (matchesKey(data, "down") || data === "j") {
							selected = Math.min(entries.length - 1, selected + 1);
							detailScroll = 0;
						} else if (matchesKey(data, "pageUp")) {
							detailScroll = Math.max(0, detailScroll - 8);
						} else if (matchesKey(data, "pageDown")) {
							detailScroll += 8;
						}
						tui.requestRender();
					},
					invalidate(): void {},
					dispose(): void {
						overlayTui = undefined;
					},
				};
			},
			{ overlay: true },
		);
	}

	pi.registerCommand("agent-hub", {
		description: "Open Agent Hub for subagent routes, prompts, and composition",
		handler: async (_args, ctx) => showHub(ctx),
	});
}
