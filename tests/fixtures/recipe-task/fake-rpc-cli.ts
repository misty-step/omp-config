#!/usr/bin/env bun
import { appendFileSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import * as readline from "node:readline";

const agentDir = process.env.PI_CODING_AGENT_DIR;
if (!agentDir) throw new Error("PI_CODING_AGENT_DIR is required");
const pidFile = join(agentDir, "child.pid");
const logFile = join(agentDir, "fixture-state.jsonl");
const skillsDir = join(agentDir, "skills");
const skills = readdirSync(skillsDir, { withFileTypes: true })
	.filter(entry => entry.isDirectory())
	.map(entry => entry.name)
	.sort();
const instructions = readFileSync(join(agentDir, "AGENTS.md"), "utf8").trim();
writeFileSync(pidFile, `${process.pid}\n`);
appendFileSync(
	logFile,
	`${JSON.stringify({
		type: "started",
		pid: process.pid,
		agentDir,
		sessionDir: process.argv[process.argv.indexOf("--session-dir") + 1],
		parentMarker: process.env.OMP_RECIPE_PARENT_ONLY ?? null,
		instructions,
		skills,
	})}\n`,
);

let lastText = "";
let waitingForSteer = false;
let waitingForNested = false;

function send(frame: unknown): void {
	process.stdout.write(`${JSON.stringify(frame)}\n`);
}

function finish(text: string): void {
	lastText = text;
	send({
		type: "message_update",
		message: { role: "assistant", content: [{ type: "text", text }], timestamp: Date.now() },
		assistantMessageEvent: { type: "text_delta", delta: text },
	});
	send({ type: "agent_end", messages: [] });
}

function marker(): string {
	return `pid=${process.pid};agent=${agentDir};instructions=${instructions};skills=${skills.join(",")};parent=${process.env.OMP_RECIPE_PARENT_ONLY ?? "absent"}`;
}

function cleanup(): void {
	try {
		rmSync(pidFile);
	} catch {}
}

process.on("SIGTERM", () => {
	cleanup();
	process.exit(0);
});
process.on("SIGINT", () => {
	cleanup();
	process.exit(0);
});
process.on("exit", cleanup);

send({ type: "ready" });
const lines = readline.createInterface({ input: process.stdin, terminal: false });
lines.on("line", line => {
	const frame = JSON.parse(line) as Record<string, unknown>;
	const id = frame.id;
	const type = frame.type;
	if (type === "set_host_tools") {
		const tools = (frame.tools as Array<{ name: string }>).map(tool => tool.name);
		appendFileSync(logFile, `${JSON.stringify({ type: "host_tools", tools })}\n`);
		send({ type: "response", id, command: type, success: true, data: { toolNames: tools } });
		return;
	}
	if (type === "prompt") {
		send({ type: "response", id, command: type, success: true, data: {} });
		const message = String(frame.message);
		if (message.startsWith("HOLD")) {
			waitingForSteer = true;
			return;
		}
		if (message.startsWith("NEST ")) {
			const [recipe, ...task] = message.slice(5).split(" ");
			waitingForNested = true;
			send({
				type: "host_tool_call",
				id: "nested-request",
				toolCallId: "nested-call",
				toolName: "recipe_task",
				arguments: { recipe, task: task.join(" ") },
			});
			return;
		}
		setTimeout(() => finish(marker()), 10);
		return;
	}
	if (type === "steer") {
		appendFileSync(logFile, `${JSON.stringify({ type: "steer", message: frame.message })}\n`);
		send({ type: "response", id, command: type, success: true, data: {} });
		if (waitingForSteer) {
			waitingForSteer = false;
			finish(`${marker()};steer=${String(frame.message)}`);
		}
		return;
	}
	if (type === "abort") {
		appendFileSync(logFile, `${JSON.stringify({ type: "abort" })}\n`);
		send({ type: "response", id, command: type, success: true, data: {} });
		return;
	}
	if (type === "get_last_assistant_text") {
		send({ type: "response", id, command: type, success: true, data: { text: lastText } });
		return;
	}
	if (type === "host_tool_update") return;
	if (type === "host_tool_result" && waitingForNested) {
		waitingForNested = false;
		const result = frame.result as { content?: Array<{ type: string; text?: string }> };
		const nested = result.content?.filter(item => item.type === "text").map(item => item.text ?? "").join("") ?? "";
		finish(`${marker()};nested=[${nested}]`);
		return;
	}
	send({ type: "response", id, command: String(type), success: true, data: {} });
});
