import { describe, expect, it } from "vitest";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { idempotencyRoot } from "../src/config.js";
import { withDispatchLock } from "../src/dispatch-lock.js";

const lockFor = (cardId: string) => resolve(idempotencyRoot, `${cardId}.dispatch.lock`);

function delay(ms: number): Promise<void> {
  const { promise, resolve: done } = Promise.withResolvers<void>();
  setTimeout(done, ms);
  return promise;
}

describe("dispatch lock", () => {
  it("lets exactly one of two simultaneous dispatches through", async () => {
    const cardId = `concurrent-${process.pid}-${Date.now()}`;
    let dispatches = 0;
    const attempt = () =>
      withDispatchLock(cardId, async () => {
        dispatches += 1;
        await delay(50);
        return "run";
      });

    const [a, b] = await Promise.all([attempt(), attempt()]);

    expect(dispatches).toBe(1);
    expect([a, b].filter(Boolean)).toEqual(["run"]);
    await rm(lockFor(cardId), { force: true });
  });

  it("releases the lock when the dispatch throws", async () => {
    // The deleted implementation's fatal property was a key that outlived its
    // run. A dispatch that throws must not park its card.
    const cardId = `throwing-${process.pid}-${Date.now()}`;
    await expect(
      withDispatchLock(cardId, async () => {
        throw new Error("dispatch exploded");
      }),
    ).rejects.toThrow("dispatch exploded");

    expect(await withDispatchLock(cardId, async () => "admitted")).toBe("admitted");
    await rm(lockFor(cardId), { force: true });
  });

  it("breaks a stale lock rather than parking the card forever", async () => {
    // A holder that died without releasing left a file behind. Waiting on it
    // forever would recreate the wedge in a new place.
    const cardId = `stale-${process.pid}-${Date.now()}`;
    await mkdir(idempotencyRoot, { recursive: true, mode: 0o700 });
    const twoMinutesAgo = Date.now() - 120_000;
    await writeFile(lockFor(cardId), `999999:${twoMinutesAgo}\n`, { encoding: "utf8", mode: 0o600 });

    expect(await withDispatchLock(cardId, async () => "admitted")).toBe("admitted");
    await rm(lockFor(cardId), { force: true });
  });

  it("holds off a fresh lock held by a live holder", async () => {
    const cardId = `held-${process.pid}-${Date.now()}`;
    await mkdir(idempotencyRoot, { recursive: true, mode: 0o700 });
    await writeFile(lockFor(cardId), `${process.pid}:${Date.now()}\n`, { encoding: "utf8", mode: 0o600 });

    expect(await withDispatchLock(cardId, async () => "admitted")).toBeUndefined();
    await rm(lockFor(cardId), { force: true });
  });
});
