import { cardFactsSchema, defaultPrSettings, prBranchForCard, prWorkflowInputSchema, type CardFacts, type PrWorkflowInput, type TriggerSource } from "./contracts.js";
import { createGithubClient, type GithubClient } from "./github.js";
import { currentHeadSha } from "./git-head.js";
import { createHatchetClient } from "./hatchet-client.js";
import { declarePrWorkflow } from "./hatchet-workflow.js";
import { findInFlightRun, type LiveRun } from "./run-liveness.js";
import { withDispatchLock } from "./dispatch-lock.js";
import type { OperatorConfig } from "./config.js";
import { DeterministicInputError } from "./errors.js";
import { createPowderCardReader, type PowderCard, type PowderCardReader } from "./powder-client.js";

export type TriggerResult = {
  // Absent only in one case: another process held the dispatch lock and its run
  // was not yet visible to the engine query. The card IS being dispatched — an
  // empty string here would be indistinguishable from a real id to every caller
  // that logs it or writes it to Powder, so there is no id instead of a fake one.
  runId?: string;
  duplicate: boolean;
  // The commit the run is pinned to. When `duplicate` is true this is the head
  // the LIVE run took, which may be behind the caller's: a commit landing
  // mid-run does not start a second run, so this is how a caller tells
  // "my change is running" from "my change is queued behind the one that is".
  headSha?: string;
};

export type CardOverride = {
  cardId: string;
  repository?: string;
  // The Powder card the caller already read. Ready-queue reconciliation lists
  // cards itself, so it hands the selected card in here rather than forcing the
  // trigger to re-read by id (which the Powder client cannot do for an arbitrary
  // id). When absent, the trigger reads the card itself from Powder.
  card?: PowderCard;
};

/**
 * Pure mapper: a Powder card's own words into the bounded `CardFacts` a stage
 * prompt may consume. No I/O. `criteria` maps from the read-side `{text}[]`
 * shape to `string[]`, preserving order and dropping entries that are empty
 * after trim. A card missing or blanking its title is a LOUD failure that names
 * the card id — never a silent placeholder — because a stage prompt without
 * the card's title has no anchor for what it was asked to do. `body` absent
 * becomes the empty string.
 */
export function cardFactsFromPowderCard(card: PowderCard): CardFacts {
  const title = card.title?.trim();
  if (!title) {
    throw new Error(`Powder card ${card.id} has no title; cannot derive card facts`);
  }
  const criteria = (card.criteria ?? [])
    .map((entry) => entry.text.trim())
    .filter((text) => text.length > 0);
  return cardFactsSchema.parse({
    title,
    body: card.body ?? "",
    criteria,
    ...(card.priority && card.priority.trim().length > 0 ? { priority: card.priority } : {}),
  });
}

/**
 * A trigger request. This is an object rather than a positional list because
 * the list had grown to six parameters, four of them optional, and callers
 * padded the gaps with `undefined` — a shape where removing one parameter
 * silently slides every later argument into the wrong slot.
 */
function delay(ms: number): Promise<void> {
  const { promise, resolve } = Promise.withResolvers<void>();
  setTimeout(resolve, ms);
  return promise;
}

export type TriggerRequest = {
  config: OperatorConfig;
  source: TriggerSource;
  headSha?: string;
  card?: CardOverride;
  readPowderCard?: PowderCardReader;
  githubClient?: GithubClient;
  checkInFlight?: (cardId: string) => Promise<LiveRun | undefined>;
};

export async function triggerConfiguredWorkflow(request: TriggerRequest): Promise<TriggerResult> {
  const { config, source, card: cardOverride, readPowderCard } = request;
  const githubClient = request.githubClient ?? createGithubClient();
  const checkInFlight = request.checkInFlight ?? findInFlightRun;
  const cardId = cardOverride?.cardId ?? config.cardId;
  const repository = cardOverride?.repository ?? config.repository;
  if (!cardId) throw new Error("cardId is required to trigger a workflow");
  if (!repository) throw new Error("repository is required to trigger a workflow");
  const requestedHead = request.headSha?.toLowerCase();
  // The operator config may leave publishing policy unspecified; the trigger is
  // where it resolves.
  const prSettings = config.pr ?? defaultPrSettings;
  // The card's branch must exist BEFORE the head is read. The head pins the run
  // and every stage asserts against it, so creating the branch later - inside
  // the workflow - would move HEAD out from under a pin already taken and fail
  // `implement` on a stale-head error. Unattended runs have nobody to
  // pre-position the worktree, so the trigger does it.
  await githubClient.ensureBranch(
    config.cwd,
    prSettings.base,
    prBranchForCard(cardId, prSettings.branchPrefix),
  );
  // The engine's live run status is the authority on whether this card is
  // busy. A terminal run — including a FAILED one — releases its card here by
  // definition, which is what the deleted filesystem mapping could never do.
  const live = await checkInFlight(cardId);
  if (live) return { runId: live.runId, duplicate: true, ...(live.headSha ? { headSha: live.headSha } : {}) };

  const headSha = requestedHead ?? await currentHeadSha(config.cwd);
  // Card facts come from the card actually read — never operator config.
  // Ready-queue reconciliation hands the card it already read via
  // cardOverride.card; the manual/webhook paths read it from Powder here.
  const powderCard = cardOverride?.card ?? await (readPowderCard ?? (await createPowderCardReader(config)))();
  const input = prWorkflowInputSchema.parse({
    version: 1,
    cardId,
    repository,
    headSha,
    recipePaths: config.recipePaths,
    cwd: config.cwd,
    task: config.task,
    pr: prSettings,
    card: cardFactsFromPowderCard(powderCard),
    triggerSource: source,
  });

  // Two triggers can both pass the check above before either dispatches, and
  // two runs sharing one worktree fight over HEAD and both die. The engine
  // would normally close that window, but the deployed one ignores the
  // idempotency config (verified live — see hatchet-workflow.ts).
  const dispatched = await withDispatchLock(cardId, async () => {
    const client = await createHatchetClient();
    const workflow = declarePrWorkflow(client);
    const reference = await workflow.runNoWait(input, {
      additionalMetadata: {
        // findInFlightRun queries on card_id, so this tag is load-bearing, not
        // decoration: without it a card's live run is invisible to the reconciler.
        card_id: input.cardId,
        head_sha: input.headSha,
        trigger_source: input.triggerSource,
      },
    });
    const runId = await reference.runId;
    // Measured: a dispatched run takes roughly 500ms to appear in the engine's
    // additionalMetadata index, though it is RUNNING immediately. Releasing the
    // lock at dispatch would leave a window where the next trigger's liveness
    // check sees nothing and starts a rival run. Hold until the run is
    // observable by the same query that guards admission.
    let observable = false;
    for (const delayMs of [100, 200, 400, 800, 1600]) {
      observable = Boolean(await checkInFlight(cardId));
      if (observable) break;
      await delay(delayMs);
    }
    if (!observable) {
      // Releasing here reopens the double-dispatch window this loop exists to
      // close. It should be unreachable — say so loudly rather than letting a
      // slower index or a broken metadata filter surface weeks later as an
      // unexplained rival run.
      process.stderr.write(
        `trigger: run ${runId} for card ${cardId} was not observable within 3.1s; ` +
        `dispatch lock releasing anyway, a concurrent trigger may start a rival run\n`,
      );
    }
    return runId;
  });

  if (!dispatched) {
    // Another process is dispatching this same card right now. Report the
    // dedupe rather than inventing a run id; the next tick observes its run.
    // The holder's run may not be queryable yet, so give it a moment before
    // reporting an unobservable dispatch.
    for (const delayMs of [150, 400, 1000]) {
      const raced = await checkInFlight(cardId);
      if (raced) return { runId: raced.runId, duplicate: true, ...(raced.headSha ? { headSha: raced.headSha } : {}) };
      await delay(delayMs);
    }
    return { duplicate: true, headSha };
  }
  return { runId: dispatched, duplicate: false, headSha };
}
