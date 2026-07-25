import { readFile, stat } from "node:fs/promises";
import { z } from "zod";
import type { OperatorConfig } from "./config.js";

// `passthrough` already carried these across the wire; declaring them is what
// lets a stage prompt use the card's own words. Optional because the ready
// queue is the authority on which cards exist, not on how complete they are -
// a card missing a title fails later, at cardFacts, with the card in hand.
const powderCardSchema = z.object({
  id: z.string().min(1),
  status: z.string().min(1),
  repo: z.string().min(1).optional(),
  title: z.string().optional(),
  body: z.string().optional(),
  priority: z.string().optional(),
  criteria: z.array(z.object({ text: z.string() }).passthrough()).optional(),
}).passthrough();
const powderCardResponseSchema = z.union([
  powderCardSchema,
  z.object({ card: powderCardSchema }).transform(({ card }) => card),
]);
const powderCardListResponseSchema = z.object({
  cards: z.array(powderCardSchema),
  has_more: z.boolean(),
  next_after: z.string().min(1).nullable().optional(),
}).passthrough();

const POWDER_READY_QUEUE_PAGE_LIMIT = 100;
const POWDER_READY_QUEUE_MAX_PAGES = 100;

export type PowderCard = z.infer<typeof powderCardSchema>;
export type PowderCardReader = () => Promise<PowderCard>;
export type PowderReadyQueueReader = () => Promise<PowderCard[]>;

async function readAuthorization(config: OperatorConfig): Promise<string | undefined> {
  const tokenFile = config.powder?.apiTokenFile;
  if (!tokenFile) return undefined;
  const metadata = await stat(tokenFile);
  if ((metadata.mode & 0o077) !== 0) throw new Error("Powder API token file must have mode 0600");
  const token = (await readFile(tokenFile, "utf8")).trim();
  if (token.length === 0) throw new Error("Powder API token file must not be empty");
  return `Bearer ${token}`;
}

export async function createPowderCardReader(
  config: OperatorConfig,
  fetchImpl: typeof fetch = fetch,
): Promise<PowderCardReader> {
  if (!config.powder) throw new Error("operator config powder section is required");
  if (!config.cardId) throw new Error("operator config cardId is required for single-card mode");
  const cardId = config.cardId;
  const authorization = await readAuthorization(config);
  const baseUrl = config.powder.baseUrl.endsWith("/") ? config.powder.baseUrl : `${config.powder.baseUrl}/`;
  const url = new URL(`api/v1/cards/${encodeURIComponent(cardId)}`, baseUrl);

  return async () => {
    const headers = new Headers();
    if (authorization) headers.set("authorization", authorization);
    const response = await fetchImpl(url, {
      headers,
      signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) throw new Error(`Powder card read failed with HTTP ${response.status}`);
    const card = powderCardResponseSchema.parse(await response.json());
    if (card.id !== cardId) throw new Error("Powder returned a different card");
    return card;
  };
}

export async function createPowderReadyQueueReader(
  config: OperatorConfig,
  fetchImpl: typeof fetch = fetch,
): Promise<PowderReadyQueueReader> {
  if (!config.powder) throw new Error("operator config powder section is required");
  const authorization = await readAuthorization(config);
  const baseUrl = config.powder.baseUrl.endsWith("/") ? config.powder.baseUrl : `${config.powder.baseUrl}/`;
  const readyStatus = config.powder.readyStatus;

  return async () => {
    const cards: PowderCard[] = [];
    let nextAfter: string | undefined;

    for (let pageNumber = 1; pageNumber <= POWDER_READY_QUEUE_MAX_PAGES; pageNumber += 1) {
      const url = new URL("api/v1/cards", baseUrl);
      url.searchParams.set("status", readyStatus);
      url.searchParams.set("limit", String(POWDER_READY_QUEUE_PAGE_LIMIT));
      if (nextAfter) url.searchParams.set("after", nextAfter);
      const headers = new Headers();
      if (authorization) headers.set("authorization", authorization);
      const response = await fetchImpl(url, {
        headers,
        signal: AbortSignal.timeout(10_000),
      });
      if (!response.ok) throw new Error(`Powder ready-queue list failed with HTTP ${response.status}`);
      const page = powderCardListResponseSchema.parse(await response.json());
      cards.push(...page.cards);
      if (!page.has_more) return cards;
      if (!page.next_after) {
        // Powder reports has_more on its final partial page but supplies no
        // cursor (observed live: 288 ready cards, page 3 of 3 returns 88 with
        // has_more=true, next_after=null). There is no further page to ask
        // for, so this is exhaustion. Throwing here would discard a complete
        // result set and disable ready-queue mode outright.
        process.stderr.write(
          `hatchet: Powder reported has_more with no next_after after ${cards.length} cards; treating as end of queue\n`,
        );
        return cards;
      }
      if (page.next_after === nextAfter) {
        // A cursor that does not advance would re-fetch the same page until
        // the cap, duplicating every card on it. Bounded, but silent and
        // wrong: name it here rather than 99 requests later.
        throw new Error(
          `Powder ready-queue cursor did not advance past ${page.next_after} after ${cards.length} cards`,
        );
      }
      nextAfter = page.next_after;
    }

    throw new Error(`Powder ready-queue pagination exceeded maximum of ${POWDER_READY_QUEUE_MAX_PAGES} pages`);
  };
}
