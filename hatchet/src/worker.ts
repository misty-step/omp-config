import { createHatchetClient } from "./hatchet-client.js";
import { declarePrWorkflow } from "./hatchet-workflow.js";
import { runWorktreeGc, startWorktreeGcLoop, worktreeGcPolicy } from "./worktree-gc.js";

const client = await createHatchetClient();
const workflow = declarePrWorkflow(client);
const worker = await client.worker("omp-pr-canary-worker", { slots: 1, durableSlots: 1, handleKill: false, workflows: [workflow] });
const worktreePolicy = worktreeGcPolicy();
const gcLoop = startWorktreeGcLoop(worktreePolicy, {
  runGc: runWorktreeGc,
  onReport: (report) => {
    process.stdout.write(`OMP worktree GC: scanned=${report.scanned} removed=${report.removed.length} remaining=${report.remainingCount} bytes=${report.remainingBytes} budgetExceeded=${report.budgetExceeded}${report.errors.length > 0 ? ` errors=${report.errors.length}` : ""}\n`);
    for (const error of report.errors) process.stderr.write(`OMP worktree GC error: ${error}\n`);
  },
  onSkip: (reason) => process.stderr.write(`OMP worktree GC: skipping tick: ${reason}\n`),
  onError: (error) => process.stderr.write(`OMP worktree GC failed: ${error instanceof Error ? error.message : String(error)}\n`),
});

let stopping = false;
const stop = async (): Promise<void> => {
  if (stopping) return;
  stopping = true;
  gcLoop.stop();
  await worker.stop();
};
process.once("SIGINT", () => { void stop(); });
process.once("SIGTERM", () => { void stop(); });

const running = worker.start();
await worker.waitUntilReady(30_000);
process.stdout.write("Hatchet worker ready\n");
await running;
