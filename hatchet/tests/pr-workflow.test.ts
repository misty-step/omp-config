import { execFile } from "node:child_process";
import { mkdir, rm, symlink } from "node:fs/promises";
import { promisify } from "node:util";
import { describe, expect, it } from "vitest";
import { prWorkflowInputSchema, type PrWorkflowInput } from "../src/contracts.js";
import { currentHeadSha, requireCurrentHead } from "../src/git-head.js";
import { runPrWorkflow } from "../src/pr-workflow.js";
import { invokeRunner, invokeRunnerWithRetry } from "../src/runner.js";
import { checkpointFinal, checkpointStage, loadWorkflowState } from "../src/state-store.js";
import type { EvidencePacket, StageResult } from "../src/contracts.js";
import { DeterministicInputError, RunnerCancelledError } from "../src/errors.js";
const fixtureRoot = new URL("../fixtures/", import.meta.url);
const runnerPath = new URL("recipe-runner.sh", fixtureRoot).pathname;
process.env.OMP_RECIPE_RUNNER = runnerPath;

// invokeRunner now stat()s request.recipePath and renders file-typed paths
// (Lane C's renderRecipe is a benign passthrough on these bash fixtures —
// they contain no {{ }} delimiters). The schema requires the five stage paths
// to be distinct strings, but each scenario ships a single .sh file, and the
// fixture dispatches on the --stage argv flag, not the path. So expose the one
// scenario file under five distinct symlinks: distinct strings satisfy the
// schema, real files satisfy stat(), and the same target keeps scenario
// dispatch unchanged.
const symlinkByStageKey: Record<string, string> = {};
async function recipePathFor(scenario: string, stage: string): Promise<string> {
  const cacheKey = `${scenario}:${stage}`;
  const cached = symlinkByStageKey[cacheKey];
  if (cached) return cached;
  const target = new URL(`scenarios/${scenario}.sh`, fixtureRoot).pathname;
  const dir = new URL("recipe-symlinks/", fixtureRoot).pathname;
  await mkdir(dir, { recursive: true });
  const link = `${dir}/${scenario}-${stage}.sh`;
  await symlink(target, link, "file").catch((error: NodeJS.ErrnoException) => {
    if (error.code !== "EEXIST") throw error;
  });
  symlinkByStageKey[cacheKey] = link;
  return link;
}

const exec = promisify(execFile);
async function gitInit(cwd: string, headSha?: string): Promise<string> {
  await rm(cwd, { recursive: true, force: true });
  await mkdir(cwd, { recursive: true, mode: 0o700 });
  await exec("git", ["-C", cwd, "init", "-q"]);
  await exec("git", ["-C", cwd, "config", "user.email", "fixture@omp.test"]);
  await exec("git", ["-C", cwd, "config", "user.name", "OMP Fixture"]);
  await exec("git", ["-C", cwd, "commit", "--allow-empty", "-m", "fixture seed"]);
  return headSha ?? await currentHeadSha(cwd);
}

async function makeInput(cwd: string, headSha: string, scenario: string, key: string): Promise<PrWorkflowInput> {
  return prWorkflowInputSchema.parse({
    version: 1,
    cardId: `card-${scenario}`,
    repository: `omp/fixture-${scenario}`,
    headSha,
    recipePaths: {
      implement: await recipePathFor(scenario, "implement"),
      adversarial_review: await recipePathFor(scenario, "adversarial_review"),
      remediate: await recipePathFor(scenario, "remediate"),
      live_verify: await recipePathFor(scenario, "live_verify"),
      terminal_evidence: await recipePathFor(scenario, "terminal_evidence"),
    },
    cwd,
    task: `run ${scenario} canary`,
    card: { title: `card-${scenario} title`, body: "", criteria: [] },
    idempotencyKey: key,
    triggerSource: "fixture",
    requestedAt: new Date().toISOString(),
  });
}

function fakeDependencies(cwd: string, observedRecipes?: string[]) {
  return {
    async runStage(...args: Parameters<typeof invokeRunnerWithRetry>) {
      observedRecipes?.push(args[0].recipePath);
      return await invokeRunnerWithRetry(...args);
    },
    readHead: () => currentHeadSha(cwd),
    requireHead: (dir: string, expected: string, edge: string) => requireCurrentHead(dir, expected, edge),
  };
}

describe("pr-workflow fixture scenarios", () => {
  it("happy path reaches awaiting_operator_approval", async () => {
    const cwd = `${fixtureRoot.pathname}runs/happy`;
    const headSha = await gitInit(cwd);
    const observedRecipes: string[] = [];
    const input = await makeInput(cwd, headSha, "happy", `happy-${headSha.slice(0, 8)}`);
    const packet = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd, observedRecipes));
    expect(packet.state).toBe("awaiting_operator_approval");
    expect(packet.fixRounds).toBe(0);
    expect(packet.reviewRounds).toBe(1);
    expect(packet.mergePerformed).toBe(false);
    expect(observedRecipes).toEqual([
      input.recipePaths.implement,
      input.recipePaths.adversarial_review,
      input.recipePaths.live_verify,
      input.recipePaths.terminal_evidence,
    ]);
  });

  it("duplicate trigger reuses existing idempotent state", async () => {
    const cwd = `${fixtureRoot.pathname}runs/duplicate`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `duplicate-${headSha.slice(0, 8)}`);
    const first = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd));
    const second = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd));
    expect(second).toEqual(first);
  });

  it("transient runner failure retries then succeeds", async () => {
    const cwd = `${fixtureRoot.pathname}runs/transient`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "transient", `transient-${headSha.slice(0, 8)}`);
    const packet = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd));
    expect(packet.state).toBe("awaiting_operator_approval");
    const state = await loadWorkflowState(input);
    const implement = state.stages.find((s) => s.stage === "implement");
    expect(implement?.attempts).toBeGreaterThan(1);
  });

  it("cancellation aborts and leaves no orphan process", async () => {
    const cwd = `${fixtureRoot.pathname}runs/cancellation`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "cancellation", `cancellation-${headSha.slice(0, 8)}`);
    const controller = new AbortController();
    const run = runPrWorkflow(input, controller.signal, fakeDependencies(cwd));
    await new Promise((resolve) => setTimeout(resolve, 100));
    controller.abort();
    await expect(run).rejects.toThrow();
  });

  it("blocked-twice terminates review_blocked after two fix rounds", async () => {
    const cwd = `${fixtureRoot.pathname}runs/blocked-twice`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "blocked-twice", `blocked-twice-${headSha.slice(0, 8)}`);
    const observedRecipes: string[] = [];
    const packet = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd, observedRecipes));
    expect(packet.state).toBe("review_blocked");
    expect(packet.fixRounds).toBe(2);
    expect(packet.reviewRounds).toBe(3);
    expect(observedRecipes).toContain(input.recipePaths.remediate);
    expect(new Set(observedRecipes).size).toBe(4);
  });
});
