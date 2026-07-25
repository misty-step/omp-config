import { prWorkflowInputSchema, type CardFacts, type EvidencePacket, type PrWorkflowInput, type RunnerTerminal, type StageName, type StageResult, type TerminalState } from "./contracts.js";
import { DeterministicInputError } from "./errors.js";
import { currentHeadSha, requireCurrentHead } from "./git-head.js";
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
};

const defaultDependencies: WorkflowDependencies = {
  runStage: invokeRunnerWithRetry,
  readHead: currentHeadSha,
  requireHead: requireCurrentHead,
};

function taskForStage(
  input: PrWorkflowInput,
  stage: StageName,
  round: number,
  headSha: string,
  priorStages: StageResult[],
  proposedState?: TerminalState,
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
  return `${input.task}\n\nHatchet durable stage: ${stage}. Round: ${round}. Required current head: ${headSha}.${terminalState}${priorEvidence}\nRun only the assigned OMP recipe. Do not merge. Complete the stage by calling the essential hatchet_terminal tool exactly once with outcome, full headSha, and artifactRefs; do not print terminal JSON.`;
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
  ): Promise<StageResult> => {
    const cached = findStage(state, stage, round);
    if (cached) return cached;

    await dependencies.requireHead(input.cwd, expectedHeadSha, `${stage}:${round}`);
    const attempt = await dependencies.runStage({
      recipePath: input.recipePaths[stage],
      task: taskForStage(input, stage, round, expectedHeadSha, state.stages, proposedState),
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

  const implement = await execute("implement", 1, input.headSha, true, ["completed"]);
  let headSha = implement.terminal.headSha.toLowerCase();
  let reviewRounds = 0;
  let fixRounds = 0;
  let terminalState: TerminalState | undefined;

  while (reviewRounds <= maxFixRounds) {
    reviewRounds += 1;
    const review = await execute("adversarial_review", reviewRounds, headSha, false, ["accepted", "blocked"]);
    if (review.terminal.outcome === "accepted") break;
    if (fixRounds === maxFixRounds) {
      terminalState = "review_blocked";
      break;
    }

    fixRounds += 1;
    const priorHead = headSha;
    const remediation = await execute("remediate", fixRounds, priorHead, true, ["completed"]);
    headSha = remediation.terminal.headSha.toLowerCase();
  }

  if (!terminalState) {
    const verification = await execute("live_verify", 1, headSha, false, ["verified", "failed"]);
    terminalState = verification.terminal.outcome === "verified"
      ? "awaiting_operator_approval"
      : "verification_failed";
  }

  await execute("terminal_evidence", 1, headSha, false, ["completed"], terminalState);
  const artifactRefs = [...new Set(state.stages.flatMap((stage) => stage.terminal.artifactRefs))];
  const packet: EvidencePacket = {
    version: 1,
    state: terminalState,
    cardId: input.cardId,
    repository: input.repository,
    initialHeadSha: input.headSha.toLowerCase(),
    finalHeadSha: headSha,
    reviewRounds,
    fixRounds,
    artifactRefs,
    mergePerformed: false,
    operatorApprovalRequired: true,
  };
  await checkpointFinal(state, packet);
  return packet;
}
