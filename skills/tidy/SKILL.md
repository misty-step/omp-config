---
name: tidy
description: Tidy uncommitted workspace state into clean commits, consolidation, and deletions.
disable-model-invocation: true
---

# Tidy

Tidy a workspace's uncommitted and untracked state into settled, semantically coherent commits, deletions, and explicit in-flight tracking.

## 1. Orient

Determine repository context and enforce clean sequencer state:

- Current branch, upstream tracking, and base branch (`main` or `master`).
- Merge-base and commits ahead/behind the base branch.
- **Sequencer & merge guard:** Check for in-progress Git operations (`MERGE_HEAD`, `rebase-merge/`, `rebase-apply/`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `BISECT_LOG`).

If an active merge, rebase, cherry-pick, revert, or bisect is detected:

- **STOP immediately.** Do not proceed to Inspect, Plan, or Execute.
- Report the active operation, conflict status, and the in-progress commit.
- Require the operator to complete (`--continue`), abort (`--abort`), or resolve the operation separately before continuing the tidy workflow.

Completion criterion: Base branch, current branch status, and merge-base identified, with zero in-progress Git operations active.

## 2. Inspect

Collect complete working tree state without triggering recursive bulk explosions:

- Run `git status --porcelain -unormal --ignored=matching` first to discover staged changes, unstaged modifications, untracked roots, and ignored paths.
- Inspect staged changes (`git diff --cached`) and unstaged modifications (`git diff`).
- Identify bulk untracked or ignored trees (`node_modules/`, `target/`, `dist/`, `.venv/`, `build/`, `vendor/`, etc.) by directory root from the `-unormal` listing; do not enumerate or read their nested contents.
- Selectively enumerate only non-bulk source directories (`git status --porcelain -uall -- <dir>` or `git ls-files --others --exclude-standard <dir>`) when per-file accounting is needed.

Inspect working tree content safely:

- **Source edits & diffs:** Read uncommitted diffs and source files needed to understand code changes.
- **Bulk trees:** Treat untracked or ignored dependency, vendor, and build directories by root directory; plan them for `.gitignore` or deletion as a single unit.
- **Secrets & credentials:** Treat `.env*`, private keys (`*.pem`, `*.key`), credential dumps, and token caches as metadata-only. Confirm presence, matching ignore rule, and retention from path metadata; do not read secret contents into context.
- **Discretionary ignored files:** Read non-secret ignored files (isolated scratch logs, test dumps) only when necessary to decide between deletion and retention.

Completion criterion: Every modified, staged, untracked, and ignored path accounted for without expanding nested bulk trees or reading secrets into context.

## 3. Classify

Group every uncommitted path into one of four states:

- **Settled work:** Completed, tested, or coherent changes that belong in a logical commit.
- **In-flight work:** Unfinished experiments or partial implementations that should remain uncommitted, move to a feature branch, or be stashed.
- **Consolidation:** Scattered edits across related files that belong together in a single atomic commit, or cohesive changes that need splitting into distinct semantic units.
- **Debris:** Disposable logs, test dumps, temporary scratchpads, obsolete stubs, or generated files that should be deleted or added to `.gitignore`.

Completion criterion: Zero unclassified paths. Every path assigned to a semantic commit group, deletion, ignore rule, or explicit in-flight hold.

## 4. Plan

Draft a structured tidy plan:

1. **Deletions:** Exact paths to remove (debris, scratch files).
2. **Ignores:** Patterns to append to `.gitignore`.
3. **Commit groups:** Ordered list of atomic commits, each specifying:
   - Included file paths or patch hunks.
   - Commit type and imperative subject line.
   - Rationale and affected scope.
4. **In-flight tracking:** List of unfinished items and recommendation (hold in working tree, branch, or stash).
5. **Branch status:** Assessment relative to base branch (`main`/`master`) — ready to merge, rebase suggested, or active development.

Completion criterion: Complete plan drafted with explicit paths, commit messages, and actions.

## 5. Confirm

Present the tidy plan to the operator and wait for explicit confirmation.

- Use direct confirmation or `ask`.
- List exact paths for deletion, ignore, and each commit group.
- Do not delete, stage, commit, or reset files before the operator confirms.
- If the operator modifies groupings, commit messages, or deletions, adjust the plan and re-confirm.

Completion criterion: Operator approval recorded for the specific plan.

## 6. Execute

Execute the approved plan in order:

1. Delete confirmed debris files.
2. Update `.gitignore` if planned.
3. Stage and commit each group with its approved message.
4. Leave confirmed in-flight work in the agreed state.

Completion criterion: Every approved deletion applied and every planned commit created cleanly.

## 7. Verify

Inspect final repository state:

- Run `git status` to verify the working tree matches the agreed state (clean, or containing only confirmed in-flight files).
- Run `git log -n <count>` to verify new commits are properly ordered, scoped, and described.

Completion criterion: Clean working tree status and verified commit log matching the approved plan.
