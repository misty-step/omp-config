import { prWorkflowInputSchema, type PrWorkflowInput, type TriggerSource } from "./contracts.js";
import { currentHeadSha } from "./git-head.js";
import { createHatchetClient } from "./hatchet-client.js";
import { declarePrWorkflow } from "./hatchet-workflow.js";
import { withIdempotentTrigger } from "./idempotency.js";
import type { OperatorConfig } from "./config.js";
import { DeterministicInputError } from "./errors.js";

export type TriggerResult = {
  runId: string;
  duplicate: boolean;
  idempotencyKey: string;
};

export async function triggerConfiguredWorkflow(
  config: OperatorConfig,
  source: TriggerSource,
  requestedHeadSha?: string,
  requestedIdempotencyKey?: string,
): Promise<TriggerResult> {
  const requestedHead = requestedHeadSha?.toLowerCase();
  const initialHead = requestedIdempotencyKey ? undefined : await currentHeadSha(config.cwd);
  const idempotencyKey = requestedIdempotencyKey ?? `${config.cardId}:${requestedHead ?? initialHead}`;
  const expectedAdmission = JSON.stringify({
    version: config.version,
    cardId: config.cardId,
    repository: config.repository,
    recipePaths: config.recipePaths,
    cwd: config.cwd,
    task: config.task,
    idempotencyKey,
  });

  const { mapping, duplicate } = await withIdempotentTrigger(
    idempotencyKey,
    async () => {
      const actualHeadSha = await currentHeadSha(config.cwd);
      const headSha = requestedHead ?? initialHead ?? actualHeadSha;
      if (headSha !== actualHeadSha) {
        throw new DeterministicInputError(
          `trigger rejected stale head: requested ${headSha}, current ${actualHeadSha}`,
        );
      }
      return prWorkflowInputSchema.parse({
        version: 1,
        cardId: config.cardId,
        repository: config.repository,
        headSha,
        recipePaths: config.recipePaths,
        cwd: config.cwd,
        task: config.task,
        idempotencyKey,
        triggerSource: source,
        requestedAt: new Date().toISOString(),
      });
    },
    (admittedInput: PrWorkflowInput) => {
      const admitted = JSON.stringify({
        version: admittedInput.version,
        cardId: admittedInput.cardId,
        repository: admittedInput.repository,
        recipePaths: admittedInput.recipePaths,
        cwd: admittedInput.cwd,
        task: admittedInput.task,
        idempotencyKey: admittedInput.idempotencyKey,
      });
      if (admitted !== expectedAdmission || (requestedHead && requestedHead !== admittedInput.headSha)) {
        throw new DeterministicInputError("idempotency key reused with different trigger input");
      }
    },
    async (input: PrWorkflowInput) => {
      const client = await createHatchetClient();
      const workflow = declarePrWorkflow(client);
      const reference = await workflow.runNoWait(input, {
        additionalMetadata: {
          card_id: input.cardId,
          head_sha: input.headSha,
          idempotency_key: input.idempotencyKey,
          trigger_source: input.triggerSource,
        },
      });
      return await reference.runId;
    },
  );
  return { runId: mapping.runId, duplicate, idempotencyKey };
}
