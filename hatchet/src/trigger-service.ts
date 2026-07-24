import { cardFactsSchema, prWorkflowInputSchema, type CardFacts, type PrWorkflowInput, type TriggerSource } from "./contracts.js";
import { currentHeadSha } from "./git-head.js";
import { createHatchetClient } from "./hatchet-client.js";
import { declarePrWorkflow } from "./hatchet-workflow.js";
import { withIdempotentTrigger } from "./idempotency.js";
import type { OperatorConfig } from "./config.js";
import { DeterministicInputError } from "./errors.js";
import { createPowderCardReader, type PowderCard, type PowderCardReader } from "./powder-client.js";

export type TriggerResult = {
  runId: string;
  duplicate: boolean;
  idempotencyKey: string;
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

export async function triggerConfiguredWorkflow(
  config: OperatorConfig,
  source: TriggerSource,
  requestedHeadSha?: string,
  requestedIdempotencyKey?: string,
  cardOverride?: CardOverride,
  readPowderCard?: PowderCardReader,
): Promise<TriggerResult> {
  const cardId = cardOverride?.cardId ?? config.cardId;
  const repository = cardOverride?.repository ?? config.repository;
  if (!cardId) throw new Error("cardId is required to trigger a workflow");
  if (!repository) throw new Error("repository is required to trigger a workflow");
  const requestedHead = requestedHeadSha?.toLowerCase();
  const initialHead = requestedIdempotencyKey ? undefined : await currentHeadSha(config.cwd);
  const idempotencyKey = requestedIdempotencyKey ?? `${cardId}:${requestedHead ?? initialHead}`;
  // The admission comparison deliberately excludes `card`: a card's body may be
  // edited mid-flight, and that edit must not break idempotency. Only the card
  // id and head pin the run; the card's words ride along on the input. The
  // idempotency key above likewise excludes card text.
  const expectedAdmission = JSON.stringify({
    version: config.version,
    cardId,
    repository,
    recipePaths: config.recipePaths,
    cwd: config.cwd,
    task: config.task,
    idempotencyKey,
  });
  const { mapping, duplicate } = await withIdempotentTrigger(
    idempotencyKey,
    async () => {
      const actualHeadSha = await currentHeadSha(config.cwd);
      const headSha = requestedHead ?? initialHead ?? actualHeadSha;
      if (headSha !== actualHeadSha) {
        throw new DeterministicInputError(
          `trigger rejected stale head: requested ${headSha}, current ${actualHeadSha}`,
        );
      }
      // Card facts come from the card actually read — never operator config.
      // Ready-queue reconciliation hands the card it already read via
      // cardOverride.card; the manual/webhook paths read it from Powder here.
      const powderCard = cardOverride?.card ?? await (readPowderCard ?? (await createPowderCardReader(config)))();
      const card = cardFactsFromPowderCard(powderCard);
      return prWorkflowInputSchema.parse({
        version: 1,
        cardId,
        repository,
        headSha,
        recipePaths: config.recipePaths,
        cwd: config.cwd,
        task: config.task,
        card,
        idempotencyKey,
        triggerSource: source,
        requestedAt: new Date().toISOString(),
      });
    },
    (admittedInput: PrWorkflowInput) => {
      const admitted = JSON.stringify({
        version: admittedInput.version,
        cardId: admittedInput.cardId,
        repository: admittedInput.repository,
        recipePaths: admittedInput.recipePaths,
        cwd: admittedInput.cwd,
        task: admittedInput.task,
        idempotencyKey: admittedInput.idempotencyKey,
      });
      if (admitted !== expectedAdmission || (requestedHead && requestedHead !== admittedInput.headSha)) {
        throw new DeterministicInputError("idempotency key reused with different trigger input");
      }
    },
    async (input: PrWorkflowInput) => {
      const client = await createHatchetClient();
      const workflow = declarePrWorkflow(client);
      const reference = await workflow.runNoWait(input, {
        additionalMetadata: {
          card_id: input.cardId,
          head_sha: input.headSha,
          idempotency_key: input.idempotencyKey,
          trigger_source: input.triggerSource,
        },
      });
      return await reference.runId;
    },
  );
  return { runId: mapping.runId, duplicate, idempotencyKey };
}
