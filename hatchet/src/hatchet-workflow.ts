import { NonRetryableError, type DurableContext, type HatchetClient as Hatchet } from "@hatchet-dev/typescript-sdk/v1/index.js";
import { evidencePacketSchema, prWorkflowInputSchema, type EvidencePacket, type PrWorkflowInput } from "./contracts.js";
import { DeterministicInputError, TransientRunnerError } from "./errors.js";
import { runPrWorkflow } from "./pr-workflow.js";

export const workflowName = "omp-pr-canary-v1";

export function declarePrWorkflow(client: Hatchet) {
  return client.durableTask<PrWorkflowInput, EvidencePacket>({
    name: workflowName,
    inputValidator: prWorkflowInputSchema,
    // INERT ON THE DEPLOYED ENGINE. hatchet-lite v0.94.10 accepts this field
    // and ignores it: a live probe registering one workflow with `ttl` and one
    // with `status`, then firing the same key twice, produced two distinct run
    // ids and no collision error in both cases. The SDK's types advertise the
    // feature regardless, so type-checking proves nothing here.
    //
    // Declared anyway because it is the correct configuration and becomes the
    // real enforcement the moment the engine is upgraded. Until then admission
    // is `checkInFlight` plus `withDispatchLock` in trigger-service.ts. Re-run
    // that probe before deleting the lock.
    //
    // `status` is the right strategy: the key lives only while the run is
    // non-terminal, so a COMPLETED, FAILED, or CANCELLED run releases its card.
    //
    // This replaces a hand-rolled filesystem lock keyed on `cardId:HEAD`. That
    // key was written on dispatch and never removed, so a run that failed
    // BEFORE committing left the key on disk with HEAD unmoved — and the card
    // could never be admitted again. What actually fixes that today is not this
    // field but `findInFlightRun`: asking the engine which runs are live means
    // a FAILED run stops holding its card, because it is no longer live.
    //
    // HEAD is deliberately out of the key. Including it meant a commit landing
    // mid-run minted a NEW key and started a SECOND run against the same
    // worktree, which is how cards died on stale-head collisions. A card is one
    // unit of work; a commit arriving mid-run belongs to the run already
    // holding it.
    idempotency: {
      strategy: "status",
      expression: "input.cardId",
      // A worker that dies without reporting terminal would otherwise hold its
      // card forever. This is the backstop, set past executionTimeout so it
      // never evicts a run that is merely slow.
      fallbackTtlMs: 73 * 60 * 60 * 1000,
    },
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
        return evidencePacketSchema.parse(await runPrWorkflow(input, ctx.workflowRunId(), ctx.abortController.signal));
      } catch (error) {
        if (error instanceof DeterministicInputError || error instanceof TransientRunnerError) {
          throw new NonRetryableError(error.message);
        }
        throw error;
      }
    },
  });
}

