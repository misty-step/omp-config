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
import type { TriggerSource } from "./contracts.js";
import { findInFlightRun } from "./run-liveness.js";

export type TriggerFn = (
  config: OperatorConfig,
  source: TriggerSource,
  requestedHeadSha?: string,
  requestedIdempotencyKey?: string,
  cardOverride?: CardOverride,
  readPowderCard?: PowderCardReader,
) => Promise<TriggerResult>;

export type CheckInFlightFn = (cardId: string) => Promise<string | undefined>;

export type ReconcileDependencies = {
  readPowderCard?: PowderCardReader;
  listReadyCards?: PowderReadyQueueReader;
  trigger?: TriggerFn;
  checkInFlight?: CheckInFlightFn;
};

/**
 * Selects the first ready card eligible for a factory trigger, preserving
 * the caller's ordering. Pure and deterministic: no I/O, no clock.
 */
export function selectReadyCard(
  cards: readonly PowderCard[],
  readyStatus: string,
  repositoryAllowlist?: readonly string[],
): PowderCard | undefined {
  return cards.find((card) => {
    if (card.status !== readyStatus) return false;
    if (!repositoryAllowlist) return true;
    return card.repo !== undefined && repositoryAllowlist.includes(card.repo);
  });
}

type LivenessVerdict =
  | { kind: "clear" }
  | { kind: "in_flight"; runId: string }
  | { kind: "unknown"; reason: string };

async function inspectLiveness(cardId: string, deps: ReconcileDependencies): Promise<LivenessVerdict> {
  const checkInFlight = deps.checkInFlight ?? findInFlightRun;
  try {
    const runId = await checkInFlight(cardId);
    return runId ? { kind: "in_flight", runId } : { kind: "clear" };
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
  const liveness = await inspectLiveness(card.id, deps);
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
  const selected = selectReadyCard(cards, readyStatus, repositoryAllowlist);
  if (!selected) {
    return { mode: "ready-queue", triggered: false, candidateCount: cards.length, reason: "no_ready_card" };
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
  // Serial factory: at most one trigger attempt per reconcile tick, ever. A
  // busy card consumes the tick rather than yielding to the next candidate -
  // there is one worktree, so "skip ahead to another card" would just start a
  // second run that fights the first one over HEAD.
  const liveness = await inspectLiveness(selected.id, deps);
  if (liveness.kind !== "clear") {
    return {
      mode: "ready-queue",
      cardId: selected.id,
      status: selected.status,
      triggered: false,
      candidateCount: cards.length,
      ...(liveness.kind === "in_flight"
        ? { reason: "run_in_flight", runId: liveness.runId }
        : { reason: "liveness_lookup_failed", detail: liveness.reason }),
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
