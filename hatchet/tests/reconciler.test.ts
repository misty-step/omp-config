import { describe, expect, it, vi } from "vitest";
import type { OperatorConfig } from "../src/config.js";
import { createPowderReadyQueueReader, type PowderCard } from "../src/powder-client.js";
import { reconcileOnce, type ReconcileDependencies } from "../src/reconciler.js";
import type { TriggerResult } from "../src/trigger-service.js";

function baseConfig(overrides: Partial<OperatorConfig> = {}): OperatorConfig {
  return {
    version: 1,
    cardId: "template-card",
    repository: "omp/template-repo",
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
      mode: "single",
    },
    ...overrides,
  };
}

function card(id: string, status: string, repo?: string): PowderCard {
  return repo === undefined ? { id, status } : { id, status, repo };
}

function fakeTriggerResult(overrides: Partial<TriggerResult> = {}): TriggerResult {
  return { runId: "run-1", duplicate: false, ...overrides };
}

describe("reconcileOnce single-card mode (legacy, preserved)", () => {
  it("does not trigger when the configured card is not ready", async () => {
    const config = baseConfig();
    const trigger = vi.fn();
    const deps: ReconcileDependencies = {
      checkInFlight: async () => undefined,
      findOpenPullRequest: async () => undefined,
      readPowderCard: async () => card("template-card", "blocked"),
      trigger,
    };
    const result = await reconcileOnce(config, deps);
    expect(result).toEqual({ mode: "single", cardId: "template-card", status: "blocked", triggered: false });
    expect(trigger).not.toHaveBeenCalled();
  });

  it("triggers exactly once with no card override when the configured card is ready", async () => {
    const config = baseConfig();
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult());
    const readyCard = { ...card("template-card", "ready"), title: "Template card", criteria: [{ text: "a" }] };
    const deps: ReconcileDependencies = {
      checkInFlight: async () => undefined,
      findOpenPullRequest: async () => undefined,
      readPowderCard: async () => readyCard,
      trigger,
    };
    const result = await reconcileOnce(config, deps);
    expect(trigger).toHaveBeenCalledTimes(1);
    expect(trigger).toHaveBeenCalledWith({
      config,
      source: "reconciler",
      card: { cardId: "template-card", card: readyCard },
      readPowderCard: expect.any(Function),
    });
    expect(result).toMatchObject({ mode: "single", cardId: "template-card", triggered: true, runId: "run-1" });
  });

  it("treats a duplicate trigger as not newly triggered", async () => {
    const config = baseConfig();
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult({ duplicate: true }));
    const deps: ReconcileDependencies = {
      checkInFlight: async () => undefined,
      findOpenPullRequest: async () => undefined,
      readPowderCard: async () => card("template-card", "ready"),
      trigger,
    };
    const result = await reconcileOnce(config, deps);
    expect(result).toMatchObject({ triggered: false, duplicate: true });
  });

  it("does not trigger a card whose run is still in flight", async () => {
    const trigger = vi.fn(async () => fakeTriggerResult());
    const deps: ReconcileDependencies = {
      findOpenPullRequest: async () => undefined,
      readPowderCard: async () => card("busy-card", "ready"),
      trigger,
      checkInFlight: async () => ({ runId: "run-live-1" }),
    };
    const result = await reconcileOnce(baseConfig({ cardId: "busy-card" }), deps);

    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({ cardId: "busy-card", triggered: false, reason: "run_in_flight", runId: "run-live-1" });
  });

  it("triggers the card when the liveness check reports it clear", async () => {
    // This proves the reconciler acts on a clear verdict. It does NOT prove the
    // self-heal property it used to claim: `checkInFlight` is stubbed here, so
    // a version of it that wedged on failed runs would pass this just as well.
    //
    // What actually releases a dead run's card lives in findInFlightRun, which
    // asks the engine for QUEUED/RUNNING runs only. That is proven end-to-end
    // by the live wedge proof in the PR: a run failed with HEAD unmoved, and
    // the next trigger was admitted with a new run id.
    const trigger = vi.fn(async () => fakeTriggerResult({ runId: "run-next" }));
    const deps: ReconcileDependencies = {
      findOpenPullRequest: async () => undefined,
      readPowderCard: async () => card("recovered-card", "ready"),
      trigger,
      checkInFlight: async () => undefined,
    };
    const result = await reconcileOnce(baseConfig({ cardId: "recovered-card" }), deps);

    expect(trigger).toHaveBeenCalledTimes(1);
    expect(result).toMatchObject({ cardId: "recovered-card", triggered: true, runId: "run-next" });
  });

  it("does not trigger when the liveness lookup itself fails", async () => {
    const trigger = vi.fn(async () => fakeTriggerResult());
    const deps: ReconcileDependencies = {
      findOpenPullRequest: async () => undefined,
      readPowderCard: async () => card("unknown-card", "ready"),
      trigger,
      checkInFlight: async () => { throw new Error("hatchet unreachable"); },
    };
    const result = await reconcileOnce(baseConfig({ cardId: "unknown-card" }), deps);

    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({ cardId: "unknown-card", triggered: false, reason: "liveness_lookup_failed" });
  });
});

describe("reconcileOnce ready-queue mode", () => {
  function queueConfig(overrides: Partial<NonNullable<OperatorConfig["powder"]>> = {}): OperatorConfig {
    return baseConfig({
      powder: {
        baseUrl: "https://powder.example.test",
        readyStatus: "ready",
        mode: "ready-queue",
        ...overrides,
      },
    });
  }

  it("selects the first ready card in listed order and triggers exactly once", async () => {
    const cards = [
      card("blocked-card", "blocked", "omp/a"),
      { ...card("first-ready", "ready", "omp/a"), title: "First ready" },
      card("second-ready", "ready", "omp/b"),
    ];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult({ runId: "run-first" }));
    const deps: ReconcileDependencies = { checkInFlight: async () => undefined, listReadyCards: async () => cards, trigger , findOpenPullRequest: async () => undefined };
    const result = await reconcileOnce(queueConfig(), deps);

    expect(trigger).toHaveBeenCalledTimes(1);
    expect(trigger).toHaveBeenCalledWith({
      config: expect.anything(),
      source: "reconciler",
      card: { cardId: "first-ready", repository: "omp/a", card: cards[1] },
    });
    expect(result).toMatchObject({
      mode: "ready-queue",
      cardId: "first-ready",
      triggered: true,
      candidateCount: 3,
    });
  });
  it("selects a ready card returned on a later queue page", async () => {
    let requestCount = 0;
    const fakeFetch = (async () => {
      requestCount += 1;
      const page = requestCount === 1
        ? { cards: [card("first-page", "blocked", "omp/a")], has_more: true, next_after: "page-2" }
        : { cards: [card("later-page", "ready", "omp/a")], has_more: false };
      return new Response(JSON.stringify(page), { status: 200 });
    }) as typeof fetch;
    const listReadyCards = await createPowderReadyQueueReader(queueConfig(), fakeFetch);
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult({ runId: "run-later" }));

    const result = await reconcileOnce(queueConfig(), { checkInFlight: async () => undefined,
      listReadyCards,
      trigger,
      findOpenPullRequest: async () => undefined,
    });

    expect(trigger).toHaveBeenCalledWith({
      config: expect.anything(),
      source: "reconciler",
      card: { cardId: "later-page", repository: "omp/a", card: expect.objectContaining({ id: "later-page" }) },
    });
    expect(result).toMatchObject({ cardId: "later-page", triggered: true, runId: "run-later" });
  });

  it("filters by repositoryAllowlist before selecting a candidate", async () => {
    const cards = [
      card("wrong-repo", "ready", "omp/excluded"),
      { ...card("allowed-repo", "ready", "omp/allowed"), title: "Allowed" },
    ];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult());
    const deps: ReconcileDependencies = { checkInFlight: async () => undefined, listReadyCards: async () => cards, trigger , findOpenPullRequest: async () => undefined };
    const result = await reconcileOnce(queueConfig({ repositoryAllowlist: ["omp/allowed"] }), deps);

    expect(trigger).toHaveBeenCalledTimes(1);
    expect(trigger).toHaveBeenCalledWith({
      config: expect.anything(),
      source: "reconciler",
      card: { cardId: "allowed-repo", repository: "omp/allowed", card: cards[1] },
    });
    expect(result).toMatchObject({ cardId: "allowed-repo", triggered: true });
  });

  it("never triggers when no candidate is ready and allowed", async () => {
    const cards = [card("blocked", "blocked", "omp/a"), card("wrong-repo", "ready", "omp/excluded")];
    const trigger = vi.fn();
    const deps: ReconcileDependencies = { checkInFlight: async () => undefined, listReadyCards: async () => cards, trigger , findOpenPullRequest: async () => undefined };
    const result = await reconcileOnce(queueConfig({ repositoryAllowlist: ["omp/allowed"] }), deps);

    expect(trigger).not.toHaveBeenCalled();
    expect(result).toEqual({ mode: "ready-queue", triggered: false, candidateCount: 2, reason: "no_ready_card" });
  });

  it("triggers at most once per tick even when multiple cards are ready", async () => {
    const cards = [
      card("first-ready", "ready", "omp/a"),
      card("second-ready", "ready", "omp/b"),
      card("third-ready", "ready", "omp/c"),
    ];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult());
    const deps: ReconcileDependencies = { checkInFlight: async () => undefined, listReadyCards: async () => cards, trigger , findOpenPullRequest: async () => undefined };
    await reconcileOnce(queueConfig(), deps);

    expect(trigger).toHaveBeenCalledTimes(1);
  });

  it("surfaces a duplicate trigger without treating it as newly triggered", async () => {
    const cards = [card("already-triggered", "ready", "omp/a")];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult({ duplicate: true }));
    const deps: ReconcileDependencies = { checkInFlight: async () => undefined, listReadyCards: async () => cards, trigger , findOpenPullRequest: async () => undefined };
    const result = await reconcileOnce(queueConfig(), deps);

    expect(result).toMatchObject({ cardId: "already-triggered", triggered: false, duplicate: true });
  });

  it("falls back to the template repository when a card omits repo", async () => {
    const cards = [{ ...card("no-repo-card", "ready"), title: "No repo" }];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult());
    const deps: ReconcileDependencies = { checkInFlight: async () => undefined, listReadyCards: async () => cards, trigger , findOpenPullRequest: async () => undefined };
    const result = await reconcileOnce(queueConfig(), deps);

    expect(trigger).toHaveBeenCalledWith({
      config: expect.anything(),
      source: "reconciler",
      card: { cardId: "no-repo-card", repository: "omp/template-repo", card: cards[0] },
    });
    expect(result).toMatchObject({ triggered: true });
  });

  it("reports a missing repository without triggering when no template fallback exists", async () => {
    const cards = [card("no-repo-card", "ready")];
    const trigger = vi.fn();
    const config = queueConfig();
    config.repository = undefined;
    const deps: ReconcileDependencies = { checkInFlight: async () => undefined, listReadyCards: async () => cards, trigger , findOpenPullRequest: async () => undefined };
    const result = await reconcileOnce(config, deps);

    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({ cardId: "no-repo-card", triggered: false, reason: "card_missing_repository" });
  });

  it("lets a busy card consume the ready-queue tick instead of starting a rival run", async () => {
    const trigger = vi.fn(async () => fakeTriggerResult());
    const deps: ReconcileDependencies = {
      findOpenPullRequest: async () => undefined,
      listReadyCards: async () => [card("busy", "ready", "omp/a"), card("idle", "ready", "omp/a")],
      trigger,
      checkInFlight: async (cardId) => (cardId === "busy" ? { runId: "run-live-2" } : undefined),
    };
    const config = baseConfig({ powder: { baseUrl: "https://powder.example.test", readyStatus: "ready", mode: "ready-queue" } });
    const result = await reconcileOnce(config, deps);

    // One worktree means one run: skipping ahead to "idle" would start a
    // second run that fights the first over HEAD.
    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({ cardId: "busy", triggered: false, reason: "run_in_flight", runId: "run-live-2" });
  });

  // Measured live: a run finished at awaiting_operator_approval, the factory
  // never writes card status back, so Powder still listed the card as ready and
  // the next tick rebuilt the same work from scratch at full agent cost.
  it("skips a card whose work is already in an open pull request", async () => {
    const cards = [card("parked", "ready", "omp/a"), card("fresh", "ready", "omp/a")];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult({ runId: "run-fresh" }));
    const asked: Array<{ cardId: string; branchPrefix: string; cwd: string }> = [];
    const result = await reconcileOnce(queueConfig(), { checkInFlight: async () => undefined,
      listReadyCards: async () => cards,
      trigger,
      findOpenPullRequest: async (cardId, branchPrefix, cwd) => {
        asked.push({ cardId, branchPrefix, cwd });
        return cardId === "parked" ? "https://github.com/o/r/pull/8" : undefined;
      },
    });

    expect(result).toMatchObject({
      cardId: "fresh",
      triggered: true,
      parkedOnOpenPullRequests: 1,
    });
    expect(trigger).toHaveBeenCalledTimes(1);
    // The parked card must not consume the tick: one unreviewed pull request
    // would otherwise starve every card behind it.
    expect(asked.map(({ cardId }) => cardId)).toEqual(["parked", "fresh"]);
    // The lookup runs against the factory's own work tree, not whatever
    // directory the reconciler process happens to have been started in.
    expect(asked.every(({ cwd }) => cwd === queueConfig().cwd)).toBe(true);
    expect(asked.every(({ branchPrefix }) => branchPrefix === "hatchet/")).toBe(true);
  });

  it("reports an all-parked queue as having no ready card", async () => {
    const cards = [card("parked-1", "ready", "omp/a"), card("parked-2", "ready", "omp/a")];
    const trigger = vi.fn();
    const result = await reconcileOnce(queueConfig(), { checkInFlight: async () => undefined,
      listReadyCards: async () => cards,
      trigger,
      findOpenPullRequest: async () => "https://github.com/o/r/pull/9",
    });

    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({
      triggered: false,
      reason: "no_ready_card",
      parkedOnOpenPullRequests: 2,
    });
  });
});
