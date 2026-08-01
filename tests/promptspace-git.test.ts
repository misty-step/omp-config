import { describe, expect, test } from "bun:test";
import { parseGitStatus } from "../global/lib/promptspace-git.ts";

describe("parseGitStatus", () => {
	test("tracking branch with ahead/behind and mixed changes", () => {
		const out = [
			"## master...origin/master [ahead 2, behind 1]",
			"M  staged.ts", // index only
			" M worktree.ts", // worktree only
			"MM both.ts", // counts in staged AND unstaged
			"?? new.ts",
			"",
		].join("\n");
		expect(parseGitStatus(out, 0)).toEqual({
			branch: "master",
			ahead: 2,
			behind: 1,
			staged: 2,
			unstaged: 2,
			untracked: 1,
		});
	});

	test("clean branch without upstream", () => {
		expect(parseGitStatus("## feature/x\n", 0)).toEqual({
			branch: "feature/x",
			ahead: 0,
			behind: 0,
			staged: 0,
			unstaged: 0,
			untracked: 0,
		});
	});

	test("unborn repo keeps the branch name", () => {
		expect(parseGitStatus("## No commits yet on master\n?? a.ts\n", 0)).toMatchObject({
			branch: "master",
			untracked: 1,
		});
	});

	test("deleted and renamed index entries count as staged", () => {
		const out = ["## master", "D  gone.ts", "R  old.ts -> new.ts", " D worktree-del.ts", ""].join("\n");
		expect(parseGitStatus(out, 0)).toMatchObject({ staged: 2, unstaged: 1, untracked: 0 });
	});

	test("detached HEAD yields undefined", () => {
		expect(parseGitStatus("## HEAD (no branch)\n M a.ts\n", 0)).toBeUndefined();
	});

	test("non-zero exit code yields undefined even with plausible stdout", () => {
		expect(parseGitStatus("## master\n", 128)).toBeUndefined();
	});

	test("missing header yields undefined", () => {
		expect(parseGitStatus("fatal: not a git repository\n", 0)).toBeUndefined();
	});

	test("branch name containing dots survives upstream split", () => {
		const out = "## release/v1.2.3...origin/release/v1.2.3 [ahead 1]\n";
		expect(parseGitStatus(out, 0)).toMatchObject({ branch: "release/v1.2.3", ahead: 1 });
	});
});
