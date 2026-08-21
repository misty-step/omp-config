---
name: deliver
description: Take the highest-priority ready ticket to an unmerged pull request with real-interface proof, reviewed repairs, and a Hunk walkthrough.
disable-model-invocation: true
---

# Deliver

One ready slice. Proved on its real interface. Then stop.

## Claim

Take the highest-priority ready piece of work this checkout should do, using
whatever ledger the project already trusts. Skip anything already moving. If
the work is still a design argument, read `skill://grilling` first.

## Slice

Work in a worktree off the default branch; leave the operator's branch alone.
Take the smallest independently useful outcome. Split broad tickets before
writing code; move unrelated cleanup out.

## Plan proof

Before the first production edit, decide how the changed behavior will be
proved through its real interface. Capture required baselines now: bugs,
regressions, comparisons, and state changes cannot be baselined after the
edit. Read `skill://evidence-packet` when the claim is observable.

## Implement

Choose the design by its data structures and relationships (Torvalds), module
depth with errors defined out of existence (Ousterhout), and
necessary-versus-incidental complexity (Hickey). Implement against accepted
intent using the repository's own checks. Fix the source, migrate every
caller, remove obsolete paths. Defend newly exposed contracts with tests that
fail on plausible defects.

## Run

Start every affected application locally and QA the product surface: exercise
the changed behavior end to end as a user would, and probe the paths around
it. A repository-owned start or seed command wins over improvisation.
Automated tests, lint, and CI do not substitute for this.

## Review and repair

Review the complete result against accepted intent, repository behavior, and
runtime evidence — not only the diff. Judge findings by data structures
(Torvalds), deep modules (Ousterhout), and necessary complexity (Hickey).
Repair supported in-scope defects; route intent conflicts to the operator;
leave speculative improvements and unrelated cleanup out. Rerun the proof any
repair touched.

## Publish

Attach the inspected evidence to the pull request; GitHub PR uploads are the
standard path (`skill://evidence-packet`, DELIVERY). Open the annotated Hunk
walkthrough per `skill://hunk`. Leave the PR unmerged; merge and deployment
belong to a separate release gate (`skill://release`).

You are done when the operator can review the PR, step the walkthrough, read
the evidence, and decide merge through the release gate.
