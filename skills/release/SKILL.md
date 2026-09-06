---
name: release
description: Finalize one pull request, merge it, deploy it, prove production, and recover on failure.
disable-model-invocation: true
argument-hint: "[pull request]"
---

# Release

`/release <pull-request>` authorizes the named change's normal merge, deploy,
and one ordinary rollback. It does not authorize candidate mutation, unrelated
changes, history rewrites, force-pushes, or tags.

## Finalize

Bind the exact pull-request head. Read its accepted intent, complete diff,
affected contracts, comments, review state, checks, and linked evidence.
Inspect every changed file for dead or scaffold code, debug paths, temporary
flags, shims, unsupported fallbacks, exposed state, unnecessary fields, and
speculative abstractions. Preserve purposeful observability, errors, security,
accessibility, supported compatibility, and active migrations.

Require the repository's applicable checks, real-surface proof, and one current
independent review for that head. Use one bounded whole-change review by
default; use `/security-review` when the change crosses a trust boundary.
Confirm findings against current source. A release blocker must be caused or
worsened by this change and make release unsafe. Repair it at the delivery
owner; a changed head starts Finalize again.

Confirm repository-owned deploy, health, smoke, and rollback paths. Persisted
state changes require migration and rollback evidence.

## Ship

Immediately recheck the head and review state. Merge through the normal path
with its expected-head condition, record the merge revision, and verify it maps
to the reviewed head. Wait for existing post-merge checks; stop before deploy
on an identity mismatch or failed check.

Deploy the verified merged artifact through the owned path. Record an immutable
runtime identity, artifact digest, deployment record, or equivalent evidence
binding it to the merge revision. An unknown artifact or failed identity check
enters Recover.

## Verify production

Watch the deploy finish, then verify production: run health and repository
smoke checks, exercise affected production surfaces, read back changed state,
and inspect relevant logs, metrics, traces, or Sentry signals. Record actions
and observations. No fixed soak window is required.

## Recover

Preserve failure evidence. Run one authorized repository-owned rollback or
reinstall of the prior artifact. Verify restored identity, health, smoke, state,
and affected surfaces. A fix-forward needs a separately accepted change and a
new `/release`.

## Report

Return the final head and merge revision, checks and production proof, review
result, deployed identity, and recovery action or pre-deploy failure.
