import { describe, expect, it } from "vitest";
import { prWorkflowInputSchema, evidencePacketSchema } from "../src/contracts.js";
import { loadWorkflowState } from "../src/state-store.js";

const baseInput = {
  version: 1 as const,
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
  triggerSource: "manual" as const,
};

describe("contracts", () => {
  it("rejects short head SHAs", () => {
    expect(() => prWorkflowInputSchema.parse({ ...baseInput, headSha: "abc" })).toThrow();
  });

  it("accepts a valid workflow input", () => {
    expect(prWorkflowInputSchema.parse(baseInput).headSha).toBe("a".repeat(40));
  });

  it("rejects reused or missing stage recipe paths", () => {
    expect(() => prWorkflowInputSchema.parse({
      ...baseInput,
      recipePaths: {
        ...baseInput.recipePaths,
        remediate: baseInput.recipePaths.implement,
      },
    })).toThrow(/distinct recipe path/);
    expect(() => prWorkflowInputSchema.parse({
      ...baseInput,
      recipePaths: {
        implement: "/recipes/implement",
      },
    })).toThrow();
  });

  it("rejects the removed single recipePath field", () => {
    expect(() => prWorkflowInputSchema.parse({
      ...baseInput,
      recipePath: "/legacy/recipe",
    })).toThrow();
  });

  it("evidence packet forbids mergePerformed true", () => {
    expect(() => evidencePacketSchema.parse({
      version: 1,
      state: "awaiting_operator_approval",
      cardId: "card",
      repository: "omp/repo",
      initialHeadSha: "a".repeat(40),
      finalHeadSha: "b".repeat(40),
      reviewRounds: 1,
      fixRounds: 0,
      artifactRefs: [],
      mergePerformed: true,
      operatorApprovalRequired: true,
    })).toThrow();
  });
});

describe("state store", () => {
  it("returns a fresh state for an unknown run id", async () => {
    const runId = `fresh-${Date.now()}`;
    const state = await loadWorkflowState(runId);
    expect(state).toEqual({ version: 3, runId, stages: [] });
  });
});
