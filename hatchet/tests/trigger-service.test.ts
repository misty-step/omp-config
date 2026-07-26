import { describe, expect, it } from "vitest";
import { rm } from "node:fs/promises";
import { cardFactsSchema, prWorkflowInputSchema, runnerTerminalSchema, type CardFacts, type PrWorkflowInput, type RunnerTerminal } from "../src/contracts.js";
import { runPrWorkflow } from "../src/pr-workflow.js";
import { cardFactsFromPowderCard, triggerConfiguredWorkflow } from "../src/trigger-service.js";
import { executionRoot } from "../src/config.js";
import type { PowderCard } from "../src/powder-client.js";

// Real Powder read-side shape (confirmed against the live API by the lead):
// criteria is a list of `{text}` objects, body may contain literal newlines,
// priority is a string. The write side uses `acceptance` — not consumed here.
const realReadyCard: PowderCard = {
  id: "buzz-omp-allowlist-allow-path-test",
  status: "ready",
  repo: "omp-config",
  title: "buzz_omp ACP allowlist has no allow-path test",
  body: "The allowlist enforces paths, but nothing proves an allow-path case.\n\nAdd a test that asserts an allowed path is permitted.",
  priority: "p1",
  criteria: [
    { text: "allow-path test exists" },
    { text: "  " },
    { text: "denied path is rejected" },
    { text: "" },
    { text: "allowed path is accepted" },
  ],
};

function baseInput(card: CardFacts): PrWorkflowInput {
  return prWorkflowInputSchema.parse({
    version: 1,
    cardId: "buzz-omp-allowlist-allow-path-test",
    repository: "omp-config",
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
    card,
    triggerSource: "manual",
  });
}

describe("cardFactsFromPowderCard", () => {
  it("maps the real read-side card shape, preserving criteria order and dropping blanks", () => {
    const facts = cardFactsFromPowderCard(realReadyCard);
    expect(facts.title).toBe("buzz_omp ACP allowlist has no allow-path test");
    expect(facts.body).toBe(
      "The allowlist enforces paths, but nothing proves an allow-path case.\n\nAdd a test that asserts an allowed path is permitted.",
    );
    expect(facts.priority).toBe("p1");
    // Order preserved; the blank and whitespace-only entries are dropped.
    expect(facts.criteria).toEqual([
      "allow-path test exists",
      "denied path is rejected",
      "allowed path is accepted",
    ]);
    // Re-validate through the schema to prove the mapper output is contract-clean.
    expect(() => cardFactsSchema.parse(facts)).not.toThrow();
  });

  it("fails loudly naming the card id when the title is missing", () => {
    const card: PowderCard = { id: "card-007", status: "ready", criteria: [{ text: "x" }] };
    expect(() => cardFactsFromPowderCard(card)).toThrow(/card-007/);
  });

  it("fails loudly naming the card id when the title is blank", () => {
    const card: PowderCard = { id: "card-008", status: "ready", title: "   ", criteria: [{ text: "x" }] };
    expect(() => cardFactsFromPowderCard(card)).toThrow(/card-008/);
  });

  it("treats an absent body as the empty string", () => {
    const card: PowderCard = { id: "c", status: "ready", title: "T", criteria: [] };
    expect(cardFactsFromPowderCard(card).body).toBe("");
  });

  it("omits priority when absent or blank", () => {
    expect(cardFactsFromPowderCard({ id: "c", status: "ready", title: "T", criteria: [] }).priority).toBeUndefined();
    expect(cardFactsFromPowderCard({ id: "c", status: "ready", title: "T", priority: "  ", criteria: [] }).priority).toBeUndefined();
  });
});

describe("card facts reach every stage request", () => {
  it("passes input.card into each runStage request", async () => {
    const observedCards: CardFacts[] = [];
    const observedStages: string[] = [];
    const card: CardFacts = cardFactsFromPowderCard(realReadyCard);
    // Checkpoints hang off the run id, so a unique one per test keeps the
    // persisted execution state hermetic: loadWorkflowState re-reads whatever
    // the run wrote, and a stale file would otherwise mask the real behavior.
    const runId = `card-reaches-stages-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const input = baseInput(card);

    const dependencies = {
      async runStage(
        request: { recipePath: string; task: string; cwd: string; stage: string; round: number; expectedHeadSha: string; card: CardFacts },
        _signal: AbortSignal,
      ): Promise<{ terminal: RunnerTerminal; attempts: number }> {
        observedCards.push(request.card);
        observedStages.push(request.stage);
        // Return an outcome each stage's allowedOutcomes accepts:
        // implement/remediate/terminal_evidence -> completed,
        // adversarial_review -> accepted, live_verify -> verified.
        const outcome = request.stage === "adversarial_review"
          ? "accepted"
          : request.stage === "live_verify"
            ? "verified"
            : "completed";
        const terminal = runnerTerminalSchema.parse({
          version: 1,
          outcome,
          headSha: "b".repeat(40),
          artifactRefs: [],
        });
        return { terminal, attempts: 1 };
      },
      readHead: () => Promise.resolve("b".repeat(40)),
      requireHead: (_dir: string, _expected: string, _edge: string) => Promise.resolve(),
      // This test is about card facts reaching stages, not about publishing.
      // The stub records nothing; it only keeps the PR lifecycle inert.
      github: {
        ensureBranch: () => Promise.resolve(),
        publishBranch: () => Promise.resolve(),
        ensurePullRequest: () => Promise.resolve({
          number: 1,
          url: "https://github.com/omp/fixture/pull/1",
          branch: "hatchet/card",
          base: "master",
        }),
        postComment: () => Promise.resolve(),
        readPrContext: () => Promise.resolve({ comments: [] }),
        readChecks: () => Promise.resolve({ conclusion: "none" as const, headSha: "b".repeat(40), failing: [] }),
        mergePullRequest: () => Promise.resolve(),
      },
    };

    try {
      await runPrWorkflow(input, runId, new AbortController().signal, dependencies as never);

      // Every stage observed received the exact card facts.
      expect(observedStages.length).toBeGreaterThan(0);
      expect(observedStages).toContain("implement");
      expect(observedStages).toContain("terminal_evidence");
      expect(observedCards).toHaveLength(observedStages.length);
      for (const observed of observedCards) {
        // Exact assertion text proving card facts reach a stage request:
        expect(observed).toEqual(card);
      }
    } finally {
      // Clean up the persisted execution state so the test is hermetic.
      await rm(`${executionRoot}/${runId}.json`, { force: true }).catch(() => {});
    }
  });
});

// These two properties survived the move to engine-native idempotency, and both
// were real incidents. A card's body is edited while its run is in flight; an
// operator flips autoMerge mid-run. Neither changes what work is running, so
// neither may start a second run against the same worktree.
//
// The old implementation enforced this by excluding both from a hand-built
// fingerprint. The engine now enforces it by keying on the card alone, so what
// is left to prove is that this function reports the dedupe rather than
// dispatching around it.
describe("admission ignores everything except the card", () => {
  const live = { runId: "run-already-going", headSha: "b".repeat(40) };
  const config = {
    version: 1 as const,
    cardId: "card-1",
    repository: "omp-config",
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
  // A dispatch would need these; the test asserts they are never reached.
  const githubClient = { ensureBranch: async () => {} } as never;

  it("reports the live run instead of starting a second one", async () => {
    const result = await triggerConfiguredWorkflow({
      config,
      source: "manual",
      githubClient,
      checkInFlight: async () => live,
    });

    expect(result).toEqual({ runId: "run-already-going", duplicate: true, headSha: "b".repeat(40) });
  });

  it("returns the head the live run pinned, not the caller's", async () => {
    // The caller is asking on behalf of a newer commit. Reporting its own head
    // back would hide the fact that this commit is not the one running.
    const result = await triggerConfiguredWorkflow({
      config,
      source: "manual",
      headSha: "c".repeat(40),
      githubClient,
      checkInFlight: async () => live,
    });

    expect(result.headSha).toBe("b".repeat(40));
    expect(result.duplicate).toBe(true);
  });

  it("dedupes on the card whose run is live, not on the requesting card's text", async () => {
    // Card body/priority/criteria are not inputs to the lookup at all: it takes
    // a card id. Proven by asking with a card override whose text differs and
    // observing the same verdict.
    const seen: string[] = [];
    const result = await triggerConfiguredWorkflow({
      config,
      source: "reconciler",
      githubClient,
      card: {
        cardId: "card-1",
        card: { id: "card-1", status: "ready", title: "edited mid-flight", body: "rewritten" },
      },
      checkInFlight: async (cardId) => {
        seen.push(cardId);
        return live;
      },
    });

    expect(seen).toEqual(["card-1"]);
    expect(result.duplicate).toBe(true);
  });
});
