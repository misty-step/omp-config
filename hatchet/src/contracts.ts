import { z } from "zod";

export const shaSchema = z.string().regex(/^[0-9a-f]{40}$/i, "expected a full git SHA");
export const artifactRefSchema = z.string().min(1).max(2048);

export const triggerSourceSchema = z.enum(["manual", "webhook", "reconciler", "fixture"]);
export type TriggerSource = z.infer<typeof triggerSourceSchema>;

export const recipePathsSchema = z.object({
  implement: z.string().min(1),
  adversarial_review: z.string().min(1),
  remediate: z.string().min(1),
  live_verify: z.string().min(1),
  terminal_evidence: z.string().min(1),
}).strict().superRefine((paths, context) => {
  const entries = Object.entries(paths);
  const uniquePaths = new Set(entries.map(([, path]) => path));
  if (uniquePaths.size !== entries.length) {
    context.addIssue({
      code: "custom",
      message: "every Hatchet stage must use a distinct recipe path",
    });
  }
});
export type RecipePaths = z.infer<typeof recipePathsSchema>;

export const prWorkflowInputSchema = z.object({
  version: z.literal(1),
  cardId: z.string().min(1).max(256),
  repository: z.string().min(1).max(512),
  headSha: shaSchema,
  recipePaths: recipePathsSchema,
  cwd: z.string().min(1),
  task: z.string().min(1),
  idempotencyKey: z.string().min(1).max(512),
  triggerSource: triggerSourceSchema,
  requestedAt: z.string().datetime(),
}).strict();

export type PrWorkflowInput = z.infer<typeof prWorkflowInputSchema>;

export const runnerOutcomeSchema = z.enum([
  "completed",
  "accepted",
  "blocked",
  "verified",
  "failed",
]);

export const runnerTerminalSchema = z.object({
  version: z.literal(1),
  outcome: runnerOutcomeSchema,
  headSha: shaSchema,
  artifactRefs: z.array(artifactRefSchema).max(64).default([]),
}).strict();

export type RunnerTerminal = z.infer<typeof runnerTerminalSchema>;

export const stageNameSchema = z.enum([
  "implement",
  "adversarial_review",
  "remediate",
  "live_verify",
  "terminal_evidence",
]);
export type StageName = z.infer<typeof stageNameSchema>;

export const stageResultSchema = z.object({
  stage: stageNameSchema,
  round: z.number().int().min(1),
  attempts: z.number().int().min(1),
  terminal: runnerTerminalSchema,
});
export type StageResult = z.infer<typeof stageResultSchema>;

export const terminalStateSchema = z.enum([
  "awaiting_operator_approval",
  "review_blocked",
  "verification_failed",
]);
export type TerminalState = z.infer<typeof terminalStateSchema>;

export const evidencePacketSchema = z.object({
  version: z.literal(1),
  state: terminalStateSchema,
  cardId: z.string(),
  repository: z.string(),
  initialHeadSha: shaSchema,
  finalHeadSha: shaSchema,
  reviewRounds: z.number().int().min(1),
  fixRounds: z.number().int().min(0).max(2),
  artifactRefs: z.array(artifactRefSchema),
  mergePerformed: z.literal(false),
  operatorApprovalRequired: z.literal(true),
});
export type EvidencePacket = z.infer<typeof evidencePacketSchema>;
