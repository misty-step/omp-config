import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { idempotencyRoot } from "./config.js";

/**
 * Mutual exclusion for the instant between "no run is live for this card" and
 * "a run is now dispatched".
 *
 * This is deliberately NOT an idempotency store. The implementation it replaced
 * kept a permanent `cardId:HEAD` mapping and treated its presence as proof that
 * work had been admitted, so a run that failed before moving HEAD left a key
 * that matched forever and its card could never run again.
 *
 * The engine's own status is the authority for whether a card is busy — see
 * findInFlightRun. This lock only stops two triggers that both looked and both
 * saw nothing from both dispatching. It is held for one API call and released
 * in a finally, and a stale one expires, so no failure mode leaves a card
 * permanently unrunnable.
 *
 * Hatchet's native `idempotency` config would make this unnecessary, but the
 * deployed engine (hatchet-lite v0.94.10) ignores that field: a live probe with
 * both `ttl` and `status` strategies produced two distinct run ids for one key.
 * Delete this file once the engine is new enough to enforce it — and verify
 * with that probe rather than the SDK's type declarations, which advertise the
 * feature regardless.
 */
const STALE_AFTER_MS = 60_000;

function lockPath(cardId: string): string {
  const safe = cardId.replace(/[^A-Za-z0-9._-]/g, "_");
  return resolve(idempotencyRoot, `${safe}.dispatch.lock`);
}

/**
 * Runs `dispatch` while holding the card's dispatch lock, or returns undefined
 * if another process holds it. A caller that gets undefined has not lost work:
 * the holder is dispatching the same card, and the next reconcile tick will see
 * the resulting run.
 */
export async function withDispatchLock<T>(cardId: string, dispatch: () => Promise<T>): Promise<T | undefined> {
  await mkdir(idempotencyRoot, { recursive: true, mode: 0o700 });
  const path = lockPath(cardId);
  try {
    await writeFile(path, `${process.pid}:${Date.now()}\n`, { encoding: "utf8", mode: 0o600, flag: "wx" });
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error;
    // A crashed holder must not park the card forever, which is the entire
    // failure mode this file exists to avoid re-creating.
    const age = Date.now() - Number((await readFile(path, "utf8").catch(() => "0:0")).split(":")[1] ?? 0);
    if (age < STALE_AFTER_MS) return undefined;
    await rm(path, { force: true });
    return await withDispatchLock(cardId, dispatch);
  }
  try {
    return await dispatch();
  } finally {
    await rm(path, { force: true });
  }
}
