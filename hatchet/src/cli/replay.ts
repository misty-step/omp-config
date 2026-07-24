import { setTimeout as delay } from "node:timers/promises";
import { createHatchetClient } from "../hatchet-client.js";

const args = process.argv.slice(2);
const flagIndex = args.indexOf("--run-id");
const runId = flagIndex === -1 ? args[0] : args[flagIndex + 1];
if (!runId) {
  throw new Error("usage: npm run replay -- --run-id RUN_ID");
}

// Replay re-executes the same Hatchet run id with its original input (same
// idempotency key), so runPrWorkflow resumes from whatever stages the
// execution-state store already checkpointed instead of redoing completed
// work. Use this to finish a run that failed for an adapter-level reason
// (not a genuine card-level review verdict) after the adapter is fixed.
const client = await createHatchetClient();
await client.runs.replay({ ids: [runId] });
let status = "UNKNOWN";
for (let attempt = 0; attempt < 100; attempt += 1) {
  status = await client.runs.get_status(runId);
  if (status !== "FAILED" && status !== "UNKNOWN") break;
  await delay(100);
}
process.stdout.write(`${JSON.stringify({ runId, status, replayRequested: true })}\n`);
