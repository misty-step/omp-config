---
name: tidy
description: Reconcile uncommitted workspace state into owned, reviewable commits and deletions.
disable-model-invocation: true
---

# Tidy

Reconcile the current workspace without touching unrelated work.

## Inventory

Read repository policy, branch and sequencer state, status, diffs, untracked
files, worktrees, and trusted records. Avoid generated or secret-bearing trees.
Give every path an owner and one disposition: commit now, keep in progress,
delete, or reconcile with another owner. Group commit candidates by semantic
outcome.

## Apply the chosen plan

Present exact commit groups, messages, checks, deletions, retained work, and
record updates. Name destructive actions. Commit or delete only groups the
operator selects. Run narrow checks for each group, then reread status, commit
contents, retained state, and trusted records.

Stop on an unexpected owner, secret, conflict, failed check, or sequencer state.
Return commits, deletions, retained work, checks, and remaining dirt.
