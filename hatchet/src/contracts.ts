import { z } from "zod";

export const shaSchema = z.string().regex(/^[0-9a-f]{40}$/i, "expected a full git SHA");
export const artifactRefSchema = z.string().min(1).max(2048);

export const triggerSourceSchema = z.enum(["manual", "webhook", "reconciler"]);
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

// The card's own words. Hatchet's trigger was always card-driven; its payload
// was not, so every stage replayed one static operator string. These are the
// only card fields a stage prompt may consume - bounded so a large card body
// cannot silently blow the runner's argv or output limits.
export const cardFactsSchema = z.object({
  title: z.string().min(1).max(512),
  body: z.string().max(20_000).default(""),
  criteria: z.array(z.string().min(1).max(2048)).max(64).default([]),
  priority: z.string().min(1).max(32).optional(),
}).strict();
export type CardFacts = z.infer<typeof cardFactsSchema>;

// Publishing policy for one run. `autoMerge` defaults false: a merge is an
// operator act, so enabling it is a visible config change, never a default.
export const prSettingsSchema = z.object({
  base: z.string().min(1).max(255).default("master"),
  branchPrefix: z.string().max(64).default("hatchet/"),
  autoMerge: z.boolean().default(false),
}).strict();
export type PrSettings = z.infer<typeof prSettingsSchema>;

// Spelled out rather than `.default({})`: the schema's default must be the
// parsed shape, and both the workflow input and the operator config reuse it.
export const defaultPrSettings: PrSettings = Object.freeze({
  base: "master",
  branchPrefix: "hatchet/",
  autoMerge: false,
});

// One card owns one branch, derived from its id so a re-run converges on the
// same branch and the same pull request instead of opening a second one.
export function prBranchForCard(cardId: string, prefix = "hatchet/"): string {
  const slug = cardId
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^[-.]+|[-.]+$/g, "")
    .replace(/\.lock$/, "-lock")
    .slice(0, 180);
  if (slug.length === 0) throw new Error(`cardId does not yield a usable branch name: ${cardId}`);
  return `${prefix}${slug}`;
}

export const prWorkflowInputSchema = z.object({
  version: z.literal(1),
  cardId: z.string().min(1).max(256),
  repository: z.string().min(1).max(512),
  headSha: shaSchema,
  recipePaths: recipePathsSchema,
  cwd: z.string().min(1),
  task: z.string().min(1),
  card: cardFactsSchema,
  triggerSource: triggerSourceSchema,
  // Defaulted so a state file written before publishing existed still replays.
  pr: prSettingsSchema.default(defaultPrSettings),
}).strict();

export type PrWorkflowInput = z.infer<typeof prWorkflowInputSchema>;

// A pull request Hatchet owns for one card. `branch` is derived from the card,
// never from the operator's current checkout, so a ready-queue run cannot
// publish onto whatever branch a worktree happened to be sitting on.
export const prRefSchema = z.object({
  number: z.number().int().positive(),
  url: z.string().url(),
  branch: z.string().min(1).max(255),
  base: z.string().min(1).max(255),
}).strict();
export type PrRef = z.infer<typeof prRefSchema>;

// CI truth as GitHub reports it, never as a stage claims it. `none` means no
// checks are configured, which is NOT green - a repository with no CI cannot
// satisfy a merge precondition by having nothing to fail.
export const checkConclusionSchema = z.enum(["green", "red", "pending", "none"]);
export type CheckConclusion = z.infer<typeof checkConclusionSchema>;

export const failingCheckSchema = z.object({
  name: z.string().min(1).max(256),
  summary: z.string().max(4_000).default(""),
}).strict();

export const checkStatusSchema = z.object({
  conclusion: checkConclusionSchema,
  headSha: shaSchema,
  failing: z.array(failingCheckSchema).max(50).default([]),
}).strict().superRefine((status, context) => {
  if (status.conclusion === "red" && status.failing.length === 0) {
    context.addIssue({ code: "custom", message: "a red check status must name at least one failing check" });
  }
  if (status.conclusion !== "red" && status.failing.length > 0) {
    context.addIssue({ code: "custom", message: "only a red check status may carry failing checks" });
  }
});
export type CheckStatus = z.infer<typeof checkStatusSchema>;

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
  // The stage's own words, published verbatim to the pull request by
  // deterministic code. The agent owns the judgment; it never owns the posting.
  findings: z.string().max(20_000).optional(),
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
  "merged",
  "awaiting_operator_approval",
  "review_blocked",
  "verification_failed",
]);
export type TerminalState = z.infer<typeof terminalStateSchema>;

// `mergePerformed` stopped being `literal(false)` when the verifier gained the
// authority to merge. The guarantee did not weaken into a comment: the schema
// now refuses any packet that claims a merge without a pull request and a
// GitHub-reported green check status recorded alongside it.
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
  pr: prRefSchema.optional(),
  checks: checkStatusSchema.optional(),
  mergePerformed: z.boolean(),
  operatorApprovalRequired: z.boolean(),
}).superRefine((packet, context) => {
  const merged = packet.state === "merged";
  if (merged !== packet.mergePerformed) {
    context.addIssue({ code: "custom", message: "state 'merged' and mergePerformed must agree" });
  }
  if (packet.mergePerformed === packet.operatorApprovalRequired) {
    context.addIssue({ code: "custom", message: "a merged packet needs no approval; an unmerged one does" });
  }
  if (!packet.mergePerformed) return;
  if (!packet.pr) {
    context.addIssue({ code: "custom", message: "a merged packet must record the pull request it merged" });
  }
  if (packet.checks?.conclusion !== "green") {
    context.addIssue({ code: "custom", message: "a merged packet must record a green GitHub check status" });
  }
  // Green for WHICH commit. Without this the packet could authorize merging
  // `finalHeadSha` on the strength of a stale green status for an older SHA -
  // exactly the window a fix round opens when it lands a new commit.
  if (packet.checks && packet.checks.headSha.toLowerCase() !== packet.finalHeadSha.toLowerCase()) {
    context.addIssue({ code: "custom", message: "the recorded check status must be for finalHeadSha" });
  }
});
export type EvidencePacket = z.infer<typeof evidencePacketSchema>;
