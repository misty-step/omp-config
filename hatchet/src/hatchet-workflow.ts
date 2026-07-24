import { NonRetryableError, type DurableContext, type HatchetClient as Hatchet } from "@hatchet-dev/typescript-sdk/v1/index.js";
import { evidencePacketSchema, prWorkflowInputSchema, type EvidencePacket, type PrWorkflowInput } from "./contracts.js";
import { DeterministicInputError } from "./errors.js";
import { runPrWorkflow } from "./pr-workflow.js";

export const workflowName = "omp-pr-canary-v1";

export function declarePrWorkflow(client: Hatchet) {
  return client.durableTask<PrWorkflowInput, EvidencePacket>({
    name: workflowName,
    inputValidator: prWorkflowInputSchema,
    retries: 2,
    backoff: { factor: 2, maxSeconds: 10 },
    executionTimeout: "2h",
    fn: async (input: PrWorkflowInput, ctx: DurableContext<PrWorkflowInput>) => {
      try {
        return evidencePacketSchema.parse(await runPrWorkflow(input, ctx.abortController.signal));
      } catch (error) {
        if (error instanceof DeterministicInputError) {
          throw new NonRetryableError(error.message);
        }
        throw error;
      }
    },
  });
}

