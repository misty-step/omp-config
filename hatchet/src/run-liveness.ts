import { readdir, readFile } from "node:fs/promises";
import { idempotencyRoot } from "./config.js";
import { createHatchetClient } from "./hatchet-client.js";

type MappingCandidate = {
  runId: string;
  createdAt: number;
  cardId: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

// Best-effort parse of one idempotency mapping file. Legacy (version 1)
// mappings carry no `input`/cardId and are silently skipped -- they predate
// the ready-queue reconciler and can never belong to a given card. A file
// that looks like a v2 mapping but is missing/malformed required fields
// throws: fail closed rather than silently ignore a mapping that might be
// this card's live run.
function parseCandidate(value: unknown, path: string): MappingCandidate | undefined {
  if (!isRecord(value) || !("input" in value)) return undefined;
  const input = value.input;
  if (!isRecord(input)) throw new Error(`invalid idempotency mapping input at ${path}`);
  if (typeof input.cardId !== "string" || input.cardId.length === 0) {
    throw new Error(`invalid idempotency mapping cardId at ${path}`);
  }
  if (typeof value.runId !== "string" || value.runId.length === 0) {
    throw new Error(`invalid idempotency mapping runId at ${path}`);
  }
  if (typeof value.createdAt !== "string") {
    throw new Error(`invalid idempotency mapping createdAt at ${path}`);
  }
  const createdAt = Date.parse(value.createdAt);
  if (!Number.isFinite(createdAt)) {
    throw new Error(`invalid idempotency mapping createdAt at ${path}`);
  }
  return { cardId: input.cardId, runId: value.runId, createdAt };
}

// Scans every mapping under idempotencyRoot and returns the most recent one
// (by createdAt) whose input.cardId matches. Mirrors the oracle described in
// the card: "every idempotency mapping ... whose input.cardId matches, take
// the most recent by createdAt".
async function readLatestMapping(cardId: string): Promise<MappingCandidate | undefined> {
  let names: string[];
  try {
    names = await readdir(idempotencyRoot);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw error;
  }

  let latest: MappingCandidate | undefined;
  for (const name of names) {
    if (!name.endsWith(".json")) continue;
    const path = `${idempotencyRoot}/${name}`;
    let raw: string;
    try {
      raw = await readFile(path, "utf8");
    } catch (error) {
      // A mapping can be renamed away mid-scan (idempotency.ts writes via
      // temp-file + rename); treat a vanished file as absent, not fatal.
      if ((error as NodeJS.ErrnoException).code === "ENOENT") continue;
      throw error;
    }
    const candidate = parseCandidate(JSON.parse(raw) as unknown, path);
    if (!candidate || candidate.cardId !== cardId) continue;
    if (!latest || candidate.createdAt > latest.createdAt) latest = candidate;
  }
  return latest;
}

// Hatchet task/workflow run statuses meaning the run is still queued,
// executing, or otherwise not yet terminal. COMPLETED/FAILED/CANCELLED (and
// any status we don't recognize) are treated as NOT in flight -- see the
// self-heal note on findInFlightRun below.
const IN_FLIGHT_STATUSES: Record<string, true> = { QUEUED: true, RUNNING: true, PENDING: true };

/**
 * Returns the runId of the most recent idempotency mapping for `cardId` if,
 * and only if, Hatchet still reports that run as in flight (queued,
 * running, or pending). Returns undefined when there is no prior mapping,
 * the mapped run is terminal (succeeded/failed/cancelled), or Hatchet no
 * longer knows the run id (404 -> treated as terminal, not an error).
 *
 * Self-heal property: the authority for "in flight" is Hatchet's live run
 * status, never local execution-state files. A crashed or failed run
 * eventually reports FAILED from Hatchet and this function returns
 * undefined for it, so the card is never wedged by a dead run. Do not
 * "optimize" this by inspecting `local/executions/*` state files instead --
 * a failed run leaves `final: null` in that state permanently, and treating
 * that as in-flight would deadlock the card forever.
 */
export async function findInFlightRun(cardId: string): Promise<string | undefined> {
  const mapping = await readLatestMapping(cardId);
  if (!mapping) return undefined;

  const client = await createHatchetClient();
  try {
    const detail = await client.runs.get(mapping.runId);
    const status = String(detail.run.status).toUpperCase();
    return IN_FLIGHT_STATUSES[status] ? mapping.runId : undefined;
  } catch (error) {
    // A run Hatchet no longer knows about (evicted/expired) is terminal for
    // reconciliation purposes, not a lookup failure -- let the card retrigger.
    const response = isRecord(error) ? error.response : undefined;
    const notFound =
      isRecord(error) &&
      ((isRecord(response) && response.status === 404) ||
        error.status === 404 ||
        error.statusCode === 404 ||
        error.code === "NOT_FOUND");
    if (notFound) return undefined;
    throw error;
  }
}
