import { z } from "zod";
import type { OperatorConfig } from "./config.js";
import { readAuthorization } from "./powder-client.js";

// Powder's canonical statuses (powder-core/src/model.rs:786-839). `shipped` and
// `abandoned` are legal but the factory never sets them: shipping is a release
// decision and abandonment is a human's judgement about whether work is worth
// doing at all. Neither is inferable from a run's outcome.
export const powderStatuses = ["backlog", "ready", "in_progress", "awaiting_input", "done"] as const;
export type PowderStatus = (typeof powderStatuses)[number];

export type WorkLogEntry = {
  body: string;
  runId?: string;
  model?: string;
  reasoning?: string;
  harness?: string;
};

export type PowderClaim = {
  // Powder mints this, and `release` will not accept the card back without it.
  // It is the claim's lease id and has nothing to do with the Hatchet run id;
  // passing one where the other belongs is silently wrong, so they are named
  // apart everywhere they travel together.
  runId: string;
  expiresAt: number;
};

export type PowderWriter = {
  claim: (cardId: string, ttlSeconds?: number) => Promise<PowderClaim>;
  release: (cardId: string, claimRunId: string) => Promise<void>;
  setStatus: (cardId: string, status: PowderStatus, dedupe: string) => Promise<void>;
  appendWorkLog: (cardId: string, entry: WorkLogEntry) => Promise<void>;
};

// Powder distinguishes the authenticated principal from the semantic worker and
// refuses to guess the second from the first (powder-server/src/main.rs:607-611).
// Work-log entries are rejected unless this matches the claim holder, so one
// constant serves both calls.
const workerIdentity = "hatchet";

// The receipt is a Claim (powder-core/src/model.rs:987-995), not a card.
const claimReceiptSchema = z
  .object({ run_id: z.string().min(1), expires_at: z.number() })
  .passthrough();

function cardUrl(config: OperatorConfig, cardId: string, suffix: string): URL {
  const configured = config.powder?.baseUrl;
  if (!configured) throw new Error("operator config powder section is required");
  const baseUrl = configured.endsWith("/") ? configured : `${configured}/`;
  return new URL(`api/v1/cards/${encodeURIComponent(cardId)}/${suffix}`, baseUrl);
}

/**
 * Writes the board. Every mutation here is observability, not control flow: a
 * card's column is a report of what the factory did, never an input to what it
 * does next. Callers decide whether a failed write is fatal, because a Powder
 * outage should not abort a run that is otherwise healthy - but they must say
 * so out loud rather than swallowing it, so these throw.
 */
export async function createPowderWriter(
  config: OperatorConfig,
  fetchImpl: typeof fetch = fetch,
): Promise<PowderWriter> {
  if (!config.powder) throw new Error("operator config powder section is required");
  const authorization = await readAuthorization(config);

  async function post(url: URL, body: unknown, idempotencyKey?: string): Promise<Response> {
    const headers = new Headers({ "content-type": "application/json" });
    if (authorization) headers.set("authorization", authorization);
    // Powder rejects keyed mutations outright without this header
    // (powder-server/src/main.rs:2387-2400). Deriving it from the run rather
    // than randomising means a retried write collapses into the first one
    // instead of appending a duplicate entry.
    if (idempotencyKey) headers.set("idempotency-key", idempotencyKey);
    const response = await fetchImpl(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) {
      throw new Error(`Powder ${url.pathname.split("/").pop()} failed with HTTP ${response.status}`);
    }
    return response;
  }

  return {
    // Claim is the only mutation Powder treats as retry-safe without a key
    // (powder-core/src/model.rs:260-301), because re-claiming a card you already
    // hold is a renewal rather than a second claim.
    async claim(cardId, ttlSeconds) {
      const response = await post(cardUrl(config, cardId, "claim"), {
        agent: workerIdentity,
        ...(ttlSeconds === undefined ? {} : { ttl_seconds: ttlSeconds }),
      });
      const receipt = claimReceiptSchema.parse(await response.json());
      return { runId: receipt.run_id, expiresAt: receipt.expires_at };
    },
    // Keyed like status and work-log; only `claim` is exempt
    // (powder-server/src/main.rs:1662 vs :1636).
    async release(cardId, runId) {
      await post(cardUrl(config, cardId, "release"), { run_id: runId }, `${cardId}:release:${runId}`);
    },
    // `dedupe` is the caller's name for this specific transition, not a nonce.
    // Two attempts to park the same run must be one board event.
    async setStatus(cardId, status, dedupe) {
      await post(cardUrl(config, cardId, "status"), { status }, `${cardId}:${status}:${dedupe}`);
    },
    async appendWorkLog(cardId, entry) {
      await post(
        cardUrl(config, cardId, "work-log"),
        {
          agent: workerIdentity,
          body: entry.body,
          ...(entry.runId === undefined ? {} : { run_id: entry.runId }),
          ...(entry.model === undefined ? {} : { model: entry.model }),
          ...(entry.reasoning === undefined ? {} : { reasoning: entry.reasoning }),
          ...(entry.harness === undefined ? {} : { harness: entry.harness }),
        },
        `${cardId}:work-log:${entry.runId ?? "unkeyed"}:${entry.body.length}`,
      );
    },
  };
}
