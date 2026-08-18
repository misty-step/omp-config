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

The spoken close and the PR MUST include the Taste verdict. Lead with it.
Do not ask the operator to accept, reject, or defer Hygiene. If one finding
passes the taste gate and sits outside this ticket, name it as the follow-up
and stop. If none pass, say none. Do not end with a mixed findings list
that forces the operator to ask whether the repairs improve the design.

## Publish

Open an unmerged pull request that carries the ticket, the Taste verdict,
and the report. Open the walkthrough with `skill://hunk`. Leave focus where
it is.

The walkthrough MUST be annotated. Follow `skill://hunk` Walkthrough:
sidecar first, quoted `herdr pane run`, live comment count > 0, viewport
on note `1/N`. Opening an empty Hunk on the first diff file is not done.

You are done when the operator can review the PR, step the annotated
walkthrough, read the Taste verdict, and decide only on Take findings.

