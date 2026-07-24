import { randomUUID } from "node:crypto";
import { setTimeout as delay } from "node:timers/promises";
import { describe, expect, it } from "vitest";
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
    idempotencyKey,
    triggerSource: "fixture",
    requestedAt: "2026-07-23T00:00:00.000Z",
  });
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
