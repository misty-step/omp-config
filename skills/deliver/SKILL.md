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

Run the applicable repository checks. Start the affected system and exercise the
changed real interface. Cover the changed success, boundary, and failure paths;
add recovery, concurrency, or hostile-input checks only when the change touches
those risks. Inspect the evidence.

For an expensive matrix, live eval, or external-provider run, first pass one
cheap deterministic case through setup, propagation, scoring or aggregation,
evidence validation, and artifact publication.

Done when the changed behavior and its relevant failure path work on the real
surface.

## Review

Review the complete result against accepted intent and surrounding behavior.
Repair supported Blockers. Record useful non-blocking findings as follow-up
work; they do not expand this slice. Any repair invalidates earlier proof, so
rerun the affected checks and real scenario on the final head.

Done when no Blocker or failed required check remains.

## Publish

Open an unmerged pull request. State the intent, decisions, checks, production
impact, rollback path, and residual risk. For observable claims that depend on
media, link reviewer-open here.now evidence. Reconcile current PR comments and
record the exact final head.

Done when the operator can review and decide whether to invoke `/release`.
