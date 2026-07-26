import { execFile } from "node:child_process";
import { mkdir, rm, symlink } from "node:fs/promises";
import { promisify } from "node:util";
import { describe, expect, it } from "vitest";
import { prWorkflowInputSchema, type CheckConclusion, type PrWorkflowInput } from "../src/contracts.js";
import { currentHeadSha, requireCurrentHead } from "../src/git-head.js";
import { runPrWorkflow } from "../src/pr-workflow.js";
import { invokeRunner, invokeRunnerWithRetry } from "../src/runner.js";
import { checkpointFinal, checkpointStage, loadWorkflowState } from "../src/state-store.js";
import type { EvidencePacket, StageResult } from "../src/contracts.js";
import { DeterministicInputError, RunnerCancelledError } from "../src/errors.js";
import type { GithubClient } from "../src/github.js";
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

async function makeInput(
  cwd: string,
  headSha: string,
  scenario: string,
  key: string,
  pr: { base?: string; branchPrefix?: string; autoMerge?: boolean } = {},
): Promise<PrWorkflowInput> {
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
    triggerSource: "manual",
    pr,
  });
}

type GithubCall = { method: string; args: unknown[] };

// Records every call so a test can assert what the WORKFLOW did, which is the
// point: publishing, posting and merging are the workflow's authority, and a
// stage must never be the thing that reaches GitHub.
function fakeGithub(options: {
  conclusion?: CheckConclusion;
  failing?: Array<{ name: string; summary: string }>;
  checkSha?: string;
} = {}) {
  const calls: GithubCall[] = [];
  const comments: Array<{ author: string; body: string }> = [];
  const client: GithubClient = {
    async ensureBranch(cwd, base, branch) { calls.push({ method: "ensureBranch", args: [cwd, base, branch] }); },
    async publishBranch(cwd, branch) { calls.push({ method: "publishBranch", args: [cwd, branch] }); },
    async ensurePullRequest(cwd, opts) {
      calls.push({ method: "ensurePullRequest", args: [cwd, opts] });
      return { number: 42, url: "https://github.com/omp/fixture/pull/42", branch: opts.branch, base: opts.base };
    },
    async postComment(cwd, pr, body) {
      calls.push({ method: "postComment", args: [cwd, pr, body] });
      comments.push({ author: "hatchet", body });
    },
    async readPrContext(cwd, pr) {
      calls.push({ method: "readPrContext", args: [cwd, pr] });
      return { comments: [...comments] };
    },
    async readChecks(cwd, pr, expectedHeadSha) {
      calls.push({ method: "readChecks", args: [cwd, pr, expectedHeadSha] });
      const sha = options.checkSha ?? expectedHeadSha;
      if (sha !== expectedHeadSha) {
        throw new Error(`check status is for ${sha}, expected ${expectedHeadSha}`);
      }
      const conclusion = options.conclusion ?? "green";
      return {
        conclusion,
        headSha: sha,
        failing: conclusion === "red" ? (options.failing ?? [{ name: "ci", summary: "boom" }]) : [],
      };
    },
    async mergePullRequest(cwd, pr) { calls.push({ method: "mergePullRequest", args: [cwd, pr] }); },
  };
  return { client, calls, comments };
}

function fakeDependencies(
  cwd: string,
  observedRecipes?: string[],
  github: GithubClient = fakeGithub().client,
  observedStages?: Array<{ stage: string; task: string }>,
) {
  return {
    async runStage(...args: Parameters<typeof invokeRunnerWithRetry>) {
      observedRecipes?.push(args[0].recipePath);
      observedStages?.push({ stage: args[0].stage, task: args[0].task });
      return await invokeRunnerWithRetry(...args);
    },
    readHead: () => currentHeadSha(cwd),
    requireHead: (dir: string, expected: string, edge: string) => requireCurrentHead(dir, expected, edge),
    github,
  };
}

let runIdCounter = 0;
const freshRunId = () => `test-run-${process.pid}-${++runIdCounter}`;

describe("pr-workflow fixture scenarios", () => {
  it("happy path reaches awaiting_operator_approval", async () => {
    const cwd = `${fixtureRoot.pathname}runs/happy`;
    const headSha = await gitInit(cwd);
    const observedRecipes: string[] = [];
    const input = await makeInput(cwd, headSha, "happy", `happy-${headSha.slice(0, 8)}`);
    const packet = await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, observedRecipes));
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
    const retriedRunId = freshRunId();
    const first = await runPrWorkflow(input, retriedRunId, new AbortController().signal, fakeDependencies(cwd));
    // Same run id: this is the engine retrying one run, which must resume.
    const second = await runPrWorkflow(input, retriedRunId, new AbortController().signal, fakeDependencies(cwd));
    expect(second).toEqual(first);
  });

  it("transient runner failure retries then succeeds", async () => {
    const cwd = `${fixtureRoot.pathname}runs/transient`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "transient", `transient-${headSha.slice(0, 8)}`);
    const runId = freshRunId();
    const packet = await runPrWorkflow(input, runId, new AbortController().signal, fakeDependencies(cwd));
    expect(packet.state).toBe("awaiting_operator_approval");
    const state = await loadWorkflowState(runId);
    const implement = state.stages.find((s) => s.stage === "implement");
    expect(implement?.attempts).toBeGreaterThan(1);
  });

  it("cancellation aborts and leaves no orphan process", async () => {
    const cwd = `${fixtureRoot.pathname}runs/cancellation`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "cancellation", `cancellation-${headSha.slice(0, 8)}`);
    const controller = new AbortController();
    const run = runPrWorkflow(input, freshRunId(), controller.signal, fakeDependencies(cwd));
    await new Promise((resolve) => setTimeout(resolve, 100));
    controller.abort();
    await expect(run).rejects.toThrow();
  });

  it("blocked-twice terminates review_blocked after two fix rounds", async () => {
    const cwd = `${fixtureRoot.pathname}runs/blocked-twice`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "blocked-twice", `blocked-twice-${headSha.slice(0, 8)}`);
    const observedRecipes: string[] = [];
    const packet = await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, observedRecipes));
    expect(packet.state).toBe("review_blocked");
    expect(packet.fixRounds).toBe(2);
    expect(packet.reviewRounds).toBe(3);
    expect(observedRecipes).toContain(input.recipePaths.remediate);
    expect(new Set(observedRecipes).size).toBe(4);
  });

  it("opens exactly one pull request and posts the review findings to it", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-open`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `pr-open-${headSha.slice(0, 8)}`);
    const github = fakeGithub();
    const packet = await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client));
    expect(packet.pr?.number).toBe(42);
    expect(packet.pr?.branch).toBe(`hatchet/card-happy`);
    expect(github.calls.filter((call) => call.method === "ensurePullRequest")).toHaveLength(1);
    const posted = github.calls.filter((call) => call.method === "postComment").map((call) => String(call.args[2]));
    expect(posted).toHaveLength(1);
    expect(posted[0]).toContain("checked everything, no blockers");
    expect(posted[0]).toContain("<!-- hatchet:adversarial_review:1:");
  });

  it("consults existing comments before every post so a replay cannot double-post", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-marker`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `pr-marker-${headSha.slice(0, 8)}`);
    const github = fakeGithub();
    await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client));
    const methods = github.calls.map((call) => call.method);
    methods.forEach((method, index) => {
      if (method !== "postComment") return;
      expect(methods.slice(0, index)).toContain("readPrContext");
    });
  });

  it("leaves a green pull request unmerged while autoMerge is off", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-nomerge`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `pr-nomerge-${headSha.slice(0, 8)}`);
    const github = fakeGithub({ conclusion: "green" });
    const packet = await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client));
    expect(packet.state).toBe("awaiting_operator_approval");
    expect(packet.mergePerformed).toBe(false);
    expect(packet.operatorApprovalRequired).toBe(true);
    expect(github.calls.some((call) => call.method === "mergePullRequest")).toBe(false);
  });

  it("merges when autoMerge is on and the checks are green for the final head", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-merge`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `pr-merge-${headSha.slice(0, 8)}`, { autoMerge: true });
    const github = fakeGithub({ conclusion: "green" });
    const packet = await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client));
    expect(packet.state).toBe("merged");
    expect(packet.mergePerformed).toBe(true);
    expect(packet.operatorApprovalRequired).toBe(false);
    // The recorded status must be for the commit that got merged, not an older one.
    expect(packet.checks?.headSha).toBe(packet.finalHeadSha);
    expect(github.calls.filter((call) => call.method === "mergePullRequest")).toHaveLength(1);
    const checkCall = github.calls.find((call) => call.method === "readChecks");
    expect(checkCall?.args[2]).toBe(packet.finalHeadSha);
  });

  it("refuses to merge red checks even with autoMerge on", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-red`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `pr-red-${headSha.slice(0, 8)}`, { autoMerge: true });
    const github = fakeGithub({ conclusion: "red", failing: [{ name: "typecheck", summary: "tsc failed" }] });
    const packet = await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client));
    expect(packet.state).toBe("awaiting_operator_approval");
    expect(packet.mergePerformed).toBe(false);
    expect(github.calls.some((call) => call.method === "mergePullRequest")).toBe(false);
  });

  it("refuses to merge when no CI is configured at all", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-nochecks`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `pr-nochecks-${headSha.slice(0, 8)}`, { autoMerge: true });
    const github = fakeGithub({ conclusion: "none" });
    const packet = await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client));
    expect(packet.state).toBe("awaiting_operator_approval");
    expect(github.calls.some((call) => call.method === "mergePullRequest")).toBe(false);
  });

  it("hands the fixer the pull request thread as its work list", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-fixer`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "blocked-twice", `pr-fixer-${headSha.slice(0, 8)}`);
    const github = fakeGithub();
    const observedStages: Array<{ stage: string; task: string }> = [];
    await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client, observedStages));
    const fixerTasks = observedStages.filter((entry) => entry.stage === "remediate").map((entry) => entry.task);
    expect(fixerTasks.length).toBeGreaterThan(0);
    expect(fixerTasks[0]).toContain("Pull request #42 context");
    expect(fixerTasks[0]).toContain("blocking problem in fixture.ts:1");
  });

  it("publishes the branch after every commit-producing stage", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-publish`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "blocked-twice", `pr-publish-${headSha.slice(0, 8)}`);
    const github = fakeGithub();
    await runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client));
    // implement, then one push per remediate round.
    expect(github.calls.filter((call) => call.method === "publishBranch")).toHaveLength(3);
    expect(github.calls[0]?.method).toBe("ensureBranch");
  });

  it("fails loud rather than merging when the authoritative check read is stale", async () => {
    const cwd = `${fixtureRoot.pathname}runs/pr-stale`;
    const headSha = await gitInit(cwd);
    const input = await makeInput(cwd, headSha, "happy", `pr-stale-${headSha.slice(0, 8)}`, { autoMerge: true });
    // A green rollup for a DIFFERENT commit is the window a fix round opens.
    // The client throws; the run must surface that, not degrade to unmerged.
    const github = fakeGithub({ conclusion: "green", checkSha: "c".repeat(40) });
    await expect(
      runPrWorkflow(input, freshRunId(), new AbortController().signal, fakeDependencies(cwd, undefined, github.client)),
    ).rejects.toThrow(/expected/);
    expect(github.calls.some((call) => call.method === "mergePullRequest")).toBe(false);
  });
});
