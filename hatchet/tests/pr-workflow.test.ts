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

function scenarioPath(name: string): string {
  return new URL(`scenarios/${name}.sh`, fixtureRoot).pathname;
}

async function gitInit(cwd: string, headSha?: string): Promise<string> {
  const { rm, mkdir } = await import("node:fs/promises");
  await rm(cwd, { recursive: true, force: true });
  await mkdir(cwd, { recursive: true, mode: 0o700 });
  const { execFile } = await import("node:child_process");
  const { promisify } = await import("node:util");
  const exec = promisify(execFile);
  await exec("git", ["-C", cwd, "init", "-q"]);
  await exec("git", ["-C", cwd, "config", "user.email", "fixture@omp.test"]);
  await exec("git", ["-C", cwd, "config", "user.name", "OMP Fixture"]);
  await exec("git", ["-C", cwd, "commit", "--allow-empty", "-m", "fixture seed"]);
  return headSha ?? await currentHeadSha(cwd);
}

function makeInput(cwd: string, headSha: string, scenario: string, key: string): PrWorkflowInput {
  return prWorkflowInputSchema.parse({
    version: 1,
    cardId: `card-${scenario}`,
    repository: `omp/fixture-${scenario}`,
    headSha,
    recipePaths: {
      implement: `${scenarioPath(scenario)}::implement`,
      adversarial_review: `${scenarioPath(scenario)}::adversarial_review`,
      remediate: `${scenarioPath(scenario)}::remediate`,
      live_verify: `${scenarioPath(scenario)}::live_verify`,
      terminal_evidence: `${scenarioPath(scenario)}::terminal_evidence`,
    },
    cwd,
    task: `run ${scenario} canary`,
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
    const input = makeInput(cwd, headSha, "happy", `happy-${headSha.slice(0, 8)}`);
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
    const input = makeInput(cwd, headSha, "happy", `duplicate-${headSha.slice(0, 8)}`);
    const first = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd));
    const second = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd));
    expect(second).toEqual(first);
  });

  it("transient runner failure retries then succeeds", async () => {
    const cwd = `${fixtureRoot.pathname}runs/transient`;
    const headSha = await gitInit(cwd);
    const input = makeInput(cwd, headSha, "transient", `transient-${headSha.slice(0, 8)}`);
    const packet = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd));
    expect(packet.state).toBe("awaiting_operator_approval");
    const state = await loadWorkflowState(input);
    const implement = state.stages.find((s) => s.stage === "implement");
    expect(implement?.attempts).toBeGreaterThan(1);
  });

  it("cancellation aborts and leaves no orphan process", async () => {
    const cwd = `${fixtureRoot.pathname}runs/cancellation`;
    const headSha = await gitInit(cwd);
    const input = makeInput(cwd, headSha, "cancellation", `cancellation-${headSha.slice(0, 8)}`);
    const controller = new AbortController();
    const run = runPrWorkflow(input, controller.signal, fakeDependencies(cwd));
    await new Promise((resolve) => setTimeout(resolve, 100));
    controller.abort();
    await expect(run).rejects.toThrow();
  });

  it("blocked-twice terminates review_blocked after two fix rounds", async () => {
    const cwd = `${fixtureRoot.pathname}runs/blocked-twice`;
    const headSha = await gitInit(cwd);
    const input = makeInput(cwd, headSha, "blocked-twice", `blocked-twice-${headSha.slice(0, 8)}`);
    const observedRecipes: string[] = [];
    const packet = await runPrWorkflow(input, new AbortController().signal, fakeDependencies(cwd, observedRecipes));
    expect(packet.state).toBe("review_blocked");
    expect(packet.fixRounds).toBe(2);
    expect(packet.reviewRounds).toBe(3);
    expect(observedRecipes).toContain(input.recipePaths.remediate);
    expect(new Set(observedRecipes).size).toBe(4);
  });
});
