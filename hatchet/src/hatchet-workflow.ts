import { NonRetryableError, type DurableContext, type HatchetClient as Hatchet } from "@hatchet-dev/typescript-sdk/v1/index.js";
import { evidencePacketSchema, prWorkflowInputSchema, type EvidencePacket, type PrWorkflowInput } from "./contracts.js";
import { DeterministicInputError, TransientRunnerError } from "./errors.js";
import { runPrWorkflow } from "./pr-workflow.js";

export const workflowName = "omp-pr-canary-v1";

export function declarePrWorkflow(client: Hatchet) {
  return client.durableTask<PrWorkflowInput, EvidencePacket>({
    name: workflowName,
    inputValidator: prWorkflowInputSchema,
    // Hatchet-level task retries exist only for infrastructure hiccups
    // (engine restart, transport blip) outside our own control. Every
    // recipe-agent failure already runs through its own bounded, more
    // targeted retry budget: invokeRunnerWithRetry gives a schema-invalid or
    // otherwise transient stage terminal up to 3 attempts, and runPrWorkflow
    // caps review/remediate cycles at maxFixRounds=2. By the time either of
    // those escapes to this boundary it has already exhausted its bounded
    // budget, so retrying the *whole* task here would silently re-run the
    // identical exhausted budget rather than recover anything — exactly the
    // "one review runs indefinitely" failure mode. Foreclose both classes
    // explicitly; the residual `retries: 2` covers everything else.
    retries: 2,
    backoff: { factor: 2, maxSeconds: 10 },
    // Outer bound over every stage of one card, including review/remediate
    // rounds. Agents run unattended for hours, so this exists only to reclaim
    // a worker slot from a workflow that will never finish.
    executionTimeout: "72h",
    // The worker runs one slot, so a second card waits behind a run that may
    // take hours. Without this the queued card dies on the SDK's short default
    // long before a slot frees.
    scheduleTimeout: "72h",
    fn: async (input: PrWorkflowInput, ctx: DurableContext<PrWorkflowInput>) => {
      try {
        return evidencePacketSchema.parse(await runPrWorkflow(input, ctx.abortController.signal));
      } catch (error) {
        if (error instanceof DeterministicInputError || error instanceof TransientRunnerError) {
          throw new NonRetryableError(error.message);
        }
        throw error;
      }
    },
  });
}

