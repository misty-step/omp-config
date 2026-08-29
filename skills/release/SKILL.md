---
name: release
description: Merge one reviewed change, deploy it, prove production, and recover on failure.
disable-model-invocation: true
argument-hint: "[pull request]"
---

# Release

A release is complete when the exact reviewed change works in production. A
timer does not prove that. `/release` authorizes merge, deploy, and one ordinary
rollback for the named pull request.

## Ready

Record the pull request head SHA. Reconcile current review comments. Close every
supported Blocker; track non-blocking findings separately. Require existing CI
on that exact head to be green. Open the evidence linked for observable
claims.

Before merge, confirm the repository-owned deploy, health, smoke, and rollback
paths exist and apply to this change. Confirm migration and rollback proof for
persisted-state changes.

Done when the recorded head is safe to ship.

## Ship

Confirm the head did not change. Merge through the repository's normal path.
Record the merge revision. Wait for existing post-merge checks. Deploy the
merged artifact through the owned path. Record the deployed identity when the
runtime exposes it.

A wrong artifact, failed deploy, or failed post-merge check is red.

Done when production runs the intended artifact or recovery has started.

## Verify production

Watch the deploy finish. Then verify production, not a local substitute:

- run health and repository-owned smoke checks;
- manually exercise every affected production product or operator surface;
- read back changed persisted state or migrations;
- inspect new relevant Sentry issues, events, and logs when Sentry is present;
- inspect applicable production logs, metrics, or traces.

Record what ran and what was observed. No fixed soak window is required. Close
when the deployed product works and no relevant production signal is red.

## Recover

Preserve the failure evidence. Run one authorized repository-owned rollback or
reinstall the prior artifact. Verify the restored identity, health, smoke,
state, and affected surfaces. Tell the operator what failed and what changed.

A fix-forward is a new revision and starts at Ready. If recovery fails or the
runtime identity is unknown, stop mutation and escalate.

Done when production is healthy on a known revision or the incident is safely
owned.
