import { describe, expect, it, vi } from "vitest";
import { mkdir, mkdtemp, realpath, readdir, rm, symlink, utimes, writeFile } from "node:fs/promises";
import { execFile as execFileCallback } from "node:child_process";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { promisify } from "node:util";
import {
  gcWorktrees,
  startWorktreeGcLoop,
  worktreeGcPolicy,
  type CleanResult,
  type UseResult,
  type WorktreeGcReport,
} from "../src/worktree-gc.js";

const execFile = promisify(execFileCallback);

async function makeWorktree(root: string, name: string, bytes: number): Promise<string> {
  const path = join(root, name);
  await mkdir(path, { recursive: true });
  await writeFile(join(path, ".git"), "gitdir: /repo/.git/worktrees/test\n");
  await writeFile(join(path, "payload"), "x".repeat(bytes));
  return path;
}

/** Create a GC root that legitimately ends in `.omp/wt` (the allowlist shape), plus a cleanup fn. */
async function makeRoot(): Promise<{ root: string; cleanup: () => Promise<void> }> {
  const base = await mkdtemp(join(tmpdir(), "omp-wt-gc-"));
  const root = join(base, ".omp", "wt");
  await mkdir(root, { recursive: true });
  return { root, cleanup: () => rm(base, { recursive: true, force: true }) };
}

/** Recursively age every file/dir in a tree so the activity signal (max file mtime) is old. */
async function ageTree(path: string, nowMs: number, ageMs: number): Promise<void> {
  const time = new Date(nowMs - ageMs);
  const stack = [path];
  while (stack.length > 0) {
    const dir = stack.pop()!;
    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (entry.isSymbolicLink()) continue;
      const entryPath = join(dir, entry.name);
      try {
        await utimes(entryPath, time, time);
      } catch {
        // ignore entries we cannot touch
      }
      if (entry.isDirectory()) stack.push(entryPath);
    }
  }
  try {
    await utimes(path, time, time);
  } catch {
    // ignore
  }
}

const clean = async (): Promise<CleanResult> => "clean";
const notInUse = async (): Promise<UseResult> => ({ inUse: false });
const noopPrune = async (): Promise<void> => {};

const emptyReport: WorktreeGcReport = {
  root: "/tmp/.omp/wt",
  scanned: 0,
  removed: [],
  remainingCount: 0,
  remainingBytes: 0,
  budgetExceeded: false,
  errors: [],
};

describe("OMP isolated worktree GC", () => {
  it("removes clean orphaned worktrees after the grace window", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const oldPath = await makeWorktree(root, "old", 20);
      const freshPath = await makeWorktree(root, "fresh", 20);
      const nowMs = Date.now();
      await ageTree(oldPath, nowMs, 10_000);
      // fresh stays current

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: clean,
        isInUse: notInUse,
        prune: noopPrune,
      });

      expect(report.scanned).toBe(2);
      expect(report.removed).toEqual([oldPath]);
      expect(report.remainingCount).toBe(1);
      expect(report.budgetExceeded).toBe(false);
    } finally {
      await cleanup();
    }
  });

  it("enforces the count budget while preserving dirty or active worktrees", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const first = await makeWorktree(root, "first", 20);
      const second = await makeWorktree(root, "second", 20);
      const dirty = await makeWorktree(root, "dirty", 20);
      const active = await makeWorktree(root, "active", 20);
      const nowMs = Date.now();
      await ageTree(first, nowMs, 10_000);
      await ageTree(second, nowMs, 5_000);

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 60 * 60_000,
        maxCount: 2,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: async path => (path === dirty ? "dirty" : "clean"),
        isInUse: async path => (path === active ? { inUse: true } : { inUse: false }),
        prune: noopPrune,
      });

      expect(report.removed).toEqual([first, second]);
      expect(report.remainingCount).toBe(2);
      expect(report.budgetExceeded).toBe(false);
    } finally {
      await cleanup();
    }
  });

  it("evicts by byte budget alone when count is under limit and nothing is stale", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const big1 = await makeWorktree(root, "big1", 1000);
      const big2 = await makeWorktree(root, "big2", 1000);
      const nowMs = Date.now();
      await ageTree(big1, nowMs, 10_000);
      await ageTree(big2, nowMs, 5_000);

      // Two ~1035-byte trees, maxBytes=1500: one must go, the newer one stays.
      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 60 * 60_000,
        maxCount: 8,
        maxBytes: 1500,
      }, {
        nowMs,
        isClean: clean,
        isInUse: notInUse,
        prune: noopPrune,
      });

      expect(report.removed).toEqual([big1]);
      expect(report.remainingCount).toBe(1);
      expect(report.budgetExceeded).toBe(false);
    } finally {
      await cleanup();
    }
  });

  it("does not evict fresh worktrees when count is exactly at the budget boundary", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      await makeWorktree(root, "a", 20);
      await makeWorktree(root, "b", 20);
      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 60 * 60_000,
        maxCount: 2,
        maxBytes: 1_000_000,
      }, {
        nowMs: Date.now(),
        isClean: clean,
        isInUse: notInUse,
        prune: noopPrune,
      });

      expect(report.removed).toEqual([]);
      expect(report.remainingCount).toBe(2);
      expect(report.budgetExceeded).toBe(false);
    } finally {
      await cleanup();
    }
  });

  it("refuses a candidate that became a symlink before removal and records the error", async () => {
    const { root, cleanup } = await makeRoot();
    const outside = await mkdtemp(join(tmpdir(), "omp-wt-out-"));
    try {
      const target = await makeWorktree(root, "target", 20);
      const nowMs = Date.now();
      await ageTree(target, nowMs, 10_000);

      // During the eligibility isClean call, swap the real dir for a symlink escaping root.
      let swapped = false;
      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: async path => {
          if (!swapped && path === target) {
            swapped = true;
            await rm(target, { recursive: true, force: true });
            await symlink(outside, target, "dir");
          }
          return "clean";
        },
        isInUse: notInUse,
        prune: noopPrune,
      });

      expect(report.removed).toEqual([]);
      expect(report.errors.some(e => e.includes("symlink") || e.includes("non-directory"))).toBe(true);
    } finally {
      await cleanup();
      await rm(outside, { recursive: true, force: true });
    }
  });

  it("re-checks liveness immediately before removal and spares a tree that became active", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const target = await makeWorktree(root, "target", 20);
      const nowMs = Date.now();
      await ageTree(target, nowMs, 10_000);

      // Eligibility pass: not in use. Delete-time recheck: in use. Must not be removed.
      let calls = 0;
      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: clean,
        isInUse: async () => {
          calls += 1;
          // First call (eligibility) says free; second call (recheck) says in use.
          return calls === 1 ? { inUse: false } : { inUse: true };
        },
        prune: noopPrune,
      });

      expect(report.removed).toEqual([]);
      expect(report.remainingCount).toBe(1);
    } finally {
      await cleanup();
    }
  });

  it("re-checks cleanliness immediately before removal and spares a tree that became dirty", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const target = await makeWorktree(root, "target", 20);
      const nowMs = Date.now();
      await ageTree(target, nowMs, 10_000);

      let calls = 0;
      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: async () => {
          calls += 1;
          // First call (eligibility) clean; second call (recheck) dirty.
          return calls === 1 ? "clean" : "dirty";
        },
        isInUse: notInUse,
        prune: noopPrune,
      });

      expect(report.removed).toEqual([]);
      expect(report.remainingCount).toBe(1);
    } finally {
      await cleanup();
    }
  });

  it("treats a tree with unreadable git status as protected (fail-closed)", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const target = await makeWorktree(root, "unknown", 20);
      const nowMs = Date.now();
      await ageTree(target, nowMs, 10_000);

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 0,
        maxBytes: 0,
      }, {
        nowMs,
        isClean: async () => "unknown",
        isInUse: notInUse,
        prune: noopPrune,
      });

      expect(report.removed).toEqual([]);
      expect(report.budgetExceeded).toBe(true);
    } finally {
      await cleanup();
    }
  });

  it("protects a clean worktree that is in use even when stale and over budget", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const target = await makeWorktree(root, "busy", 20);
      const nowMs = Date.now();
      await ageTree(target, nowMs, 10_000);

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 0,
        maxBytes: 0,
      }, {
        nowMs,
        isClean: clean,
        isInUse: async () => ({ inUse: true }),
        prune: noopPrune,
      });

      expect(report.removed).toEqual([]);
      expect(report.budgetExceeded).toBe(true);
    } finally {
      await cleanup();
    }
  });

  it("prunes the parent worktree record in the parent repo after removal", async () => {
    const { root, cleanup } = await makeRoot();
    try {
      const target = await makeWorktree(root, "target", 20);
      const nowMs = Date.now();
      await ageTree(target, nowMs, 10_000);

      const pruned: string[] = [];
      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: clean,
        isInUse: notInUse,
        prune: async gitDir => { pruned.push(gitDir); },
      });

      expect(report.removed).toEqual([target]);
      // makeWorktree writes `gitdir: /repo/.git/worktrees/test`; parentGitDir resolves to /repo/.git.
      expect(pruned).toEqual(["/repo/.git"]);
    } finally {
      await cleanup();
    }
  });

  it("refuses to GC a root outside ~/.omp/wt unless explicitly allowlisted", async () => {
    const base = await mkdtemp(join(tmpdir(), "omp-wt-gc-"));
    try {
      const target = await makeWorktree(base, "a", 20);
      const nowMs = Date.now();
      await ageTree(target, nowMs, 10_000);

      // Refused: root does not end in `.omp/wt` and no allowlist.
      const refused = await gcWorktrees({
        root: base,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: clean,
        isInUse: notInUse,
        prune: noopPrune,
        allowedRoots: [],
      });
      expect(refused.scanned).toBe(0);
      expect(refused.removed).toEqual([]);
      expect(refused.errors.some(e => e.includes("allowlist"))).toBe(true);

      // Permitted via explicit realpath-resolved allowlist entry.
      const realBase = await realpath(base);
      const allowed = await gcWorktrees({
        root: base,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1_000,
      }, {
        nowMs,
        isClean: clean,
        isInUse: notInUse,
        prune: noopPrune,
        allowedRoots: [realBase],
      });
      expect(allowed.scanned).toBe(1);
      expect(allowed.removed).toEqual([target]);
    } finally {
      await rm(base, { recursive: true, force: true });
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

  it("removes a real clean git worktree via the real git-status path", async () => {
    const repo = await mkdtemp(join(tmpdir(), "omp-wt-repo-"));
    const { root, cleanup } = await makeRoot();
    try {
      await execFile("git", ["init", "-q", repo]);
      await execFile("git", ["-C", repo, "config", "user.email", "t@t.t"]);
      await execFile("git", ["-C", repo, "config", "user.name", "t"]);
      await writeFile(join(repo, "f"), "x");
      await execFile("git", ["-C", repo, "add", "."]);
      await execFile("git", ["-C", repo, "commit", "-qm", "init"]);
      const wtPath = join(root, "wt");
      await execFile("git", ["-C", repo, "worktree", "add", "--detach", wtPath]);
      const nowMs = Date.now();
      await ageTree(wtPath, nowMs, 10_000);

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1024 ** 3,
      }, {
        nowMs,
        isInUse: notInUse, // avoid lsof on the tree; exercise the real isClean path
        prune: noopPrune,
      });

      expect(report.removed).toEqual([wtPath]);
    } finally {
      await rm(repo, { recursive: true, force: true });
      await cleanup();
    }
  });

  it("protects a real dirty git worktree via the real git-status path", async () => {
    const repo = await mkdtemp(join(tmpdir(), "omp-wt-repo-"));
    const { root, cleanup } = await makeRoot();
    try {
      await execFile("git", ["init", "-q", repo]);
      await execFile("git", ["-C", repo, "config", "user.email", "t@t.t"]);
      await execFile("git", ["-C", repo, "config", "user.name", "t"]);
      await writeFile(join(repo, "f"), "x");
      await execFile("git", ["-C", repo, "add", "."]);
      await execFile("git", ["-C", repo, "commit", "-qm", "init"]);
      const wtPath = join(root, "wt");
      await execFile("git", ["-C", repo, "worktree", "add", "--detach", wtPath]);
      await writeFile(join(wtPath, "f"), "changed"); // uncommitted change
      const nowMs = Date.now();
      await ageTree(wtPath, nowMs, 10_000);

      const report = await gcWorktrees({
        root,
        intervalMs: 5_000,
        staleAfterMs: 1_000,
        maxCount: 8,
        maxBytes: 1, // also over byte budget, but dirty must still protect it
      }, {
        nowMs,
        isInUse: notInUse,
        prune: noopPrune,
      });

      expect(report.removed).toEqual([]);
      expect(report.budgetExceeded).toBe(true);
    } finally {
      await rm(repo, { recursive: true, force: true });
      await cleanup();
    }
  });

  it("is a no-op on a missing root", async () => {
    const report = await gcWorktrees({
      root: join(tmpdir(), "omp-wt-gc-does-not-exist-", ".omp", "wt"),
      intervalMs: 5_000,
      staleAfterMs: 1_000,
      maxCount: 8,
      maxBytes: 1_000,
    }, { isClean: clean, isInUse: notInUse, prune: noopPrune });
    expect(report.scanned).toBe(0);
    expect(report.removed).toEqual([]);
    expect(report.budgetExceeded).toBe(false);
  });

  it("runs the GC loop on startup and on schedule, skipping overlapping ticks while busy", async () => {
    vi.useFakeTimers();
    try {
      let resolveGc: () => void = () => {};
      const runGc = vi.fn(async () => new Promise<WorktreeGcReport>(resolve => {
        resolveGc = () => resolve(emptyReport);
      }));
      const skips: string[] = [];
      const reports: WorktreeGcReport[] = [];
      const policy = worktreeGcPolicy({
        OMP_WORKTREE_ROOT: "/tmp/.omp/wt",
        OMP_WORKTREE_GC_INTERVAL_MS: "100",
      });

      const loop = startWorktreeGcLoop(policy, {
        runGc,
        onReport: r => { reports.push(r); },
        onSkip: reason => { skips.push(reason); },
      });

      // Startup tick fires immediately (runGc called, promise pending).
      expect(runGc).toHaveBeenCalledTimes(1);

      // Interval elapses while the first run is still in flight -> busy -> skip.
      await vi.advanceTimersByTimeAsync(100);
      expect(skips.length).toBe(1);
      expect(runGc).toHaveBeenCalledTimes(1);

      // Complete the first run; the chained schedule sets the next timer.
      resolveGc();
      await vi.advanceTimersByTimeAsync(0);
      expect(reports.length).toBe(1);

      // Next interval fires a fresh tick.
      await vi.advanceTimersByTimeAsync(100);
      expect(runGc).toHaveBeenCalledTimes(2);

      loop.stop();
      resolveGc();
      await vi.advanceTimersByTimeAsync(0);
    } finally {
      vi.useRealTimers();
    }
  });
});
