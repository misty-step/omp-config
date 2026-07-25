import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import { rm } from "node:fs/promises";
import { cardFactsSchema, prWorkflowInputSchema, runnerTerminalSchema, type CardFacts, type PrWorkflowInput, type RunnerTerminal } from "../src/contracts.js";
import { runPrWorkflow } from "../src/pr-workflow.js";
import { admissionPrSettings, cardFactsFromPowderCard } from "../src/trigger-service.js";
import { withIdempotentTrigger } from "../src/idempotency.js";
import { executionRoot, idempotencyRoot } from "../src/config.js";
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

function baseInput(card: CardFacts, idempotencyKey: string): PrWorkflowInput {
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
    idempotencyKey,
    triggerSource: "fixture",
    requestedAt: "2026-07-23T00:00:00.000Z",
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
    // Unique idempotency key per run keeps the persisted execution state
    // hermetic — loadWorkflowState re-reads and re-parses whatever the run
    // checkpoints, so a stale file from a prior shape would otherwise mask
    // the real behavior under test.
    const input = baseInput(card, `card-reaches-stages-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`);

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
      await runPrWorkflow(input, new AbortController().signal, dependencies as never);

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
      const stateStem = createHash("sha256").update(input.idempotencyKey).digest("hex");
      await rm(`${executionRoot}/${stateStem}.json`, { force: true }).catch(() => {});
    }
  });
});

describe("idempotency is unaffected by card text", () => {
  // The admission comparison in triggerConfiguredWorkflow deliberately
  // excludes `card`, and the idempotency key is `${cardId}:${head}` before the
  // card is ever read. Prove this end-to-end through the real
  // withIdempotentTrigger: a card whose body is edited mid-flight dedupes to
  // the same run (createRun called exactly once, duplicate=true on the second
  // admission), and the admission check passes because it excludes card text.
  // Mirrors triggerConfiguredWorkflow's admission exactly, reusing the same
  // pr-slice helper so this cannot silently diverge from production. It did:
  // this helper omitted `pr` entirely, which is why an autoMerge flip
  // colliding with a recorded run went unnoticed until it wedged a live card.
  function admissionOf(input: PrWorkflowInput): string {
    return JSON.stringify({
      version: input.version,
      cardId: input.cardId,
      repository: input.repository,
      recipePaths: input.recipePaths,
      cwd: input.cwd,
      task: input.task,
      pr: admissionPrSettings(input.pr),
      idempotencyKey: input.idempotencyKey,
    });
  }

  function buildInput(cardToUse: PowderCard, idempotencyKey: string): PrWorkflowInput {
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
      card: cardFactsFromPowderCard(cardToUse),
      idempotencyKey,
      triggerSource: "reconciler",
      requestedAt: "2026-07-23T00:00:00.000Z",
    });
  }

  it("a card whose body is edited mid-flight dedupes to the same run", async () => {
    const idempotencyKey = "buzz-omp-allowlist-allow-path-test:" + "a".repeat(40);
    const editedCard: PowderCard = { ...realReadyCard, body: "EDITED MID-FLIGHT BODY" };

    const expectedAdmission = admissionOf(buildInput(realReadyCard, idempotencyKey));
    let createRunCalls = 0;

    const first = await withIdempotentTrigger(
      idempotencyKey,
      async () => buildInput(realReadyCard, idempotencyKey),
      (input) => {
        expect(admissionOf(input)).toBe(expectedAdmission);
      },
      async () => {
        createRunCalls += 1;
        return "run-A";
      },
    );
    expect(first.duplicate).toBe(false);
    expect(first.mapping.runId).toBe("run-A");

    // Second admission: same idempotency key, edited card body. Must dedupe.
    const second = await withIdempotentTrigger(
      idempotencyKey,
      async () => buildInput(editedCard, idempotencyKey),
      (input) => {
        // Exact assertion text proving idempotency is unaffected by card text:
        // the edited card's admission equals the original's, because card is
        // excluded from the comparison.
        expect(admissionOf(input)).toBe(expectedAdmission);
      },
      async () => {
        createRunCalls += 1;
        return "run-B";
      },
    );
    expect(second.duplicate).toBe(true);
    expect(second.mapping.runId).toBe("run-A");
    expect(createRunCalls).toBe(1); // createRun ran exactly once — the edited card did not fork a new run

    // The persisted mapping carries the card from the first (winning) build.
    expect((second.mapping.input as PrWorkflowInput).card.body).toBe(realReadyCard.body);

    // Clean up the idempotency mapping so the test is hermetic.
    const stem = createHash("sha256").update(idempotencyKey).digest("hex");
    await rm(`${idempotencyRoot}/${stem}.json`, { force: true });
    await rm(`${idempotencyRoot}/${stem}.lock`, { recursive: true, force: true });
  });

  // Measured live: flipping autoMerge on the operator config made every
  // recorded run at the current head collide, and the card stayed wedged until
  // the head moved. autoMerge decides what to do after the work is done and
  // green; it never changes what work runs.
  it("an operator flipping autoMerge dedupes to the same run", async () => {
    const idempotencyKey = "automerge-flip-test:" + "b".repeat(40);
    const merging = buildInput(realReadyCard, idempotencyKey);
    const notMerging = prWorkflowInputSchema.parse({
      ...merging,
      pr: { ...merging.pr, autoMerge: !merging.pr.autoMerge },
    });

    expect(notMerging.pr.autoMerge).not.toBe(merging.pr.autoMerge);
    expect(admissionOf(notMerging)).toBe(admissionOf(merging));

    // ...while a change that does alter the work still collides.
    const otherBase = prWorkflowInputSchema.parse({
      ...merging,
      pr: { ...merging.pr, base: `${merging.pr.base}-elsewhere` },
    });
    expect(admissionOf(otherBase)).not.toBe(admissionOf(merging));

    let createRunCalls = 0;
    const first = await withIdempotentTrigger(
      idempotencyKey,
      async () => merging,
      (input) => expect(admissionOf(input)).toBe(admissionOf(merging)),
      async () => {
        createRunCalls += 1;
        return "run-merging";
      },
    );
    expect(first.duplicate).toBe(false);

    const second = await withIdempotentTrigger(
      idempotencyKey,
      async () => notMerging,
      (input) => expect(admissionOf(input)).toBe(admissionOf(merging)),
      async () => {
        createRunCalls += 1;
        return "run-not-merging";
      },
    );
    expect(second.duplicate).toBe(true);
    expect(second.mapping.runId).toBe("run-merging");
    expect(createRunCalls).toBe(1);

    const stem = createHash("sha256").update(idempotencyKey).digest("hex");
    await rm(`${idempotencyRoot}/${stem}.json`, { force: true });
    await rm(`${idempotencyRoot}/${stem}.lock`, { recursive: true, force: true });
  });
});
