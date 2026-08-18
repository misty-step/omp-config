---
name: deliver
description: Take the highest-priority ready ticket to an unmerged pull request with a Hunk walkthrough and a code-review report.
disable-model-invocation: true
---

# Deliver

One ready ticket. A reviewable change. Then stop.

## Claim

Take the highest-priority ready piece of work this checkout should do. Use whatever
ledger the project already trusts. Skip anything already moving. If
the work is still a design argument, read `skill://grilling` first.

## Isolate

Leave the operator's branch alone. Do this in a worktree from the
default branch.

## Implement

The smallest change that is actually true. See a new contract fail
before you make it pass. Show that acceptance holds
(`skill://evidence-packet` when the proof is something you can point
at).

## Report

Read `skill://code-review` through the report. Do not repair.

## Publish

Open an unmerged pull request that carries the ticket and the
report. Open the walkthrough with `skill://hunk`. Leave focus where
it is.

You are done when the operator can review the PR, the walkthrough,
and the report.
