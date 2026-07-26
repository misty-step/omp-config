import { execFile as execFileCallback } from "node:child_process";
import { lstat, readdir, realpath, rm, stat, readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join, relative, resolve, sep } from "node:path";
import { promisify } from "node:util";

const execFile = promisify(execFileCallback);

export const worktreeGcDefaults = Object.freeze({
  root: join(homedir(), ".omp", "wt"),
  intervalMs: 5 * 60_000,
  staleAfterMs: 15 * 60_000,
  maxCount: 8,
  maxBytes: 20 * 1024 ** 3,
  maxDepth: 64,
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
  activityMs: number;
};

export type WorktreeGcReport = {
  root: string;
  scanned: number;
  removed: string[];
  remainingCount: number;
  remainingBytes: number;
  budgetExceeded: boolean;
  errors: string[];
};

/** "clean" = no uncommitted changes; "dirty" = real uncommitted changes (protected); "unknown" = git cannot read the tree (e.g. dangling gitdir pointer, the canonical orphan shape). */
export type CleanResult = "clean" | "dirty" | "unknown";

/** inUse=true blocks removal. error is set when the liveness tool itself failed (missing binary, timeout, EPERM). */
export type UseResult = { inUse: boolean; error?: string };

type GcOptions = {
  nowMs?: number;
  isClean?: (path: string) => Promise<CleanResult>;
  isInUse?: (path: string) => Promise<UseResult>;
  remove?: (path: string) => Promise<void>;
  /** Best-effort deregistration of the worktree record in its parent repo, given the parent repo's git dir. */
  prune?: (parentGitDir: string) => Promise<void>;
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

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

/** Walk a worktree, summing file bytes and tracking the most recent file mtime as the activity signal. Symlinks are skipped so the walk cannot escape the tree. Depth-bounded to bound pathological trees. */
async function measureTree(path: string, maxDepth: number, errors: string[]): Promise<{ bytes: number; activityMs: number }> {
  let bytes = 0;
  let activityMs = 0;
  const stack: Array<{ dir: string; depth: number }> = [{ dir: path, depth: 0 }];
  while (stack.length > 0) {
    const { dir, depth } = stack.pop()!;
    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch (error) {
      errors.push(`unreadable ${dir}: ${errorMessage(error)}`);
      continue;
    }
    for (const entry of entries) {
      if (entry.isSymbolicLink()) continue;
      const entryPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (depth + 1 < maxDepth) stack.push({ dir: entryPath, depth: depth + 1 });
        continue;
      }
      if (entry.isFile()) {
        try {
          const info = await stat(entryPath);
          bytes += info.size;
          if (info.mtimeMs > activityMs) activityMs = info.mtimeMs;
        } catch (error) {
          errors.push(`stat failed ${entryPath}: ${errorMessage(error)}`);
        }
      }
    }
  }
  // Floor activity at the tree root's own mtime so an empty/tree-only change is still dated.
  try {
    const rootInfo = await stat(path);
    if (rootInfo.mtimeMs > activityMs) activityMs = rootInfo.mtimeMs;
  } catch {
    // ignore; activityMs already reflects contents
  }
  return { bytes, activityMs };
}

async function findWorktrees(
  path: string,
  depth: number,
  maxDepth: number,
  errors: string[],
  result: WorktreeGcCandidate[],
): Promise<void> {
  let entries;
  try {
    entries = await readdir(path, { withFileTypes: true });
  } catch (error) {
    errors.push(`unreadable ${path}: ${errorMessage(error)}`);
    return;
  }
  const gitMarker = entries.find(entry => entry.name === ".git" && entry.isFile() && !entry.isSymbolicLink());
  if (gitMarker) {
    let marker: string;
    try {
      marker = await readFile(join(path, ".git"), "utf8");
    } catch (error) {
      errors.push(`git marker read failed ${path}: ${errorMessage(error)}`);
      marker = "";
    }
    if (/^gitdir:\s*\S+/m.test(marker)) {
      const measured = await measureTree(path, maxDepth, errors);
      result.push({ path, bytes: measured.bytes, activityMs: measured.activityMs });
      return;
    }
  }
  if (depth + 1 >= maxDepth) return;
  await Promise.all(
    entries
      .filter(entry => entry.isDirectory() && !entry.isSymbolicLink() && entry.name !== ".git")
      .map(entry => findWorktrees(join(path, entry.name), depth + 1, maxDepth, errors, result)),
  );
}

export async function discoverWorktrees(root: string): Promise<WorktreeGcCandidate[]> {
  const errors: string[] = [];
  return discoverWorktreesWithErrors(root, errors);
}

async function discoverWorktreesWithErrors(root: string, errors: string[]): Promise<WorktreeGcCandidate[]> {
  const resolvedRoot = resolve(root);
  try {
    if (!(await stat(resolvedRoot)).isDirectory()) return [];
  } catch {
    return [];
  }
  const result: WorktreeGcCandidate[] = [];
  await findWorktrees(resolvedRoot, 0, worktreeGcDefaults.maxDepth, errors, result);
  return result;
}

async function isCleanWorktree(path: string): Promise<CleanResult> {
  try {
    const { stdout } = await execFile("git", ["-C", path, "status", "--porcelain", "--untracked-files=all"], {
      timeout: 5_000,
      maxBuffer: 64 * 1024,
    });
    return stdout.length === 0 ? "clean" : "dirty";
  } catch {
    // git cannot read this tree (dangling gitdir pointer, missing parent repo, etc.). That is the
    // canonical orphan shape, not a dirty tree; treat it as eligible when stale rather than protected.
    return "unknown";
  }
}

async function isWorktreeInUse(path: string): Promise<UseResult> {
  try {
    await execFile("lsof", ["-t", "+D", path], { timeout: 5_000, maxBuffer: 64 * 1024 });
    return { inUse: true };
  } catch (error) {
    const code = (error as NodeJS.ErrnoException & { code?: number }).code;
    // lsof exit 1 = ran successfully, no users. Any other failure (missing binary, timeout, EPERM)
    // is a tooling failure: stay safe (treat as in use) but surface the failure mode.
    if (code === 1) return { inUse: false };
    return { inUse: true, error: `lsof exited ${code ?? "?"}: ${errorMessage(error)}` };
  }
}

/** Resolve the parent repository's .git dir from a worktree's `.git` gitdir pointer. */
async function parentGitDir(worktreePath: string): Promise<string | null> {
  let marker: string;
  try {
    marker = await readFile(join(worktreePath, ".git"), "utf8");
  } catch {
    return null;
  }
  const match = marker.match(/^gitdir:\s*(\S+)/m);
  if (!match || match[1] === undefined) return null;
  const gitdir = resolve(match[1]);
  const segments = gitdir.split(sep);
  const gitIdx = segments.lastIndexOf(".git");
  if (gitIdx >= 0 && segments[gitIdx + 1] === "worktrees") {
    return segments.slice(0, gitIdx + 1).join(sep);
  }
  // Not under a .git/worktrees layout; assume the pointer is the repo gitdir itself.
  return gitdir;
}

async function pruneParentWorktree(parentGitDir: string): Promise<void> {
  await execFile("git", ["--git-dir", parentGitDir, "worktree", "prune"], {
    timeout: 10_000,
    maxBuffer: 64 * 1024,
  });
}

/** True only if candidateReal is strictly inside rootReal (both already realpath-resolved). */
function withinRootReal(rootReal: string, candidateReal: string): boolean {
  if (candidateReal === rootReal) return false;
  const rel = relative(rootReal, candidateReal);
  return rel.length > 0 && !rel.startsWith(`..${sep}`) && rel !== "..";
}

async function realpathSafe(path: string): Promise<string | null> {
  try {
    return await realpath(path);
  } catch {
    return null;
  }
}

export async function gcWorktrees(
  policy: WorktreeGcPolicy,
  options: GcOptions = {},
): Promise<WorktreeGcReport> {
  const root = resolve(policy.root);
  const errors: string[] = [];
  const rootReal = await realpathSafe(root);
  if (rootReal === null) {
    return { root, scanned: 0, removed: [], remainingCount: 0, remainingBytes: 0, budgetExceeded: false, errors };
  }

  const nowMs = options.nowMs ?? Date.now();
  const isClean = options.isClean ?? isCleanWorktree;
  const isInUse = options.isInUse ?? isWorktreeInUse;
  const remove = options.remove ?? ((path: string) => rm(path, { recursive: true, force: true }));
  const prune = options.prune ?? pruneParentWorktree;

  const discovered = await discoverWorktreesWithErrors(root, errors);

  // Reject candidates whose realpath escapes root (symlinks, moved dirs).
  const candidates: WorktreeGcCandidate[] = [];
  for (const candidate of discovered) {
    const real = await realpathSafe(candidate.path);
    if (real === null) continue;
    if (!withinRootReal(rootReal, real)) {
      errors.push(`refused candidate outside root: ${candidate.path}`);
      continue;
    }
    candidates.push(candidate);
  }

  // Eligibility pass: protected trees (real uncommitted changes, or in use) are excluded.
  type Eligible = WorktreeGcCandidate & { gitDir: string | null };
  const eligible: Eligible[] = [];
  for (const candidate of candidates) {
    const cleanResult = await isClean(candidate.path);
    if (cleanResult === "dirty") continue;
    const use = await isInUse(candidate.path);
    if (use.error) errors.push(`lsof failure for ${candidate.path}: ${use.error}`);
    if (use.inUse) continue;
    let gitDir: string | null = null;
    try {
      gitDir = await parentGitDir(candidate.path);
    } catch (error) {
      errors.push(`gitdir resolve failed ${candidate.path}: ${errorMessage(error)}`);
    }
    eligible.push({ ...candidate, gitDir });
  }

  // Evict oldest-first: stale trees, then over-budget trees.
  eligible.sort((left, right) => left.activityMs - right.activityMs);
  const removed: string[] = [];
  let remainingCount = candidates.length;
  let remainingBytes = candidates.reduce((total, candidate) => total + candidate.bytes, 0);

  for (const candidate of eligible) {
    const underBudget = remainingCount <= policy.maxCount && remainingBytes <= policy.maxBytes;
    const stale = nowMs - candidate.activityMs >= policy.staleAfterMs;
    if (!stale && underBudget) continue;

    // Delete-time re-verification (TOCTOU): re-stat the path, refuse symlinks/non-directories,
    // re-check liveness and cleanliness immediately before removal.
    let info;
    try {
      info = await lstat(candidate.path);
    } catch {
      continue; // already gone
    }
    if (info.isSymbolicLink() || !info.isDirectory()) {
      errors.push(`refused non-directory/symlink at ${candidate.path}`);
      continue;
    }
    const realNow = await realpathSafe(candidate.path);
    if (realNow === null || !withinRootReal(rootReal, realNow)) {
      errors.push(`refused path traversal at ${candidate.path}`);
      continue;
    }
    const useNow = await isInUse(candidate.path);
    if (useNow.error) errors.push(`lsof failure (recheck) for ${candidate.path}: ${useNow.error}`);
    if (useNow.inUse) continue;
    const cleanNow = await isClean(candidate.path);
    if (cleanNow === "dirty") continue;

    try {
      await remove(candidate.path);
    } catch (error) {
      errors.push(`remove failed for ${candidate.path}: ${errorMessage(error)}`);
      continue;
    }
    removed.push(candidate.path);
    remainingCount -= 1;
    remainingBytes -= candidate.bytes;

    // Best-effort deregistration of the stale worktree record in the parent repo.
    if (candidate.gitDir) {
      try {
        await prune(candidate.gitDir);
      } catch (error) {
        errors.push(`prune failed for ${candidate.gitDir}: ${errorMessage(error)}`);
      }
    }
  }

  return {
    root,
    scanned: candidates.length,
    removed,
    remainingCount,
    remainingBytes,
    budgetExceeded: remainingCount > policy.maxCount || remainingBytes > policy.maxBytes,
    errors,
  };
}

export async function runWorktreeGc(policy = worktreeGcPolicy()): Promise<WorktreeGcReport> {
  return gcWorktrees(policy);
}
