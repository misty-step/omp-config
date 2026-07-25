import { setTimeout as delay } from "node:timers/promises";
import { createHatchetClient } from "../hatchet-client.js";

const args = process.argv.slice(2);
const flagIndex = args.indexOf("--run-id");
const runId = flagIndex === -1 ? args[0] : args[flagIndex + 1];
if (!runId) {
  throw new Error("usage: npm run cancel -- --run-id RUN_ID");
}

const client = await createHatchetClient();
await client.runs.cancel({ ids: [runId] });
let status = "UNKNOWN";
for (let attempt = 0; attempt < 100; attempt += 1) {
  status = await client.runs.get_status(runId);
  if (["CANCELLED", "COMPLETED", "FAILED"].includes(status)) break;
  await delay(100);
}
process.stdout.write(`${JSON.stringify({ runId, status, cancellationRequested: true })}\n`);
