import { createHatchetClient } from "./hatchet-client.js";
import { declarePrWorkflow } from "./hatchet-workflow.js";
import { runWorktreeGc, worktreeGcPolicy } from "./worktree-gc.js";

const client = await createHatchetClient();
const workflow = declarePrWorkflow(client);
const worker = await client.worker("omp-pr-canary-worker", { slots: 1, durableSlots: 1, handleKill: false, workflows: [workflow] });
const worktreePolicy = worktreeGcPolicy();
const cleanupWorktrees = async (): Promise<void> => {
  try {
    const report = await runWorktreeGc(worktreePolicy);
    process.stdout.write(`OMP worktree GC: scanned=${report.scanned} removed=${report.removed.length} remaining=${report.remainingCount} bytes=${report.remainingBytes} budgetExceeded=${report.budgetExceeded}\n`);
  } catch (error) {
    process.stderr.write(`OMP worktree GC failed: ${error instanceof Error ? error.message : String(error)}\n`);
  }
};
void cleanupWorktrees();
const cleanupTimer = setInterval(() => { void cleanupWorktrees(); }, worktreePolicy.intervalMs);
cleanupTimer.unref();

let stopping = false;
const stop = async () => {
  if (stopping) return;
  stopping = true;
  clearInterval(cleanupTimer);
  await worker.stop();
};
process.once("SIGINT", () => { void stop(); });
process.once("SIGTERM", () => { void stop(); });

const running = worker.start();
await worker.waitUntilReady(30_000);
process.stdout.write("Hatchet worker ready\n");
await running;
