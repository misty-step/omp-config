import { describe, expect, it } from "vitest";
import { mkdir, rm, utimes, writeFile } from "node:fs/promises";
import { mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { gcWorktrees, worktreeGcPolicy } from "../src/worktree-gc.js";

async function makeWorktree(root: string, name: string, bytes: number): Promise<string> {
  const path = join(root, name);
  await mkdir(path, { recursive: true });
  await writeFile(join(path, ".git"), "gitdir: /repo/.git/worktrees/test\n");
  await writeFile(join(path, "payload"), "x".repeat(bytes));
  return path;
}

describe("OMP isolated worktree GC", () => {
  it("removes clean orphaned worktrees after the grace window", async () => {
    const root = await mkdtemp(join(tmpdir(), "omp-wt-gc-"));
    try {
      const oldPath = await makeWorktree(root, "old", 20);
      const freshPath = await makeWorktree(root, "fresh", 20);
      const nowMs = Date.now();
      const oldTime = new Date(nowMs - 10_000);
      await utimes(oldPath, oldTime, oldTime);

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: async () => true,
        isInUse: async () => false,
      });

      expect(report.scanned).toBe(2);
      expect(report.removed).toEqual([oldPath]);
      expect(report.remainingCount).toBe(1);
      expect(report.budgetExceeded).toBe(false);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  it("enforces the count budget while preserving dirty or active worktrees", async () => {
    const root = await mkdtemp(join(tmpdir(), "omp-wt-gc-"));
    try {
      const first = await makeWorktree(root, "first", 20);
      const second = await makeWorktree(root, "second", 20);
      const dirty = await makeWorktree(root, "dirty", 20);
      const active = await makeWorktree(root, "active", 20);
      const nowMs = Date.now();
      const firstTime = new Date(nowMs - 10_000);
      const secondTime = new Date(nowMs - 5_000);
      await utimes(first, firstTime, firstTime);
      await utimes(second, secondTime, secondTime);

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 60 * 60_000,
        maxCount: 2,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: async path => path !== dirty,
        isInUse: async path => path === active,
      });

      expect(report.removed).toEqual([first, second]);
      expect(report.remainingCount).toBe(2);
      expect(report.budgetExceeded).toBe(false);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  it("uses bounded defaults and accepts explicit policy environment overrides", () => {
    expect(worktreeGcPolicy({
      OMP_WORKTREE_ROOT: "/tmp/omp-wt",
      OMP_WORKTREE_GC_INTERVAL_MS: "60000",
      OMP_WORKTREE_GC_STALE_AFTER_MS: "120000",
      OMP_WORKTREE_MAX_COUNT: "3",
      OMP_WORKTREE_MAX_BYTES: "4096",
    })).toEqual({
      root: "/tmp/omp-wt",
      intervalMs: 60_000,
      staleAfterMs: 120_000,
      maxCount: 3,
      maxBytes: 4096,
    });
  });
});
