import { readFile, stat } from "node:fs/promises";
import { setTimeout as delay } from "node:timers/promises";
import { z } from "zod";
import { readOperatorConfig } from "./config.js";
import { triggerConfiguredWorkflow } from "./trigger-service.js";

const cardSchema = z.object({
  id: z.string(),
  status: z.string(),
  headSha: z.string().regex(/^[0-9a-f]{40}$/i).optional(),
});
const responseSchema = z.union([cardSchema, z.object({ card: cardSchema }).transform(({ card }) => card)]);
const operatorConfig = await readOperatorConfig();
if (!operatorConfig.powder) throw new Error("operator config powder section is required");

let authorization: string | undefined;
if (operatorConfig.powder.apiTokenFile) {
  const metadata = await stat(operatorConfig.powder.apiTokenFile);
  if ((metadata.mode & 0o077) !== 0) throw new Error("Powder API token file must have mode 0600");
  authorization = `Bearer ${(await readFile(operatorConfig.powder.apiTokenFile, "utf8")).trim()}`;
}

async function reconcileOnce(): Promise<object> {
  const url = new URL(`/api/v1/cards/${encodeURIComponent(operatorConfig.cardId)}`, operatorConfig.powder!.baseUrl);
  const headers = new Headers();
  if (authorization) headers.set("authorization", authorization);
  const response = await fetch(url, {
    headers,
    signal: AbortSignal.timeout(10_000),
  });
  if (!response.ok) throw new Error(`Powder card read failed with HTTP ${response.status}`);
  const card = responseSchema.parse(await response.json());
  if (card.id !== operatorConfig.cardId) throw new Error("Powder returned a different card");
  if (card.status !== operatorConfig.powder!.readyStatus) {
    return { cardId: card.id, status: card.status, triggered: false };
  }
  const result = await triggerConfiguredWorkflow(operatorConfig, "reconciler", card.headSha);
  return { cardId: card.id, status: card.status, triggered: true, ...result };
}

if (process.argv.includes("--once")) {
  process.stdout.write(`${JSON.stringify(await reconcileOnce())}\n`);
} else {
  const intervalMs = Number.parseInt(process.env.HATCHET_RECONCILE_INTERVAL_MS ?? "60000", 10);
  if (!Number.isSafeInteger(intervalMs) || intervalMs < 5_000) {
    throw new Error("HATCHET_RECONCILE_INTERVAL_MS must be an integer of at least 5000");
  }
  process.stdout.write(`Powder reconciler ready; interval=${intervalMs}ms\n`);
  while (true) {
    try {
      process.stdout.write(`${JSON.stringify(await reconcileOnce())}\n`);
    } catch {
      process.stderr.write("Powder reconciliation failed\n");
    }
    await delay(intervalMs);
  }
}
