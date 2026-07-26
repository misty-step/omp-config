import { createHatchetClient } from "./hatchet-client.js";
import { declarePrWorkflow } from "./hatchet-workflow.js";
import { runWorktreeGc, worktreeGcPolicy } from "./worktree-gc.js";

const client = await createHatchetClient();
const workflow = declarePrWorkflow(client);
const worker = await client.worker("omp-pr-canary-worker", { slots: 1, durableSlots: 1, handleKill: false, workflows: [workflow] });
const worktreePolicy = worktreeGcPolicy();
let gcBusy = false;
let gcTimer: NodeJS.Timeout | undefined;
const cleanupWorktrees = async (): Promise<void> => {
  if (gcBusy) {
    process.stderr.write("OMP worktree GC: previous run still in progress; skipping this tick\n");
    return;
  }
  gcBusy = true;
  try {
    const report = await runWorktreeGc(worktreePolicy);
    process.stdout.write(`OMP worktree GC: scanned=${report.scanned} removed=${report.removed.length} remaining=${report.remainingCount} bytes=${report.remainingBytes} budgetExceeded=${report.budgetExceeded}${report.errors.length > 0 ? ` errors=${report.errors.length}` : ""}\n`);
    for (const error of report.errors) process.stderr.write(`OMP worktree GC error: ${error}\n`);
  } catch (error) {
    process.stderr.write(`OMP worktree GC failed: ${error instanceof Error ? error.message : String(error)}\n`);
  } finally {
    gcBusy = false;
  }
};
void cleanupWorktrees();
const scheduleGc = (): void => {
  gcTimer = setTimeout(() => {
    void cleanupWorktrees().finally(scheduleGc);
  }, worktreePolicy.intervalMs);
  gcTimer.unref();
};
scheduleGc();

let stopping = false;
const stop = async (): Promise<void> => {
  if (stopping) return;
  stopping = true;
  clearTimeout(gcTimer);
  await worker.stop();
};
process.once("SIGINT", () => { void stop(); });
process.once("SIGTERM", () => { void stop(); });

const running = worker.start();
await worker.waitUntilReady(30_000);
process.stdout.write("Hatchet worker ready\n");
await running;
