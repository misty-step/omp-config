import { createHatchetClient } from "./hatchet-client.js";
import { declarePrWorkflow } from "./hatchet-workflow.js";

const client = await createHatchetClient();
const workflow = declarePrWorkflow(client);
const worker = await client.worker("omp-pr-canary-worker", { slots: 1, durableSlots: 1, handleKill: false, workflows: [workflow] });

let stopping = false;
const stop = async () => {
  if (stopping) return;
  stopping = true;
  await worker.stop();
};
process.once("SIGINT", () => { void stop(); });
process.once("SIGTERM", () => { void stop(); });

const running = worker.start();
await worker.waitUntilReady(30_000);
process.stdout.write("Hatchet worker ready\n");
await running;
