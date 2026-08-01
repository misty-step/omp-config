/**
 * promptspace-git.ts — pure parser for `git status -b --porcelain` output,
 * consumed by extensions/promptspace.ts and tested directly (the extension
 * itself imports CustomEditor by value and cannot load outside omp).
 */

export interface GitInfo {
	branch: string;
	ahead: number;
	behind: number;
	/** Paths with index changes (X column set). A file with both index and
	 *  worktree changes (`MM`) counts in staged AND unstaged, starship-style. */
	staged: number;
	/** Paths with worktree changes (Y column set), excluding untracked. */
	unstaged: number;
	/** `??` paths. */
	untracked: number;
}

/**
 * Parse `git status -b --porcelain` output into status-line fields.
 *
 * Header shapes handled:
 *   `## master`                                     — no upstream
 *   `## master...origin/master [ahead 2, behind 1]` — tracking
 *   `## No commits yet on master`                   — unborn repo (branch kept)
 *   `## HEAD (no branch)`                           — detached → undefined
 *
 * Returns undefined for non-zero exit codes, missing headers, and detached
 * HEAD.
 */
export function parseGitStatus(stdout: string, code: number): GitInfo | undefined {
	if (code !== 0) return undefined;
	const lines = stdout.split("\n");
	let header = lines[0]?.startsWith("## ") ? lines[0].slice(3) : undefined;
	if (!header || header.startsWith("HEAD ")) return undefined;
	// Unborn repo: `No commits yet on <branch>` — keep the branch name.
	header = header.replace(/^No commits yet on /, "");
	// `branch...remote/branch [ahead 2, behind 1]` — anchor on the upstream
	// separator once instead of splitting every `...`.
	const branch = (/^(.*?)(?:\.\.\.\S+)?(?:\s+\[.*\])?$/.exec(header)?.[1] ?? header).trim();
	if (!branch) return undefined;
	const ahead = Number(/\[.*ahead (\d+)/.exec(header)?.[1] ?? 0);
	const behind = Number(/\[.*behind (\d+)/.exec(header)?.[1] ?? 0);
	let staged = 0;
	let unstaged = 0;
	let untracked = 0;
	for (const line of lines.slice(1)) {
		if (line.length < 2) continue;
		const x = line[0];
		const y = line[1];
		if (x === "?" || x === "!") {
			untracked++;
			continue;
		}
		if (x !== " ") staged++;
		if (y !== " ") unstaged++;
	}
	return { branch, ahead, behind, staged, unstaged, untracked };
}
