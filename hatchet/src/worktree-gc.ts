import { execFile as execFileCallback } from "node:child_process";
import { readdir, rm, stat, readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { promisify } from "node:util";

const execFile = promisify(execFileCallback);

export const worktreeGcDefaults = Object.freeze({
  root: join(homedir(), ".omp", "wt"),
  intervalMs: 5 * 60_000,
  staleAfterMs: 15 * 60_000,
  maxCount: 8,
  maxBytes: 20 * 1024 ** 3,
});

export type WorktreeGcPolicy = {
  root: string;
  intervalMs: number;
  staleAfterMs: number;
  maxCount: number;
  maxBytes: number;
};

export type WorktreeGcCandidate = {
  path: string;
  bytes: number;
  mtimeMs: number;
};

export type WorktreeGcReport = {
  root: string;
  scanned: number;
  removed: string[];
  remainingCount: number;
  remainingBytes: number;
  budgetExceeded: boolean;
};

type GcOptions = {
  nowMs?: number;
  isClean?: (path: string) => Promise<boolean>;
  isInUse?: (path: string) => Promise<boolean>;
  remove?: (path: string) => Promise<void>;
};

function positiveInteger(value: string | undefined, fallback: number): number {
  if (value === undefined) return fallback;
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : fallback;
}

export function worktreeGcPolicy(environment: NodeJS.ProcessEnv = process.env): WorktreeGcPolicy {
  return {
    root: resolve(environment.OMP_WORKTREE_ROOT ?? worktreeGcDefaults.root),
    intervalMs: positiveInteger(environment.OMP_WORKTREE_GC_INTERVAL_MS, worktreeGcDefaults.intervalMs),
    staleAfterMs: positiveInteger(environment.OMP_WORKTREE_GC_STALE_AFTER_MS, worktreeGcDefaults.staleAfterMs),
    maxCount: positiveInteger(environment.OMP_WORKTREE_MAX_COUNT, worktreeGcDefaults.maxCount),
    maxBytes: positiveInteger(environment.OMP_WORKTREE_MAX_BYTES, worktreeGcDefaults.maxBytes),
  };
}

async function directoryBytes(path: string): Promise<number> {
  let bytes = 0;
  const entries = await readdir(path, { withFileTypes: true });
  for (const entry of entries) {
    const entryPath = join(path, entry.name);
    if (entry.isDirectory()) bytes += await directoryBytes(entryPath);
    else if (entry.isFile()) bytes += (await stat(entryPath)).size;
  }
  return bytes;
}

async function findWorktrees(path: string, result: WorktreeGcCandidate[]): Promise<void> {
  let entries;
  try {
    entries = await readdir(path, { withFileTypes: true });
  } catch {
    return;
  }
  const gitMarker = entries.find(entry => entry.name === ".git" && entry.isFile());
  if (gitMarker) {
    try {
      const marker = await readFile(join(path, ".git"), "utf8");
      if (/^gitdir:\s*\S+/m.test(marker)) {
        const metadata = await stat(path);
        result.push({ path, bytes: await directoryBytes(path), mtimeMs: metadata.mtimeMs });
        return;
      }
    } catch {
      return;
    }
  }
  await Promise.all(
    entries
      .filter(entry => entry.isDirectory() && entry.name !== ".git")
      .map(entry => findWorktrees(join(path, entry.name), result)),
  );
}

export async function discoverWorktrees(root: string): Promise<WorktreeGcCandidate[]> {
  const resolvedRoot = resolve(root);
  try {
    if (!(await stat(resolvedRoot)).isDirectory()) return [];
  } catch {
    return [];
  }
  const result: WorktreeGcCandidate[] = [];
  await findWorktrees(resolvedRoot, result);
  return result;
}

async function isCleanWorktree(path: string): Promise<boolean> {
  try {
    const { stdout } = await execFile("git", ["-C", path, "status", "--porcelain", "--untracked-files=all"], {
      timeout: 5_000,
      maxBuffer: 64 * 1024,
    });
    return stdout.length === 0;
  } catch {
    return false;
  }
}

async function isWorktreeInUse(path: string): Promise<boolean> {
  try {
    await execFile("lsof", ["-t", "+D", path], { timeout: 5_000, maxBuffer: 64 * 1024 });
    return true;
  } catch (error) {
    return (error as NodeJS.ErrnoException & { code?: number }).code !== 1;
  }
}

function withinRoot(root: string, candidate: string): boolean {
  const rel = relative(root, candidate);
  return rel.length > 0 && rel !== ".." && !rel.startsWith(`..${resolve("/")}`);
}

export async function gcWorktrees(
  policy: WorktreeGcPolicy,
  options: GcOptions = {},
): Promise<WorktreeGcReport> {
  const root = resolve(policy.root);
  const candidates = (await discoverWorktrees(root)).filter(candidate => withinRoot(root, resolve(candidate.path)));
  const nowMs = options.nowMs ?? Date.now();
  const isClean = options.isClean ?? isCleanWorktree;
  const isInUse = options.isInUse ?? isWorktreeInUse;
  const remove = options.remove ?? ((path: string) => rm(path, { recursive: true, force: true }));
  const eligible: WorktreeGcCandidate[] = [];

  for (const candidate of candidates) {
    if (!(await isClean(candidate.path)) || (await isInUse(candidate.path))) continue;
    eligible.push(candidate);
  }

  eligible.sort((left, right) => left.mtimeMs - right.mtimeMs);
  const removed: string[] = [];
  let remainingCount = candidates.length;
  let remainingBytes = candidates.reduce((total, candidate) => total + candidate.bytes, 0);
  for (const candidate of eligible) {
    const underBudget = remainingCount <= policy.maxCount && remainingBytes <= policy.maxBytes;
    const stale = nowMs - candidate.mtimeMs >= policy.staleAfterMs;
    if (!stale && underBudget) continue;
    await remove(candidate.path);
    removed.push(candidate.path);
    remainingCount -= 1;
    remainingBytes -= candidate.bytes;
  }

  return {
    root,
    scanned: candidates.length,
    removed,
    remainingCount,
    remainingBytes,
    budgetExceeded: remainingCount > policy.maxCount || remainingBytes > policy.maxBytes,
  };
}

export async function runWorktreeGc(policy = worktreeGcPolicy()): Promise<WorktreeGcReport> {
  return gcWorktrees(policy);
}
