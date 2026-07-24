import { chmod, cp, mkdir, readdir, readFile, realpath, rm, stat, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { runnerTerminalSchema, shaSchema, stageNameSchema, type RunnerTerminal, type StageName } from "./contracts.js";

const adapterInputSchema = z.object({
  recipe: z.string().min(1),
  task: z.string().min(1),
  cwd: z.string().min(1),
  stage: stageNameSchema,
  round: z.coerce.number().int().min(1),
  headSha: shaSchema,
}).strict();

const taskSkillSchema = z.object({ name: z.string().min(1), path: z.string().min(1) }).strict();
// The compiled bundle's `recipe.json` (bin/omp_recipe.py's RECIPE_FILE) carries
// fields this adapter never needs (instructions, models, the parent's own
// `skills`, mcpServers); only `taskSkills` is read here, so every other
// field passes through unchecked rather than being re-validated.
const recipeManifestSchema = z.object({ taskSkills: z.array(taskSkillSchema) }).passthrough();

type AdapterInput = z.infer<typeof adapterInputSchema>;
type RecipeTaskHostTool = {
  name: string;
  label: string;
  description: string;
  loadMode: "essential";
  parameters: Record<string, unknown>;
  execute(params: Record<string, unknown>, context: {
    signal: AbortSignal;
    sendUpdate(update: string | { content: Array<{ type: "text"; text: string }> }): void;
  }): Promise<string>;
};
type RecipeTaskHandle = {
  wait(): Promise<{ text: string }>;
  stop(): Promise<void>;
};
type RecipeLaunchDescriptor = {
  cwd: string;
  agentDir: string;
  home: string;
  runtimeRoot: string;
  // Compiled recipe root (contains `recipe.json`). Carried on the real
  // descriptor built by global/lib/recipe-task-runner.ts's parseDescriptor;
  // declared here so stageLiveTaskProjection can read the recipe's
  // declared `taskSkills` allowlist.
  bundle: string;
  model: {
    provider: string;
    id: string;
    reasoning: string;
  };
};
type StartRecipeTask = (options: {
  recipe: string;
  task: string;
  cwd: string;
  signal: AbortSignal;
  timeoutMs: number;
  hostTools: RecipeTaskHostTool[];
  beforeStart?: (descriptor: RecipeLaunchDescriptor) => Promise<void>;
  onPrepared?: (descriptor: RecipeLaunchDescriptor) => Promise<void>;
}) => Promise<RecipeTaskHandle>;

// Bounds a single recipe-agent attempt so one hung or slow-to-converge model
// call cannot occupy an invokeRunnerWithRetry attempt indefinitely. A timeout
// rejects `handle.wait()` with a plain Error, which the adapter's own exit
// classification below treats as transient (exit 70) and therefore retryable
// up to invokeRunnerWithRetry's bounded attempt cap — the same outcome as any
// other transient stage failure, not a hang.
const stageTimeoutMs = 8 * 60_000;
const terminalToolParameters = z.toJSONSchema(runnerTerminalSchema) as Record<string, unknown>;

// Live Task projection matters only for a stage whose OWN instructions spawn
// Task children needing a skill beyond the parent's — a stage's own agent
// already gets its declared `skills` baked into `agentDir` at compile time
// (bin/omp_recipe.py's `_replace_runtime_agent`), no projection required.
// `adversarial_review` spawns `code-critic` children with an injected lens;
// `live_verify` already relied on this. Every other stage — including
// `remediate`, whose fixer reads a skill itself as the parent agent via its
// own `skills` declaration — spawns no Task child and stays ungated.
const liveTaskProjectionStages: Partial<Record<StageName, true>> = {
  live_verify: true,
  adversarial_review: true,
};

const flagToField: Record<string, keyof AdapterInput> = {
  "--recipe": "recipe",
  "--task": "task",
  "--cwd": "cwd",
  "--stage": "stage",
  "--round": "round",
  "--head-sha": "headSha",
};

export function parseAdapterInput(argv: string[]): AdapterInput {
  const values: Partial<Record<keyof AdapterInput, string>> = {};
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    const field = flag === undefined ? undefined : flagToField[flag];
    if (!field || value === undefined) {
      throw new Error(`invalid Hatchet runner arguments near ${flag ?? "end of input"}`);
    }
    if (values[field] !== undefined) {
      throw new Error(`duplicate Hatchet runner argument ${flag}`);
    }
    values[field] = value;
  }
  return adapterInputSchema.parse(values);
}


// Copies `source` into `target` as a frozen point-in-time snapshot: regular
// files are chmod'd read-only so neither the staged child process nor a
// later source mutation can alter what Task discovery sees. Directories keep
// their write bit so `cleanupRuntimeRoot`'s recursive `rm` can still unlink
// entries. `target`'s parent is created as needed since the runtime `home`
// starts as an empty directory with no `.omp/agent` tree yet.
async function copyImmutableSnapshot(source: string, target: string): Promise<void> {
  const resolvedSource = await realpath(source);
  if (!(await stat(resolvedSource)).isDirectory()) {
    throw new Error(`live Task projection source is not a directory: ${source}`);
  }
  await rm(target, { recursive: true, force: true });
  await mkdir(dirname(target), { recursive: true });
  await cp(resolvedSource, target, { recursive: true, dereference: true });
  await freezeFiles(target);
}

async function freezeFiles(root: string): Promise<void> {
  const entries = await readdir(root, { withFileTypes: true });
  await Promise.all(entries.map(async entry => {
    const entryPath = join(root, entry.name);
    if (entry.isDirectory()) await freezeFiles(entryPath);
    else if (entry.isFile()) await chmod(entryPath, 0o444);
  }));
}

export async function stageLiveTaskProjection(descriptor: RecipeLaunchDescriptor): Promise<void> {
  const preservedPaths = ["AGENTS.md", "config.yml", "models.yml"]
    .map(name => join(descriptor.agentDir, name));
  const preservedContent = await Promise.all(preservedPaths.map(path => readFile(path)));
  const preservedModel = JSON.stringify(descriptor.model);

  // User-level agent discovery reads `$HOME/.omp/agent/agents` (see
  // oh-my-pi task/discovery.ts `discoverAgents` + config.ts
  // `USER_CONFIG_BASES`), independent of `PI_CODING_AGENT_DIR`. The isolated
  // recipe HOME is `descriptor.home`, not `descriptor.agentDir` — staging the
  // catalog under `agentDir/agents` (the old symlink target) never reaches
  // Task's discovery root at all.
  await copyImmutableSnapshot(
    join(descriptor.cwd, "global", "agents"),
    join(descriptor.home, ".omp", "agent", "agents"),
  );
  // Child (task) skills are a SECOND explicit, bounded allowlist declared on
  // the recipe as `taskSkills` — distinct from the parent's own `skills`,
  // which `agentDir` already governs via the compiled bundle's existing
  // strict allowlist. A spawned Task child (e.g. a code-critic lane) reads
  // its lens skill under `PI_CODING_AGENT_DIR/skills` the same way the
  // parent does (oh-my-pi discovery/builtin.ts uses `getAgentDir()`, which
  // honors `PI_CODING_AGENT_DIR`). Project exactly the names this recipe
  // declared — never widen the parent's own skill surface and never
  // project all of `global/skills`.
  const recipeManifest = recipeManifestSchema.parse(
    JSON.parse(await readFile(join(descriptor.bundle, "recipe.json"), "utf8")),
  );
  for (const taskSkill of recipeManifest.taskSkills) {
    await copyImmutableSnapshot(
      join(descriptor.cwd, taskSkill.path),
      join(descriptor.agentDir, "skills", taskSkill.name),
    );
  }

  const currentContent = await Promise.all(preservedPaths.map(path => readFile(path)));
  if (currentContent.some((content, index) => !content.equals(preservedContent[index]!))
    || JSON.stringify(descriptor.model) !== preservedModel) {
    throw new Error("live Task projection changed the parent recipe composition");
  }
}

// Writes only `runtimeRoot` (nothing else from the descriptor — no env, no
// model, no paths that could leak secrets) into the receipt file the parent
// process (hatchet/src/runner.ts's invokeRunner) pre-creates and names via
// OMP_RECIPE_RUNTIME_RECEIPT. This is the adapter's half of a parent-owned
// defense: if this process is killed (e.g. OS SIGTERM) before its own async
// `cleanupRuntimeRoot` can run, the parent reads this receipt after reaping
// the child and reclaims the runtime root itself. `mode: 0o600` guards
// against a parent that couldn't pre-create the file with restrictive
// permissions for some reason; `chmod` after write makes the mode
// unconditional regardless of umask or pre-existing file permissions.
export async function writeRuntimeReceipt(receiptPath: string, runtimeRoot: string): Promise<void> {
  await writeFile(receiptPath, runtimeRoot, { mode: 0o600 });
  await chmod(receiptPath, 0o600);
}

async function loadStartRecipeTask(): Promise<StartRecipeTask> {
  // Tests select a process-level fake; production always falls back to the Bun-only shared runner.
  const moduleUrl = process.env.OMP_RECIPE_SHARED_RUNNER_MODULE
    ?? new URL("../../global/lib/recipe-task-runner.ts", import.meta.url).href;
  const loaded = await import(moduleUrl) as { startRecipeTask?: StartRecipeTask };
  if (typeof loaded.startRecipeTask !== "function") {
    throw new Error("shared recipe-task runner does not export startRecipeTask");
  }
  return loaded.startRecipeTask;
}

export async function runRecipeAdapter(
  argv: string[],
  signal: AbortSignal,
  startRecipeTask: StartRecipeTask | undefined = undefined,
): Promise<RunnerTerminal> {
  const input = parseAdapterInput(argv);
  const runtimeReceiptPath = process.env.OMP_RECIPE_RUNTIME_RECEIPT;
  const start = startRecipeTask ?? await loadStartRecipeTask();
  let handle: RecipeTaskHandle | undefined;
  let terminal: RunnerTerminal | undefined;
  let terminalCalls = 0;
  let terminalViolation: Error | undefined;
  const terminalTool: RecipeTaskHostTool = {
    name: "hatchet_terminal",
    label: "Hatchet Terminal",
    description: "Complete the current Hatchet stage with its typed terminal evidence. Call exactly once after all checks.",
    loadMode: "essential",
    parameters: terminalToolParameters,
    async execute(params): Promise<string> {
      terminalCalls += 1;
      if (terminalCalls !== 1) {
        terminalViolation = new Error("hatchet_terminal must be called exactly once");
        throw terminalViolation;
      }
      const parsed = runnerTerminalSchema.safeParse(params);
      if (!parsed.success) {
        terminalViolation = new Error("hatchet_terminal arguments do not match runnerTerminalSchema");
        throw terminalViolation;
      }
      terminal = parsed.data;
      return "Hatchet terminal accepted. Do not call this tool again. End the turn.";
    },
  };
  const cancellation = Promise.withResolvers<never>();
  const abort = (): void => cancellation.reject(
    signal.reason instanceof Error ? signal.reason : new Error("Hatchet recipe runner interrupted"),
  );
  if (signal.aborted) abort();
  else signal.addEventListener("abort", abort, { once: true });
  try {
    handle = await start({
      recipe: input.recipe,
      task: input.task,
      cwd: input.cwd,
      signal,
      timeoutMs: stageTimeoutMs,
      hostTools: [terminalTool],
      ...(runtimeReceiptPath
        ? { onPrepared: (descriptor: RecipeLaunchDescriptor) => writeRuntimeReceipt(runtimeReceiptPath, descriptor.runtimeRoot) }
        : {}),
      ...(liveTaskProjectionStages[input.stage] ? { beforeStart: stageLiveTaskProjection } : {}),
    });
    await Promise.race([handle.wait(), cancellation.promise]);
    if (terminalViolation) throw terminalViolation;
    if (terminalCalls !== 1 || terminal === undefined) {
      throw new Error("recipe did not call hatchet_terminal exactly once");
    }
    return terminal;
  } finally {
    signal.removeEventListener("abort", abort);
    await handle?.stop();
  }
}

async function main(argv: string[]): Promise<number> {
  const controller = new AbortController();
  const interrupt = (): void => controller.abort(new Error("Hatchet recipe runner interrupted"));
  process.once("SIGINT", interrupt);
  process.once("SIGTERM", interrupt);
  try {
    const terminal = await runRecipeAdapter(argv, controller.signal);
    process.stdout.write(`${JSON.stringify(terminal)}\n`);
    return 0;
  } catch (error) {
    if (controller.signal.aborted) return 130;
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`hatchet-recipe-runner: ${message}\n`);
    // Malformed CLI arguments are a genuine deterministic input problem: the
    // same recipe/round/head will fail identically on every retry. A missing
    // or schema-invalid terminal object is the *model's* non-deterministic
    // output for this attempt — a fresh attempt can plausibly produce a
    // conforming terminal, so it must stay transient/retryable (exit 70)
    // rather than aborting the whole Hatchet run as non-retryable.
    return error instanceof z.ZodError || message.startsWith("invalid Hatchet runner arguments")
      || message.startsWith("duplicate Hatchet runner argument")
      ? 64
      : 70;
  } finally {
    process.off("SIGINT", interrupt);
    process.off("SIGTERM", interrupt);
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = await main(process.argv.slice(2));
}
