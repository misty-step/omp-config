import { resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { readOperatorConfig, type OperatorConfig } from "./config.js";
import {
  createPowderCardReader,
  createPowderReadyQueueReader,
  type PowderCard,
  type PowderCardReader,
  type PowderReadyQueueReader,
} from "./powder-client.js";
import { triggerConfiguredWorkflow, type CardOverride, type TriggerResult } from "./trigger-service.js";
import { defaultPrSettings, type TriggerSource } from "./contracts.js";
import { findInFlightRun } from "./run-liveness.js";
import { findOpenPullRequestForCard } from "./github.js";

export type TriggerFn = (
  config: OperatorConfig,
  source: TriggerSource,
  requestedHeadSha?: string,
  requestedIdempotencyKey?: string,
  cardOverride?: CardOverride,
  readPowderCard?: PowderCardReader,
) => Promise<TriggerResult>;

export type CheckInFlightFn = (cardId: string) => Promise<string | undefined>;
export type FindOpenPullRequestFn = (
  cardId: string,
  branchPrefix: string,
  cwd: string,
) => Promise<string | undefined>;

export type ReconcileDependencies = {
  readPowderCard?: PowderCardReader;
  listReadyCards?: PowderReadyQueueReader;
  trigger?: TriggerFn;
  checkInFlight?: CheckInFlightFn;
  findOpenPullRequest?: FindOpenPullRequestFn;
};

/**
 * Every ready card eligible for a factory trigger, in the caller's order.
 * Pure and deterministic: no I/O, no clock. The reconciler walks these rather
 * than taking only the first, because a candidate can turn out to be parked on
 * an open pull request and must be skipped without consuming the tick.
 */
export function eligibleReadyCards(
  cards: readonly PowderCard[],
  readyStatus: string,
  repositoryAllowlist?: readonly string[],
): PowderCard[] {
  return cards.filter((card) => {
    if (card.status !== readyStatus) return false;
    if (!repositoryAllowlist) return true;
    return card.repo !== undefined && repositoryAllowlist.includes(card.repo);
  });
}

/**
 * The first eligible ready card, preserving the caller's ordering.
 */
export function selectReadyCard(
  cards: readonly PowderCard[],
  readyStatus: string,
  repositoryAllowlist?: readonly string[],
): PowderCard | undefined {
  return eligibleReadyCards(cards, readyStatus, repositoryAllowlist)[0];
}

type LivenessVerdict =
  | { kind: "clear" }
  | { kind: "in_flight"; runId: string }
  | { kind: "pr_open"; url: string }
  | { kind: "unknown"; reason: string };

async function inspectLiveness(
  cardId: string,
  config: OperatorConfig,
  deps: ReconcileDependencies,
): Promise<LivenessVerdict> {
  const checkInFlight = deps.checkInFlight ?? findInFlightRun;
  const findOpenPr = deps.findOpenPullRequest ?? findOpenPullRequestForCard;
  try {
    const runId = await checkInFlight(cardId);
    if (runId) return { kind: "in_flight", runId };
    // A card whose work is already sitting in an open pull request is not
    // waiting for the factory - it is waiting for a human. Powder still calls
    // it ready because the factory never writes card status back, so without
    // this the reconciler re-runs the same card every tick forever, paying
    // full agent cost each time to rebuild what is already up for review.
    const branchPrefix = (config.pr ?? defaultPrSettings).branchPrefix;
    const url = await findOpenPr(cardId, branchPrefix, config.cwd);
    if (url) return { kind: "pr_open", url };
    return { kind: "clear" };
  } catch (error) {
    // Fail closed. Starting a possibly-duplicate run is strictly worse than
    // skipping a tick: the next tick is 300 seconds away, while two runs
    // sharing one worktree fight over HEAD and both die on stale-head checks.
    return { kind: "unknown", reason: error instanceof Error ? error.message : String(error) };
  }
}

async function reconcileSingle(
  config: OperatorConfig,
  deps: ReconcileDependencies,
): Promise<object> {
  const readPowderCard = deps.readPowderCard ?? await createPowderCardReader(config);
  const trigger = deps.trigger ?? triggerConfiguredWorkflow;
  const card = await readPowderCard();
  if (card.status !== config.powder!.readyStatus) {
    return { mode: "single", cardId: card.id, status: card.status, triggered: false };
  }
  const liveness = await inspectLiveness(card.id, config, deps);
  if (liveness.kind === "in_flight") {
    return {
      mode: "single",
      cardId: card.id,
      status: card.status,
      triggered: false,
      reason: "run_in_flight",
      runId: liveness.runId,
    };
  }
  if (liveness.kind === "pr_open") {
    return {
      mode: "single",
      cardId: card.id,
      status: card.status,
      triggered: false,
      reason: "pull_request_open",
      url: liveness.url,
    };
  }
  if (liveness.kind === "unknown") {
    return {
      mode: "single",
      cardId: card.id,
      status: card.status,
      triggered: false,
      reason: "liveness_lookup_failed",
      detail: liveness.reason,
    };
  }
  // The card was just read; hand it to the trigger so the trigger never has to
  // re-read the card and the card facts come from this exact card, not config.
  const result = await trigger(config, "reconciler", undefined, undefined, { cardId: card.id, card }, readPowderCard);
  return { mode: "single", cardId: card.id, status: card.status, triggered: !result.duplicate, ...result };
}

async function reconcileReadyQueue(
  config: OperatorConfig,
  deps: ReconcileDependencies,
): Promise<object> {
  const listReadyCards = deps.listReadyCards ?? await createPowderReadyQueueReader(config);
  const trigger = deps.trigger ?? triggerConfiguredWorkflow;
  const cards = await listReadyCards();
  const readyStatus = config.powder!.readyStatus;
  const repositoryAllowlist = config.powder!.repositoryAllowlist;
  const candidates = eligibleReadyCards(cards, readyStatus, repositoryAllowlist);

  // A card whose work already sits in an open pull request is not busy, it is
  // parked on a human indefinitely. Consuming the tick on it - the way a truly
  // in-flight run does - would let one unreviewed PR starve the whole queue,
  // which is worse than the re-run it prevents. So these are skipped over,
  // not waited on.
  let selected: PowderCard | undefined;
  let parked = 0;
  let blocked: { reason: string; detail: string } | undefined;
  for (const candidate of candidates) {
    const verdict = await inspectLiveness(candidate.id, config, deps);
    if (verdict.kind === "pr_open") {
      parked += 1;
      continue;
    }
    if (verdict.kind === "unknown") {
      blocked = { reason: "liveness_lookup_failed", detail: verdict.reason };
      selected = candidate;
      break;
    }
    if (verdict.kind === "in_flight") {
      // Serial factory: one worktree, so a running card consumes the tick
      // rather than yielding. Skipping ahead would start a second run that
      // fights the first over HEAD.
      blocked = { reason: "run_in_flight", detail: verdict.runId };
      selected = candidate;
      break;
    }
    selected = candidate;
    break;
  }

  if (!selected) {
    return {
      mode: "ready-queue",
      triggered: false,
      candidateCount: cards.length,
      reason: "no_ready_card",
      ...(parked > 0 ? { parkedOnOpenPullRequests: parked } : {}),
    };
  }
  if (blocked) {
    return {
      mode: "ready-queue",
      cardId: selected.id,
      status: selected.status,
      triggered: false,
      candidateCount: cards.length,
      ...(parked > 0 ? { parkedOnOpenPullRequests: parked } : {}),
      ...(blocked.reason === "run_in_flight"
        ? { reason: "run_in_flight", runId: blocked.detail }
        : { reason: "liveness_lookup_failed", detail: blocked.detail }),
    };
  }
  const repository = selected.repo ?? config.repository;
  if (!repository) {
    return {
      mode: "ready-queue",
      cardId: selected.id,
      triggered: false,
      candidateCount: cards.length,
      reason: "card_missing_repository",
    };
  }
  // The selected card was just listed; hand it in so the trigger derives card
  // facts from it rather than re-reading by id.
  const result = await trigger(config, "reconciler", undefined, undefined, { cardId: selected.id, repository, card: selected });
  return {
    mode: "ready-queue",
    cardId: selected.id,
    status: selected.status,
    triggered: !result.duplicate,
    candidateCount: cards.length,
    ...(parked > 0 ? { parkedOnOpenPullRequests: parked } : {}),
    ...result,
  };
}

export async function reconcileOnce(
  config: OperatorConfig,
  deps: ReconcileDependencies = {},
): Promise<object> {
  if (!config.powder) throw new Error("operator config powder section is required");
  return config.powder.mode === "ready-queue"
    ? reconcileReadyQueue(config, deps)
    : reconcileSingle(config, deps);
}

async function main(): Promise<void> {
  const operatorConfig = await readOperatorConfig();
  if (!operatorConfig.powder) throw new Error("operator config powder section is required");
  const deps: ReconcileDependencies = operatorConfig.powder.mode === "ready-queue"
    ? { listReadyCards: await createPowderReadyQueueReader(operatorConfig) }
    : { readPowderCard: await createPowderCardReader(operatorConfig) };
  const tick = () => reconcileOnce(operatorConfig, deps);

  if (process.argv.includes("--once")) {
    process.stdout.write(`${JSON.stringify(await tick())}\n`);
    return;
  }
  const intervalMs = Number.parseInt(process.env.HATCHET_RECONCILE_INTERVAL_MS ?? "60000", 10);
  if (!Number.isSafeInteger(intervalMs) || intervalMs < 5_000) {
    throw new Error("HATCHET_RECONCILE_INTERVAL_MS must be an integer of at least 5000");
  }
  process.stdout.write(`Powder reconciler ready; interval=${intervalMs}ms\n`);
  while (true) {
    try {
      process.stdout.write(`${JSON.stringify(await tick())}\n`);
    } catch {
      process.stderr.write("Powder reconciliation failed\n");
    }
    await delay(intervalMs);
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main();
}
