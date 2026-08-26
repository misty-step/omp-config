---
name: tidy
description: Reconcile uncommitted workspace state into approved commits, deletions, and tracked work.
disable-model-invocation: true
---

# Tidy

A dirty workspace can contain operator work, generated residue, abandoned
experiments, and finished changes. Tidy identifies ownership before mutation.

## Inventory

Read repository policy, branch, sequencer state, status, diffs, untracked files,
worktrees, and related trusted work records. Do not bulk-open generated or
secret-bearing trees. Preserve unrelated work.

Classify every path as: commit now, keep in progress, delete, or reconcile with
another owner. Group commit candidates by one semantic outcome.

Done when every uncommitted path has evidence, owner, and disposition.

## Propose

Present the exact commit groups, messages, checks, deletions, retained paths,
and record updates. Name destructive or irreversible actions. Wait for explicit
operator approval; invocation alone does not approve the plan.

Done when the operator accepts one exact mutation plan.

## Execute and verify

Apply only the approved plan. Run the narrow checks for each commit group.
Create semantic commits without folding unrelated work together. Re-read final
status, commit contents, retained state, and trusted records.

Return commits, deletions, retained work, checks, and remaining dirt. Stop on an
unexpected owner, secret, conflict, failed check, or sequencer state.

Done when final workspace state matches the approved plan exactly.
