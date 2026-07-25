import { evidencePacketSchema, prBranchForCard, prWorkflowInputSchema, type CardFacts, type CheckStatus, type EvidencePacket, type PrRef, type PrWorkflowInput, type RunnerTerminal, type StageName, type StageResult, type TerminalState } from "./contracts.js";
import { DeterministicInputError } from "./errors.js";
import { currentHeadSha, requireCurrentHead } from "./git-head.js";
import { createGithubClient, type GithubClient } from "./github.js";
import { invokeRunnerWithRetry, type RunnerAttempt } from "./runner.js";
import { checkpointFinal, checkpointStage, findStage, loadWorkflowState } from "./state-store.js";

const maxFixRounds = 2;

type RunStage = (request: {
  recipePath: string;
  task: string;
  cwd: string;
  stage: StageName;
  round: number;
  expectedHeadSha: string;
  card: CardFacts;
}, signal: globalThis.AbortSignal) => Promise<RunnerAttempt>;

type WorkflowDependencies = {
  runStage: RunStage;
  readHead: typeof currentHeadSha;
  requireHead: typeof requireCurrentHead;
  github: GithubClient;
};

const defaultDependencies: WorkflowDependencies = {
  runStage: invokeRunnerWithRetry,
  readHead: currentHeadSha,
  requireHead: requireCurrentHead,
  github: createGithubClient(),
};

function prBody(input: PrWorkflowInput): string {
  const criteria = input.card.criteria.length === 0
    ? ""
    : `\n\n## Acceptance criteria\n\n${input.card.criteria.map((line) => `- [ ] ${line}`).join("\n")}`;
  const body = input.card.body.trim().length === 0 ? "" : `\n\n${input.card.body.trim()}`;
  return `Opened by Hatchet for card \`${input.cardId}\`.${body}${criteria}\n\nReview findings and fix rounds are posted to this pull request as they happen.`;
}

function stageHeading(stage: StageName, round: number, outcome: RunnerTerminal["outcome"]): string {
  return `### ${stage} round ${round} — ${outcome}`;
}

// Posting is idempotent through a content marker rather than extra durable
// state: a replayed run re-reaches this line with a cached stage result, and a
// second identical comment would be indistinguishable from a second review.
async function publishFindings(
  github: GithubClient,
  cwd: string,
  pr: number,
  result: StageResult,
): Promise<void> {
  const findings = result.terminal.findings?.trim();
  if (!findings) return;
  const marker = `<!-- hatchet:${result.stage}:${result.round}:${result.terminal.headSha.toLowerCase()} -->`;
  const existing = await github.readPrContext(cwd, pr);
  if (existing.comments.some((comment) => comment.body.includes(marker))) return;
  const heading = stageHeading(result.stage, result.round, result.terminal.outcome);
  await github.postComment(cwd, pr, `${marker}\n${heading}\n\n${findings}`);
}

// The fixer's work list. This read is INFORMATIONAL, so a check status that is
// unavailable or lagging behind a just-pushed commit degrades to a note rather
// than failing the run. The merge decision uses its own authoritative read.
async function fixerContext(
  github: GithubClient,
  cwd: string,
  pr: number,
  headSha: string,
): Promise<string> {
  const comments = await github.readPrContext(cwd, pr);
  let checkNote = "CI status for this commit is not available yet.";
  try {
    const checks = await github.readChecks(cwd, pr, headSha);
    checkNote = checks.conclusion === "red"
      ? `Failing CI checks:\n${checks.failing.map((check) => `- ${check.name}: ${check.summary}`).join("\n")}`
      : `CI checks for this commit: ${checks.conclusion}.`;
  } catch {
    // Left as the default note on purpose - see the comment above.
  }
  const thread = comments.comments.length === 0
    ? "No pull request comments yet."
    : comments.comments.map((comment) => `--- ${comment.author} ---\n${comment.body}`).join("\n\n");
  return `Pull request #${pr} context. Treat every unresolved item below as your work list.\n\n${thread}\n\n${checkNote}`;
}

function taskForStage(
  input: PrWorkflowInput,
  stage: StageName,
  round: number,
  headSha: string,
  priorStages: StageResult[],
  proposedState?: TerminalState,
  prContext?: string,
): string {
  const terminalState = proposedState ? `\nTerminal state: ${proposedState}.` : "";
  const priorEvidence = priorStages.length === 0
    ? ""
    : `\nPrior durable stage evidence: ${JSON.stringify(priorStages.map((result) => ({
      stage: result.stage,
      round: result.round,
      outcome: result.terminal.outcome,
      headSha: result.terminal.headSha,
      artifactRefs: result.terminal.artifactRefs,
    })))}.`;
  const pullRequest = prContext ? `\n\n${prContext}` : "";
  return `${input.task}\n\nHatchet durable stage: ${stage}. Round: ${round}. Required current head: ${headSha}.${terminalState}${priorEvidence}${pullRequest}\nRun only the assigned OMP recipe. Do not merge and do not push; the workflow publishes your commit and posts your findings for you. Complete the stage by calling the essential hatchet_terminal tool exactly once with outcome, full headSha, artifactRefs, and findings when this stage authors them; do not print terminal JSON.`;
}

function requireOutcome(stage: StageName, terminal: RunnerTerminal, allowed: RunnerTerminal["outcome"][]): void {
  if (!allowed.includes(terminal.outcome)) {
    throw new DeterministicInputError(`${stage} returned disallowed outcome ${terminal.outcome}`);
  }
}

export async function runPrWorkflow(
  rawInput: PrWorkflowInput,
  signal: globalThis.AbortSignal,
  dependencies: WorkflowDependencies = defaultDependencies,
): Promise<EvidencePacket> {
  const input = prWorkflowInputSchema.parse(rawInput);
  const state = await loadWorkflowState(input);
  if (state.final) return state.final;

  const execute = async (
    stage: StageName,
    round: number,
    expectedHeadSha: string,
    mutatesHead: boolean,
    allowedOutcomes: RunnerTerminal["outcome"][],
    proposedState?: TerminalState,
    prContext?: string,
  ): Promise<StageResult> => {
    const cached = findStage(state, stage, round);
    if (cached) return cached;

    await dependencies.requireHead(input.cwd, expectedHeadSha, `${stage}:${round}`);
    const attempt = await dependencies.runStage({
      recipePath: input.recipePaths[stage],
      task: taskForStage(input, stage, round, expectedHeadSha, state.stages, proposedState, prContext),
      cwd: input.cwd,
      stage,
      round,
      expectedHeadSha,
      card: input.card,
    }, signal);
    requireOutcome(stage, attempt.terminal, allowedOutcomes);
    const actualHead = await dependencies.readHead(input.cwd);
    if (attempt.terminal.headSha.toLowerCase() !== actualHead) {
      throw new DeterministicInputError(`${stage}:${round} runner head does not match current HEAD`);
    }
    if (!mutatesHead && actualHead !== expectedHeadSha.toLowerCase()) {
      throw new DeterministicInputError(`${stage}:${round} changed HEAD unexpectedly`);
    }
    if (mutatesHead && actualHead === expectedHeadSha.toLowerCase()) {
      throw new DeterministicInputError(`${stage}:${round} did not produce a new HEAD`);
    }

    const result: StageResult = { stage, round, attempts: attempt.attempts, terminal: attempt.terminal };
    await checkpointStage(state, result);
    return result;
  };

  const branch = prBranchForCard(input.cardId, input.pr.branchPrefix);
  await dependencies.github.ensureBranch(input.cwd, input.pr.base, branch);

  const implement = await execute("implement", 1, input.headSha, true, ["completed"]);
  let headSha = implement.terminal.headSha.toLowerCase();

  // Publishing belongs to the workflow, never to a stage. An agent that can
  // push and open pull requests can also do both without passing review.
  await dependencies.github.publishBranch(input.cwd, branch);
  const pr: PrRef = await dependencies.github.ensurePullRequest(input.cwd, {
    branch,
    base: input.pr.base,
    title: input.card.title,
    body: prBody(input),
  });
  await publishFindings(dependencies.github, input.cwd, pr.number, implement);

  let reviewRounds = 0;
  let fixRounds = 0;
  let terminalState: TerminalState | undefined;

  while (reviewRounds <= maxFixRounds) {
    reviewRounds += 1;
    const review = await execute("adversarial_review", reviewRounds, headSha, false, ["accepted", "blocked"]);
    await publishFindings(dependencies.github, input.cwd, pr.number, review);
    if (review.terminal.outcome === "accepted") break;
    if (fixRounds === maxFixRounds) {
      terminalState = "review_blocked";
      break;
    }

    fixRounds += 1;
    const priorHead = headSha;
    const context = await fixerContext(dependencies.github, input.cwd, pr.number, priorHead);
    const remediation = await execute("remediate", fixRounds, priorHead, true, ["completed"], undefined, context);
    headSha = remediation.terminal.headSha.toLowerCase();
    await dependencies.github.publishBranch(input.cwd, branch);
    await publishFindings(dependencies.github, input.cwd, pr.number, remediation);
  }

  let checks: CheckStatus | undefined;
  if (!terminalState) {
    const verification = await execute("live_verify", 1, headSha, false, ["verified", "failed"]);
    if (verification.terminal.outcome !== "verified") {
      terminalState = "verification_failed";
    } else {
      // Authoritative, unlike the fixer's read: this one decides a merge, so a
      // stale or unreadable status must fail the run rather than degrade. The
      // client throws when the rollup is not for `headSha`.
      checks = await dependencies.github.readChecks(input.cwd, pr.number, headSha);
      if (input.pr.autoMerge && checks.conclusion === "green") {
        await dependencies.github.mergePullRequest(input.cwd, pr.number);
        terminalState = "merged";
      } else {
        terminalState = "awaiting_operator_approval";
      }
    }
  }

  await execute("terminal_evidence", 1, headSha, false, ["completed"], terminalState);
  const artifactRefs = [...new Set(state.stages.flatMap((stage) => stage.terminal.artifactRefs))];
  // Parsed, not cast: the schema is what refuses a packet that claims a merge
  // without a pull request and a green status for this exact commit.
  const packet: EvidencePacket = evidencePacketSchema.parse({
    version: 1,
    state: terminalState,
    cardId: input.cardId,
    repository: input.repository,
    initialHeadSha: input.headSha.toLowerCase(),
    finalHeadSha: headSha,
    reviewRounds,
    fixRounds,
    artifactRefs,
    pr,
    checks,
    mergePerformed: terminalState === "merged",
    operatorApprovalRequired: terminalState !== "merged",
  });
  await checkpointFinal(state, packet);
  return packet;
}
