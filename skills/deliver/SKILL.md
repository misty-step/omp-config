---
name: deliver
description: Take one ready slice to a proved, reviewed, unmerged pull request.
disable-model-invocation: true
argument-hint: "[ticket or accepted spec]"
---

# Deliver

One ready slice. Prove it on its real interface. Open the pull request. Stop.
Release is a separate operator decision.

## Claim

Take one accepted, independently useful slice from the project's trusted work
record. Use `/shape` when material intent, compatibility, scope, or architecture
is still open. Isolate the work from the operator's checkout and record the
base revision.

Done when the slice, owner, accepted intent, and proof boundary are explicit.

## Build

Plan proof before production edits. Capture a baseline when the claim is a fix,
comparison, or state change. Use the current data owners and interfaces unless
evidence shows they fail. Fix the source, migrate every caller, and delete the
obsolete path.

Add a test only for a new observable contract that lacks defense. Keep unrelated
cleanup and speculative flexibility out.

Done when the slice is complete and no caller or temporary path remains.

## Prove

Run the fastest deterministic repository gates first. Fix changed-caused
failures before model review, external-provider work, or an expensive matrix.
Then run the remaining applicable checks, start the affected system, and
exercise the changed real interface. Cover the changed success, boundary, and
failure paths; add recovery, concurrency, or hostile-input checks only when the
change touches those risks. Inspect the evidence.

For an expensive matrix, live eval, or external-provider run, first pass one
cheap deterministic case through setup, propagation, scoring or aggregation,
evidence validation, and artifact publication.

Done when the deterministic gates are green and the changed behavior and its
relevant failure path work on the real surface.

## Review

Review only residual risk that the green deterministic gates cannot decide:
accepted intent, domain behavior, boundaries, non-local effects, and the
high-risk surfaces this slice touches. Repair supported Blockers.

Classify a recurring, locally decidable finding as a control candidate. Record
it in the trusted work record for `/custom-linters` (or `/foundation` when the
repository lacks a lint host); keep its implementation outside this slice.
Record other useful non-blocking findings as follow-up work. Any repair
invalidates earlier proof, so rerun the affected gates and real scenario on
the final head.

Done when no Blocker or failed required gate remains.

## Publish

Open an unmerged pull request with an active imperative title (`type(scope): outcome`).
Lead with bottom-line intent, key decisions, and the smallest visual structure
(`show-me` diff, call tree, component tree, or Mermaid diagram) when structure
or flow changed.

For observable claims that depend on media: when GitHub is the review surface,
attach sanitized media directly with `gh pr create --attach path/to/media.png#Alt`
(referencing local paths inline in the body); link reviewer-open here.now
evidence for interactive web artifacts or external review. Record the exact final
head beside any attached claim. Record passed deterministic gates, real-surface
proof, rollback path, and residual risk. Reconcile current PR comments and
record the exact final head.

Done when the operator can review and decide whether to invoke `/release`.
