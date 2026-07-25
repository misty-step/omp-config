import { describe, expect, it } from "vitest";
import type { OperatorConfig } from "../src/config.js";
import { createPowderReadyQueueReader } from "../src/powder-client.js";

function config(overrides: Partial<NonNullable<OperatorConfig["powder"]>> = {}): OperatorConfig {
  return {
    version: 1,
    recipePaths: {
      implement: "/recipes/implement",
      adversarial_review: "/recipes/review",
      remediate: "/recipes/remediate",
      live_verify: "/recipes/verify",
      terminal_evidence: "/recipes/evidence",
    },
    cwd: "/repo",
    task: "task",
    powder: {
      baseUrl: "https://powder.example.test",
      readyStatus: "ready",
      mode: "ready-queue",
      ...overrides,
    },
  };
}

describe("createPowderReadyQueueReader", () => {
  it("lists cards filtered by the configured ready status", async () => {
    let capturedUrl: URL | undefined;
    const fakeFetch = (async (url: string | URL) => {
      capturedUrl = new URL(url as string);
      return new Response(
        JSON.stringify({ cards: [{ id: "c1", status: "ready", repo: "omp/a" }], total_count: 1, has_more: false }),
        { status: 200 },
      );
    }) as typeof fetch;

    const listReadyCards = await createPowderReadyQueueReader(config(), fakeFetch);
    const cards = await listReadyCards();

    expect(cards).toEqual([{ id: "c1", status: "ready", repo: "omp/a" }]);
    expect(capturedUrl?.pathname).toBe("/api/v1/cards");
    expect(capturedUrl?.searchParams.get("status")).toBe("ready");
  });

  it("throws on a non-OK HTTP response", async () => {
    const fakeFetch = (async () => new Response("", { status: 503 })) as typeof fetch;
    const listReadyCards = await createPowderReadyQueueReader(config(), fakeFetch);
    await expect(listReadyCards()).rejects.toThrow(/503/);
  });

  it("rejects a payload missing the cards array", async () => {
    const fakeFetch = (async () => new Response(JSON.stringify({ total_count: 0 }), { status: 200 })) as typeof fetch;
    const listReadyCards = await createPowderReadyQueueReader(config(), fakeFetch);
    await expect(listReadyCards()).rejects.toThrow();
  });

  it("requires a powder section", async () => {
    const bare: OperatorConfig = {
      version: 1,
      recipePaths: {
        implement: "/recipes/implement",
        adversarial_review: "/recipes/review",
        remediate: "/recipes/remediate",
        live_verify: "/recipes/verify",
        terminal_evidence: "/recipes/evidence",
      },
      cwd: "/repo",
      task: "task",
    };
    await expect(createPowderReadyQueueReader(bare)).rejects.toThrow(/powder section/);
  });
});
