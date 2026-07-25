import { describe, expect, it, vi } from "vitest";
import type { OperatorConfig } from "../src/config.js";
import type { PowderCard } from "../src/powder-client.js";
import { reconcileOnce, selectReadyCard, type ReconcileDependencies } from "../src/reconciler.js";
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
  return { runId: "run-1", duplicate: false, idempotencyKey: "key", ...overrides };
}

describe("selectReadyCard", () => {
  const cards = [
    card("c-blocked", "blocked", "omp/a"),
    card("c-first-ready", "ready", "omp/a"),
    card("c-second-ready", "ready", "omp/b"),
  ];

  it("returns the first card matching the ready status, preserving order", () => {
    expect(selectReadyCard(cards, "ready")?.id).toBe("c-first-ready");
  });

  it("skips cards whose status does not match", () => {
    expect(selectReadyCard([card("only-blocked", "blocked")], "ready")).toBeUndefined();
  });

  it("filters by repository allowlist when provided", () => {
    expect(selectReadyCard(cards, "ready", ["omp/b"])?.id).toBe("c-second-ready");
  });

  it("skips cards missing a repo when an allowlist is configured", () => {
    const noRepo = [card("no-repo", "ready")];
    expect(selectReadyCard(noRepo, "ready", ["omp/a"])).toBeUndefined();
  });

  it("returns undefined when no card is eligible", () => {
    expect(selectReadyCard(cards, "ready", ["omp/z"])).toBeUndefined();
  });
});

describe("reconcileOnce single-card mode (legacy, preserved)", () => {
  it("does not trigger when the configured card is not ready", async () => {
    const config = baseConfig();
    const trigger = vi.fn();
    const deps: ReconcileDependencies = {
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
      readPowderCard: async () => readyCard,
      trigger,
    };
    const result = await reconcileOnce(config, deps);
    expect(trigger).toHaveBeenCalledTimes(1);
    expect(trigger).toHaveBeenCalledWith(
      config,
      "reconciler",
      undefined,
      undefined,
      { cardId: "template-card", card: readyCard },
      expect.any(Function),
    );
    expect(result).toMatchObject({ mode: "single", cardId: "template-card", triggered: true, runId: "run-1" });
  });

  it("treats a duplicate trigger as not newly triggered", async () => {
    const config = baseConfig();
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult({ duplicate: true }));
    const deps: ReconcileDependencies = {
      readPowderCard: async () => card("template-card", "ready"),
      trigger,
    };
    const result = await reconcileOnce(config, deps);
    expect(result).toMatchObject({ triggered: false, duplicate: true });
  });

  it("does not trigger a card whose run is still in flight", async () => {
    const trigger = vi.fn(async () => fakeTriggerResult());
    const deps: ReconcileDependencies = {
      readPowderCard: async () => card("busy-card", "ready"),
      trigger,
      checkInFlight: async () => "run-live-1",
    };
    const result = await reconcileOnce(baseConfig({ cardId: "busy-card" }), deps);

    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({ cardId: "busy-card", triggered: false, reason: "run_in_flight", runId: "run-live-1" });
  });

  it("triggers a card whose last run failed, so a dead run never wedges it", async () => {
    // The self-heal property. `checkInFlight` reports undefined for any
    // terminal run, including a failure that left local state half-written.
    // If this ever regresses to reading execution-state files, a failed run
    // leaves `final: null` forever and the card can never be picked up again.
    const trigger = vi.fn(async () => fakeTriggerResult({ runId: "run-next" }));
    const deps: ReconcileDependencies = {
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
    const deps: ReconcileDependencies = { listReadyCards: async () => cards, trigger };
    const result = await reconcileOnce(queueConfig(), deps);

    expect(trigger).toHaveBeenCalledTimes(1);
    expect(trigger).toHaveBeenCalledWith(
      expect.anything(),
      "reconciler",
      undefined,
      undefined,
      { cardId: "first-ready", repository: "omp/a", card: cards[1] },
    );
    expect(result).toMatchObject({
      mode: "ready-queue",
      cardId: "first-ready",
      triggered: true,
      candidateCount: 3,
    });
  });

  it("filters by repositoryAllowlist before selecting a candidate", async () => {
    const cards = [
      card("wrong-repo", "ready", "omp/excluded"),
      { ...card("allowed-repo", "ready", "omp/allowed"), title: "Allowed" },
    ];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult());
    const deps: ReconcileDependencies = { listReadyCards: async () => cards, trigger };
    const result = await reconcileOnce(queueConfig({ repositoryAllowlist: ["omp/allowed"] }), deps);

    expect(trigger).toHaveBeenCalledTimes(1);
    expect(trigger).toHaveBeenCalledWith(
      expect.anything(),
      "reconciler",
      undefined,
      undefined,
      { cardId: "allowed-repo", repository: "omp/allowed", card: cards[1] },
    );
    expect(result).toMatchObject({ cardId: "allowed-repo", triggered: true });
  });

  it("never triggers when no candidate is ready and allowed", async () => {
    const cards = [card("blocked", "blocked", "omp/a"), card("wrong-repo", "ready", "omp/excluded")];
    const trigger = vi.fn();
    const deps: ReconcileDependencies = { listReadyCards: async () => cards, trigger };
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
    const deps: ReconcileDependencies = { listReadyCards: async () => cards, trigger };
    await reconcileOnce(queueConfig(), deps);

    expect(trigger).toHaveBeenCalledTimes(1);
  });

  it("surfaces a duplicate trigger without treating it as newly triggered", async () => {
    const cards = [card("already-triggered", "ready", "omp/a")];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult({ duplicate: true }));
    const deps: ReconcileDependencies = { listReadyCards: async () => cards, trigger };
    const result = await reconcileOnce(queueConfig(), deps);

    expect(result).toMatchObject({ cardId: "already-triggered", triggered: false, duplicate: true });
  });

  it("falls back to the template repository when a card omits repo", async () => {
    const cards = [{ ...card("no-repo-card", "ready"), title: "No repo" }];
    const trigger = vi.fn().mockResolvedValue(fakeTriggerResult());
    const deps: ReconcileDependencies = { listReadyCards: async () => cards, trigger };
    const result = await reconcileOnce(queueConfig(), deps);

    expect(trigger).toHaveBeenCalledWith(
      expect.anything(),
      "reconciler",
      undefined,
      undefined,
      { cardId: "no-repo-card", repository: "omp/template-repo", card: cards[0] },
    );
    expect(result).toMatchObject({ triggered: true });
  });

  it("reports a missing repository without triggering when no template fallback exists", async () => {
    const cards = [card("no-repo-card", "ready")];
    const trigger = vi.fn();
    const config = queueConfig();
    config.repository = undefined;
    const deps: ReconcileDependencies = { listReadyCards: async () => cards, trigger };
    const result = await reconcileOnce(config, deps);

    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({ cardId: "no-repo-card", triggered: false, reason: "card_missing_repository" });
  });

  it("lets a busy card consume the ready-queue tick instead of starting a rival run", async () => {
    const trigger = vi.fn(async () => fakeTriggerResult());
    const deps: ReconcileDependencies = {
      listReadyCards: async () => [card("busy", "ready", "omp/a"), card("idle", "ready", "omp/a")],
      trigger,
      checkInFlight: async (cardId) => (cardId === "busy" ? "run-live-2" : undefined),
    };
    const config = baseConfig({ powder: { baseUrl: "https://powder.example.test", readyStatus: "ready", mode: "ready-queue" } });
    const result = await reconcileOnce(config, deps);

    // One worktree means one run: skipping ahead to "idle" would start a
    // second run that fights the first over HEAD.
    expect(trigger).not.toHaveBeenCalled();
    expect(result).toMatchObject({ cardId: "busy", triggered: false, reason: "run_in_flight", runId: "run-live-2" });
  });
});
