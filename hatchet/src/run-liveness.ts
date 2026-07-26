import { V1TaskStatus } from "@hatchet-dev/typescript-sdk/clients/rest/generated/data-contracts.js";
import { createHatchetClient } from "./hatchet-client.js";
import { workflowName } from "./hatchet-workflow.js";

/**
 * The run currently occupying a card, as the engine sees it.
 *
 * `headSha` is the commit that run pinned when it was admitted. A caller whose
 * own HEAD has moved past it is looking at work that has not started yet, and
 * this is the only field that lets it say so.
 */
export type LiveRun = {
  runId: string;
  headSha?: string;
};

/**
 * Runs that have not reached a terminal status. Hatchet's own enum is the
 * authority; COMPLETED, FAILED, and CANCELLED are terminal and their cards are
 * free to run again immediately.
 *
 * This is the whole wedge fix. The previous implementation asked a local
 * `cardId:HEAD` mapping file, which was written on dispatch and never removed,
 * so a run that failed *before* committing left its key on disk with HEAD
 * unmoved and the card could never be admitted again. Asking the engine
 * instead means a failed run releases its card by definition.
 */
const IN_FLIGHT = [V1TaskStatus.QUEUED, V1TaskStatus.RUNNING];

/**
 * The in-flight run for `cardId`, or undefined when the card is free.
 *
 * Runs are tagged with `card_id` at dispatch, so this is one indexed query
 * against the engine rather than a scan of local state. There is deliberately
 * no local fallback: local files cannot observe a crashed worker, and treating
 * their staleness as liveness is what deadlocked cards before.
 */
export async function findInFlightRun(cardId: string): Promise<LiveRun | undefined> {
  const client = await createHatchetClient();
  const { rows } = await client.runs.list({
    additionalMetadata: { card_id: cardId },
    workflowNames: [workflowName],
    statuses: IN_FLIGHT,
    limit: 1,
  });
  const run = rows?.[0];
  if (!run) return undefined;
  const metadata = run.additionalMetadata;
  const headSha =
    typeof metadata === "object" && metadata !== null
      ? (metadata as Record<string, unknown>).head_sha
      : undefined;
  return {
    runId: run.taskExternalId ?? run.metadata.id,
    ...(typeof headSha === "string" ? { headSha } : {}),
  };
}
