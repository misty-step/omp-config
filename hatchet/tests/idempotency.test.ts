import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, readdir, rename, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { describe, expect, it } from "vitest";
import { idempotencyRoot } from "../src/config.js";
import { prWorkflowInputSchema, type PrWorkflowInput } from "../src/contracts.js";
import { withIdempotentTrigger } from "../src/idempotency.js";

function inputFor(idempotencyKey: string): PrWorkflowInput {
  return prWorkflowInputSchema.parse({
    version: 1,
    cardId: "card",
    repository: "omp/repo",
    headSha: "a".repeat(40),
    recipePaths: {
      implement: "/recipes/implement",
      adversarial_review: "/recipes/review",
      remediate: "/recipes/remediate",
      live_verify: "/recipes/verify",
      terminal_evidence: "/recipes/evidence",
    },
    cwd: "/repo",
    task: "task",
    card: { title: "card title", body: "", criteria: [] },
    idempotencyKey,
    triggerSource: "fixture",
    requestedAt: "2026-07-23T00:00:00.000Z",
  });
}

function lockPaths(key: string): { lockPath: string; mappingPath: string; stem: string } {
  const stem = createHash("sha256").update(key).digest("hex");
  return {
    stem,
    lockPath: resolve(idempotencyRoot, `${stem}.lock`),
    mappingPath: resolve(idempotencyRoot, `${stem}.json`),
  };
}

async function createFixtureLock(
  key: string,
  owner: { pid: number; createdAt: string; token: string },
): Promise<void> {
  const { lockPath } = lockPaths(key);
  await mkdir(idempotencyRoot, { recursive: true, mode: 0o700 });
  await mkdir(lockPath, { mode: 0o700 });
  await writeFile(resolve(lockPath, "owner.json"), `${JSON.stringify(owner)}\n`, {
    encoding: "utf8",
    mode: 0o600,
  });
}

async function cleanupKey(key: string): Promise<void> {
  const { stem } = lockPaths(key);
  const entries = await readdir(idempotencyRoot).catch(() => []);
  await Promise.all(entries
    .filter((entry) => entry.startsWith(stem))
    .map((entry) => rm(resolve(idempotencyRoot, entry), { recursive: true, force: true })));
}

describe("trigger admission idempotency", () => {
  it("admits one run under contention and resolves the persisted winner", async () => {
    const key = `concurrent-${randomUUID()}`;
    const input = inputFor(key);
    let buildCount = 0;
    let createCount = 0;
    const admit = () => withIdempotentTrigger(
      key,
      async () => { buildCount += 1; return input; },
      (existing) => expect(existing).toEqual(input),
      async () => { createCount += 1; await delay(100); return "run-concurrent"; },
    );

    const [first, second] = await Promise.all([admit(), admit()]);
    expect([first.duplicate, second.duplicate].sort()).toEqual([false, true]);
    expect(first.mapping.runId).toBe("run-concurrent");
    expect(second.mapping.runId).toBe("run-concurrent");
    expect(buildCount).toBe(1);
    expect(createCount).toBe(1);
  });

  it("recovers a lock orphaned by abrupt owner death without quarantine debris", async () => {
    const key = `dead-owner-${randomUUID()}`;
    const input = inputFor(key);
    const { stem } = lockPaths(key);
    try {
      await createFixtureLock(key, {
        pid: 999_999,
        createdAt: new Date().toISOString(),
        token: randomUUID(),
      });
      const result = await withIdempotentTrigger(
        key,
        async () => input,
        () => undefined,
        async () => "run-recovered",
        {
          isProcessAlive: () => false,
          retryDelayMs: 5,
          waitTimeoutMs: 100,
        },
      );
      expect(result).toMatchObject({
        duplicate: false,
        mapping: { runId: "run-recovered" },
      });
      const leftovers = (await readdir(idempotencyRoot))
        .filter((entry) => entry.startsWith(`${stem}.lock`));
      expect(leftovers).toEqual([]);
    } finally {
      await cleanupKey(key);
    }
  });

  it("never steals a valid live-owner lock even beyond the stale age", async () => {
    const key = `live-owner-${randomUUID()}`;
    const token = randomUUID();
    const { lockPath } = lockPaths(key);
    try {
      await createFixtureLock(key, {
        pid: process.pid,
        createdAt: new Date(Date.now() - 60_000).toISOString(),
        token,
      });
      await expect(withIdempotentTrigger(
        key,
        async () => inputFor(key),
        () => undefined,
        async () => "must-not-run",
        {
          staleAfterMs: 1,
          waitTimeoutMs: 40,
          retryDelayMs: 5,
          isProcessAlive: () => true,
        },
      )).rejects.toThrow("timed out waiting for active idempotency lock after 40ms");
      const owner = JSON.parse(await readFile(resolve(lockPath, "owner.json"), "utf8"));
      expect(owner.token).toBe(token);
    } finally {
      await cleanupKey(key);
    }
  });

  it("bounds waiting for an active lock and fails clearly", async () => {
    const key = `bounded-wait-${randomUUID()}`;
    try {
      await createFixtureLock(key, {
        pid: process.pid,
        createdAt: new Date().toISOString(),
        token: randomUUID(),
      });
      const startedAt = Date.now();
      await expect(withIdempotentTrigger(
        key,
        async () => inputFor(key),
        () => undefined,
        async () => "must-not-run",
        {
          waitTimeoutMs: 30,
          retryDelayMs: 5,
          isProcessAlive: () => true,
        },
      )).rejects.toThrow("timed out waiting for active idempotency lock after 30ms");
      expect(Date.now() - startedAt).toBeLessThan(500);
    } finally {
      await cleanupKey(key);
    }
  });

  it("releases only its own lock token", async () => {
    const key = `replacement-owner-${randomUUID()}`;
    const input = inputFor(key);
    const replacementToken = randomUUID();
    const { lockPath } = lockPaths(key);
    try {
      await expect(withIdempotentTrigger(
        key,
        async () => input,
        () => undefined,
        async () => {
          const displacedPath = `${lockPath}.displaced`;
          await rename(lockPath, displacedPath);
          await createFixtureLock(key, {
            pid: process.pid,
            createdAt: new Date().toISOString(),
            token: replacementToken,
          });
          await rm(displacedPath, { recursive: true });
          throw new Error("simulated owner replacement");
        },
      )).rejects.toThrow("simulated owner replacement");
      const owner = JSON.parse(await readFile(resolve(lockPath, "owner.json"), "utf8"));
      expect(owner.token).toBe(replacementToken);
    } finally {
      await cleanupKey(key);
    }
  });

  it("replays a completed admission without rebuilding mutable-head input", async () => {
    const key = `replay-${randomUUID()}`;
    const input = inputFor(key);
    await withIdempotentTrigger(key, async () => input, () => undefined, async () => "run-complete");

    let rebuilt = false;
    const replay = await withIdempotentTrigger(
      key,
      async () => { rebuilt = true; throw new Error("stale mutable HEAD must not be read"); },
      (existing) => expect(existing.headSha).toBe(input.headSha),
      async () => { throw new Error("duplicate must not create a run"); },
    );
    expect(replay.duplicate).toBe(true);
    expect(replay.mapping.runId).toBe("run-complete");
    expect(rebuilt).toBe(false);
  });
});
