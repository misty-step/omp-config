import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { runnerTerminalSchema, shaSchema, stageNameSchema, type RunnerTerminal } from "./contracts.js";

const adapterInputSchema = z.object({
  recipe: z.string().min(1),
  task: z.string().min(1),
  cwd: z.string().min(1),
  stage: stageNameSchema,
  round: z.coerce.number().int().min(1),
  headSha: shaSchema,
}).strict();

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
type StartRecipeTask = (options: {
  recipe: string;
  task: string;
  cwd: string;
  signal: AbortSignal;
  timeoutMs: number;
  hostTools: RecipeTaskHostTool[];
}) => Promise<RecipeTaskHandle>;

// Bounds a single recipe-agent attempt so one hung or slow-to-converge model
// call cannot occupy an invokeRunnerWithRetry attempt indefinitely. A timeout
// rejects `handle.wait()` with a plain Error, which the adapter's own exit
// classification below treats as transient (exit 70) and therefore retryable
// up to invokeRunnerWithRetry's bounded attempt cap — the same outcome as any
// other transient stage failure, not a hang.
const stageTimeoutMs = 8 * 60_000;
const terminalToolParameters = z.toJSONSchema(runnerTerminalSchema) as Record<string, unknown>;

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
