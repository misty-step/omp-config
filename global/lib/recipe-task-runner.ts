import { randomUUID } from "node:crypto";
import { realpathSync } from "node:fs";
import { rm } from "node:fs/promises";
import { homedir, tmpdir } from "node:os";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const RECIPE_LAUNCH_SCHEMA = "omp.recipe.launch.v1";
export const RECIPE_TASK_MAX_DEPTH = 4;

export interface RecipeTaskEvent {
	type: string;
	[key: string]: unknown;
}

export interface RecipeLaunchDescriptor {
	schemaVersion: typeof RECIPE_LAUNCH_SCHEMA;
	bundle: string;
	cwd: string;
	runtimeRoot: string;
	agentDir: string;
	home: string;
	sessionDir: string;
	model: {
		provider: string;
		id: string;
		reasoning: string;
	};
	env: Record<string, string>;
}

export interface RecipeTaskResult {
	text: string;
	runtimeRoot: string;
	sessionDir: string;
}

export interface RecipeTaskHandle {
	readonly descriptor: RecipeLaunchDescriptor;
	send(message: string): Promise<void>;
	wait(): Promise<RecipeTaskResult>;
	stop(): Promise<void>;
}

export interface StartRecipeTaskOptions {
	recipe: string;
	task: string;
	cwd: string;
	signal?: AbortSignal;
	onEvent?: (event: RecipeTaskEvent) => void;
	timeoutMs?: number;
	compilerPath?: string;
	pythonPath?: string;
	ompSourceRoot?: string;
	rpcClientModule?: string;
	cliPath?: string;
}

interface RpcClientToolContext {
	signal: AbortSignal;
	sendUpdate(update: string | { content: Array<{ type: "text"; text: string }> }): void;
}

interface RpcClientTool {
	name: string;
	label: string;
	description: string;
	loadMode: "essential";
	parameters: Record<string, unknown>;
	execute(params: Record<string, unknown>, context: RpcClientToolContext): Promise<string>;
}

interface RpcClientLike {
	start(): Promise<void>;
	stop(): Promise<void>;
	abort(): Promise<void>;
	prompt(message: string): Promise<void>;
	steer(message: string): Promise<void>;
	waitForIdle(timeout?: number): Promise<void>;
	getLastAssistantText(): Promise<string | null>;
	onSessionEvent(listener: (event: RecipeTaskEvent) => void): () => void;
}

interface RpcClientModule {
	RpcClient: new (options: Record<string, unknown>) => RpcClientLike;
	defineRpcClientTool?: (tool: RpcClientTool) => RpcClientTool;
}

const SAFE_PREPARE_ENV = [
	"PATH",
	"TMPDIR",
	"LANG",
	"LC_ALL",
	"TERM",
	"SSL_CERT_FILE",
	"SSL_CERT_DIR",
	"NO_PROXY",
] as const;

function sourceCompilerPath(): string {
	const sourceFile = realpathSync(fileURLToPath(import.meta.url));
	return resolve(dirname(sourceFile), "../../bin/omp_recipe.py");
}

function expandHome(path: string): string {
	if (path === "~") return homedir();
	return path.startsWith("~/") ? join(homedir(), path.slice(2)) : path;
}

function optionPath(value: string | undefined, fallback: string): string {
	return resolve(expandHome(value ?? fallback));
}


function importTarget(value: string): string {
	if (value.startsWith("file:") || (!isAbsolute(value) && !value.startsWith("."))) return value;
	return pathToFileURL(resolve(value)).href;
}

function requireString(value: unknown, label: string): string {
	if (typeof value !== "string" || value.length === 0) throw new Error(`${label} must be a non-empty string`);
	return value;
}

function parseDescriptor(value: unknown, expectedRuntimeRoot: string): RecipeLaunchDescriptor {
	if (typeof value !== "object" || value === null || Array.isArray(value)) {
		throw new Error("recipe preparation returned a non-object descriptor");
	}
	const raw = value as Record<string, unknown>;
	if (raw.schemaVersion !== RECIPE_LAUNCH_SCHEMA) {
		throw new Error(`recipe preparation returned unsupported schema ${String(raw.schemaVersion)}`);
	}
	if (typeof raw.model !== "object" || raw.model === null || Array.isArray(raw.model)) {
		throw new Error("recipe preparation returned an invalid model");
	}
	if (typeof raw.env !== "object" || raw.env === null || Array.isArray(raw.env)) {
		throw new Error("recipe preparation returned an invalid environment");
	}
	const env: Record<string, string> = {};
	for (const [key, entry] of Object.entries(raw.env as Record<string, unknown>)) {
		if (typeof entry !== "string") throw new Error(`recipe preparation returned a non-string environment value for ${key}`);
		env[key] = entry;
	}
	const modelRaw = raw.model as Record<string, unknown>;
	const descriptor: RecipeLaunchDescriptor = {
		schemaVersion: RECIPE_LAUNCH_SCHEMA,
		bundle: requireString(raw.bundle, "descriptor.bundle"),
		cwd: requireString(raw.cwd, "descriptor.cwd"),
		runtimeRoot: requireString(raw.runtimeRoot, "descriptor.runtimeRoot"),
		agentDir: requireString(raw.agentDir, "descriptor.agentDir"),
		home: requireString(raw.home, "descriptor.home"),
		sessionDir: requireString(raw.sessionDir, "descriptor.sessionDir"),
		model: {
			provider: requireString(modelRaw.provider, "descriptor.model.provider"),
			id: requireString(modelRaw.id, "descriptor.model.id"),
			reasoning: requireString(modelRaw.reasoning, "descriptor.model.reasoning"),
		},
		env,
	};
	if (realpathSync(descriptor.runtimeRoot) !== realpathSync(expectedRuntimeRoot)) {
		throw new Error("recipe preparation changed the caller-supplied runtime root");
	}
	return descriptor;
}

function prepareEnvironment(): Record<string, string> {
	const env: Record<string, string> = {};
	for (const key of SAFE_PREPARE_ENV) {
		const value = process.env[key];
		if (value !== undefined) env[key] = value;
	}
	return env;
}

async function prepareLaunch(
	bundle: string,
	cwd: string,
	runtimeRoot: string,
	compilerPath: string,
	pythonPath: string,
	signal?: AbortSignal,
): Promise<RecipeLaunchDescriptor> {
	if (signal?.aborted) throw signal.reason ?? new Error("recipe task cancelled before preparation");
	const child = Bun.spawn(
		[
			pythonPath,
			compilerPath,
			"prepare-runtime",
			"--bundle",
			bundle,
			"--cwd",
			cwd,
			"--runtime-root",
			runtimeRoot,
		],
		{ env: prepareEnvironment(), stdout: "pipe", stderr: "pipe" },
	);
	const abort = (): void => child.kill();
	signal?.addEventListener("abort", abort, { once: true });
	try {
		const [stdout, stderr, exitCode] = await Promise.all([
			new Response(child.stdout).text(),
			new Response(child.stderr).text(),
			child.exited,
		]);
		if (signal?.aborted) throw signal.reason ?? new Error("recipe task cancelled during preparation");
		if (exitCode !== 0) throw new Error(`recipe preparation failed (${exitCode}): ${stderr.trim()}`);
		let parsed: unknown;
		try {
			parsed = JSON.parse(stdout);
		} catch (error) {
			throw new Error("recipe preparation returned invalid JSON", { cause: error });
		}
		return parseDescriptor(parsed, runtimeRoot);
	} finally {
		signal?.removeEventListener("abort", abort);
	}
}

async function loadRpcClientModule(path: string): Promise<RpcClientModule> {
	// The deployment selects either the local source RpcClient or an installed module at runtime.
	const loaded = (await import(importTarget(path))) as Partial<RpcClientModule>;
	if (typeof loaded.RpcClient !== "function") throw new Error(`RPC client module does not export RpcClient: ${path}`);
	return loaded as RpcClientModule;
}

export function recipeTaskProgress(event: RecipeTaskEvent): string | undefined {
	if (event.type === "message_update") {
		const update = event.assistantMessageEvent;
		if (typeof update === "object" && update !== null) {
			const raw = update as Record<string, unknown>;
			if ((raw.type === "text_delta" || raw.type === "thinking_delta") && typeof raw.delta === "string") {
				return raw.delta;
			}
		}
	}
	if (event.type === "tool_execution_start" && typeof event.toolName === "string") {
		return `\n[${event.toolName}]\n`;
	}
	return undefined;
}

async function cleanupRuntimeRoot(runtimeRoot: string): Promise<void> {
	await rm(runtimeRoot, { recursive: true, force: true });
}

export async function startRecipeTask(options: StartRecipeTaskOptions): Promise<RecipeTaskHandle> {
	return startRecipeTaskAtDepth(options, 0);
}

async function startRecipeTaskAtDepth(options: StartRecipeTaskOptions, depth: number): Promise<RecipeTaskHandle> {
	const cwd = resolve(options.cwd);
	const bundle = resolve(cwd, options.recipe);
	const runtimeRoot = join(tmpdir(), `omp-recipe-task-${randomUUID()}`);
	const compilerPath = optionPath(options.compilerPath ?? process.env.OMP_RECIPE_COMPILER, sourceCompilerPath());
	const pythonPath = options.pythonPath ?? process.env.OMP_RECIPE_PYTHON ?? "/usr/bin/python3";
	const ompSourceRoot = optionPath(
		options.ompSourceRoot ?? process.env.OMP_RECIPE_OMP_SOURCE,
		join(homedir(), "Development/oh-my-pi"),
	);
	const rpcClientModule =
		options.rpcClientModule ??
		process.env.OMP_RECIPE_RPC_CLIENT_MODULE ??
		join(ompSourceRoot, "packages/coding-agent/src/modes/rpc/rpc-client.ts");
	const cliPath = optionPath(
		options.cliPath ?? process.env.OMP_RECIPE_CLI_PATH,
		join(ompSourceRoot, "packages/coding-agent/src/cli.ts"),
	);
	let descriptor: RecipeLaunchDescriptor | undefined;
	try {
		descriptor = await prepareLaunch(bundle, cwd, runtimeRoot, compilerPath, pythonPath, options.signal);
		return await startPreparedRecipeTask(options, depth, descriptor, rpcClientModule, cliPath);
	} catch (error) {
		try {
			await cleanupRuntimeRoot(descriptor?.runtimeRoot ?? runtimeRoot);
		} catch (cleanupError) {
			throw new AggregateError([error, cleanupError], "recipe task failed and its runtime root could not be removed");
		}
		throw error;
	}
}

async function startPreparedRecipeTask(
	options: StartRecipeTaskOptions,
	depth: number,
	descriptor: RecipeLaunchDescriptor,
	rpcClientModule: string,
	cliPath: string,
): Promise<RecipeTaskHandle> {
	const rpc = await loadRpcClientModule(rpcClientModule);
	const nestedTool: RpcClientTool = {
		name: "recipe_task",
		label: "Recipe Task",
		description: "Run a task in a fresh sibling OMP process prepared from a compiled omp.recipe.v1 bundle.",
		loadMode: "essential",
		parameters: {
			type: "object",
			properties: {
				recipe: { type: "string", minLength: 1, description: "Compiled recipe path, relative to the caller cwd." },
				task: { type: "string", minLength: 1, description: "Task for the fresh recipe process." },
			},
			required: ["recipe", "task"],
			additionalProperties: false,
		},
		async execute(params, context): Promise<string> {
			if (depth >= RECIPE_TASK_MAX_DEPTH) {
				throw new Error(`recipe_task maximum nesting depth ${RECIPE_TASK_MAX_DEPTH} exceeded`);
			}
			const recipe = requireString(params.recipe, "recipe_task.recipe");
			const task = requireString(params.task, "recipe_task.task");
			let streamed = "";
			const nested = await startRecipeTaskAtDepth(
				{
					...options,
					recipe,
					task,
					cwd: descriptor.cwd,
					signal: context.signal,
					onEvent(event) {
						const progress = recipeTaskProgress(event);
						if (progress) {
							streamed += progress;
							context.sendUpdate({ content: [{ type: "text", text: streamed }] });
						}
					},
				},
				depth + 1,
			);
			try {
				return (await nested.wait()).text;
			} finally {
				await nested.stop();
			}
		},
	};
	const customTool = rpc.defineRpcClientTool ? rpc.defineRpcClientTool(nestedTool) : nestedTool;
	const client = new rpc.RpcClient({
		cliPath,
		cwd: descriptor.cwd,
		env: descriptor.env,
		envMode: "replace",
		provider: descriptor.model.provider,
		model: descriptor.model.id,
		sessionDir: descriptor.sessionDir,
		args: ["--thinking", descriptor.model.reasoning],
		customTools: [customTool],
	});

	let started = false;
	let stopped = false;
	let stopPromise: Promise<void> | undefined;
	let completion: Promise<void> | undefined;
	let waitPromise: Promise<RecipeTaskResult> | undefined;
	const unsubscribe = client.onSessionEvent(event => options.onEvent?.(event));

	const shutdown = (abortFirst: boolean): Promise<void> => {
		if (stopPromise) return stopPromise;
		stopped = true;
		stopPromise = (async () => {
			try {
				if (abortFirst && started) await client.abort().catch(() => {});
				await client.stop();
			} finally {
				unsubscribe();
				await cleanupRuntimeRoot(descriptor.runtimeRoot);
			}
		})();
		return stopPromise;
	};
	const cancel = (): void => {
		void shutdown(true);
	};
	options.signal?.addEventListener("abort", cancel, { once: true });

	try {
		await client.start();
		started = true;
		if (options.signal?.aborted) {
			await shutdown(true);
			throw options.signal.reason ?? new Error("recipe task cancelled during start");
		}
		completion = client.waitForIdle(options.timeoutMs ?? 30 * 60_000);
		await client.prompt(options.task);
	} catch (error) {
		await shutdown(started);
		options.signal?.removeEventListener("abort", cancel);
		throw error;
	}

	return {
		descriptor,
		async send(message: string): Promise<void> {
			if (stopped) throw new Error("recipe task is stopped");
			await client.steer(requireString(message, "steering message"));
		},
		wait(): Promise<RecipeTaskResult> {
			if (!waitPromise) {
				waitPromise = (async () => {
					try {
						await completion;
						const text = (await client.getLastAssistantText()) ?? "";
						return { text, runtimeRoot: descriptor.runtimeRoot, sessionDir: descriptor.sessionDir };
					} finally {
						await shutdown(false);
						options.signal?.removeEventListener("abort", cancel);
					}
				})();
			}
			return waitPromise;
		},
		async stop(): Promise<void> {
			await shutdown(true);
			options.signal?.removeEventListener("abort", cancel);
		},
	};
}
