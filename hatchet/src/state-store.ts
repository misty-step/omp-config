import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { z } from "zod";
import { evidencePacketSchema, prWorkflowInputSchema, stageResultSchema, type EvidencePacket, type PrWorkflowInput, type StageResult } from "./contracts.js";
import { executionRoot } from "./config.js";
import { DeterministicInputError } from "./errors.js";

const workflowStateSchema = z.object({
  version: z.literal(2),
  inputHash: z.string().regex(/^[0-9a-f]{64}$/),
  input: prWorkflowInputSchema,
  stages: z.array(stageResultSchema),
  final: evidencePacketSchema.optional(),
});

export type WorkflowState = z.infer<typeof workflowStateSchema>;

export function canonicalInputHash(input: PrWorkflowInput): string {
  return createHash("sha256").update(JSON.stringify(input)).digest("hex");
}

function executionPath(input: PrWorkflowInput): string {
  const keyHash = createHash("sha256").update(input.idempotencyKey).digest("hex");
  return resolve(executionRoot, `${keyHash}.json`);
}

export async function loadWorkflowState(input: PrWorkflowInput): Promise<WorkflowState> {
  const inputHash = canonicalInputHash(input);
  const path = executionPath(input);
  try {
    const decoded: unknown = JSON.parse(await readFile(path, "utf8"));
    if (
      typeof decoded === "object"
      && decoded !== null
      && "version" in decoded
      && decoded.version === 1
    ) {
      throw new DeterministicInputError(
        "workflow state uses the legacy single-recipe contract; use a new idempotency key",
      );
    }
    const state = workflowStateSchema.parse(decoded);
    if (state.inputHash !== inputHash) {
      throw new DeterministicInputError("idempotency key reused with different workflow input");
    }
    return state;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return { version: 2, inputHash, input, stages: [] };
    }
    throw error;
  }
}

export async function saveWorkflowState(state: WorkflowState): Promise<void> {
  await mkdir(executionRoot, { recursive: true, mode: 0o700 });
  const path = executionPath(state.input);
  const temporary = `${path}.${randomUUID()}.tmp`;
  await writeFile(temporary, `${JSON.stringify(state)}\n`, { encoding: "utf8", mode: 0o600, flag: "wx" });
  await rename(temporary, path);
}

export function findStage(state: WorkflowState, stage: StageResult["stage"], round: number): StageResult | undefined {
  return state.stages.find((entry) => entry.stage === stage && entry.round === round);
}

export async function checkpointStage(state: WorkflowState, result: StageResult): Promise<void> {
  const existing = findStage(state, result.stage, result.round);
  if (existing) return;
  state.stages.push(result);
  await saveWorkflowState(state);
}

export async function checkpointFinal(state: WorkflowState, packet: EvidencePacket): Promise<void> {
  state.final = packet;
  await saveWorkflowState(state);
}
