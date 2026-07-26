import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { resolve } from "node:path";
import { z } from "zod";
import { evidencePacketSchema, stageResultSchema, type EvidencePacket, type StageResult } from "./contracts.js";
import { executionRoot } from "./config.js";

/**
 * Stage checkpoints for one run.
 *
 * Hatchet wraps `runPrWorkflow` in a single durable task, so the engine knows
 * whether the run is alive but not which stage last committed. That is the only
 * thing this file exists to answer; run status, admission, and card state all
 * belong to the engine and to Powder.
 */
const workflowStateSchema = z.object({
  version: z.literal(3),
  runId: z.string().min(1),
  stages: z.array(stageResultSchema),
  final: evidencePacketSchema.optional(),
});

type WorkflowState = z.infer<typeof workflowStateSchema>;
export type { WorkflowState };

/**
 * Checkpoints are keyed by run, not by input.
 *
 * A Hatchet task retry resumes the same run id, so it correctly picks up the
 * stages already committed. A fresh trigger gets a new run id and therefore a
 * clean slate — which is the point: the previous scheme keyed on the trigger's
 * idempotency key, so a card retried at an unchanged HEAD would silently
 * inherit the failed run's checkpoints and skip stages that never succeeded.
 */
function executionPath(runId: string): string {
  if (!/^[A-Za-z0-9._-]+$/.test(runId)) throw new Error(`unsafe run id: ${runId}`);
  return resolve(executionRoot, `${runId}.json`);
}

export async function loadWorkflowState(runId: string): Promise<WorkflowState> {
  try {
    return workflowStateSchema.parse(JSON.parse(await readFile(executionPath(runId), "utf8")));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return { version: 3, runId, stages: [] };
    throw error;
  }
}

export async function saveWorkflowState(state: WorkflowState): Promise<void> {
  await mkdir(executionRoot, { recursive: true, mode: 0o700 });
  const path = executionPath(state.runId);
  const temporary = `${path}.${randomUUID()}.tmp`;
  try {
    await writeFile(temporary, `${JSON.stringify(state)}\n`, { encoding: "utf8", mode: 0o600, flag: "wx" });
    await rename(temporary, path);
  } catch (error) {
    // A failed rename otherwise leaves the temp file behind forever; the
    // execution directory had accumulated hundreds of them.
    await rm(temporary, { force: true });
    throw error;
  }
}

export function findStage(state: WorkflowState, stage: StageResult["stage"], round: number): StageResult | undefined {
  return state.stages.find((entry) => entry.stage === stage && entry.round === round);
}

export async function checkpointStage(state: WorkflowState, result: StageResult): Promise<void> {
  if (findStage(state, result.stage, result.round)) return;
  state.stages.push(result);
  await saveWorkflowState(state);
}

export async function checkpointFinal(state: WorkflowState, packet: EvidencePacket): Promise<void> {
  state.final = packet;
  await saveWorkflowState(state);
}
