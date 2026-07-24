import { setTimeout as delay } from "node:timers/promises";
import { readOperatorConfig } from "./config.js";
import { createPowderCardReader } from "./powder-client.js";
import { triggerConfiguredWorkflow } from "./trigger-service.js";

const operatorConfig = await readOperatorConfig();
if (!operatorConfig.powder) throw new Error("operator config powder section is required");
const readPowderCard = await createPowderCardReader(operatorConfig);

async function reconcileOnce(): Promise<object> {
  const card = await readPowderCard();
  if (card.status !== operatorConfig.powder!.readyStatus) {
    return { cardId: card.id, status: card.status, triggered: false };
  }
  const result = await triggerConfiguredWorkflow(operatorConfig, "reconciler");
  return { cardId: card.id, status: card.status, triggered: !result.duplicate, ...result };
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
