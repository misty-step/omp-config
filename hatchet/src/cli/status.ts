import { createHatchetClient } from "../hatchet-client.js";

const args = process.argv.slice(2);
const flagIndex = args.indexOf("--run-id");
const runId = flagIndex === -1 ? args[0] : args[flagIndex + 1];
if (!runId) {
  throw new Error("usage: npm run status -- --run-id RUN_ID");
}

const client = await createHatchetClient();
const detail = await client.runs.get(runId);
process.stdout.write(`${JSON.stringify({
  runId,
  status: detail.run.status,
  startedAt: detail.run.startedAt ?? null,
  finishedAt: detail.run.finishedAt ?? null,
  output: detail.run.output,
})}\n`);
