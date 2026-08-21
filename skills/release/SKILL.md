---
name: release
description: Merge and deploy a review-ready pull request through the repository's protected path, then verify the running release.
disable-model-invocation: true
---

# Release

Explicit invocation only. One review-ready PR. Merge, deploy, verify.

## Gate

Proceed only when every condition holds:

- the operator explicitly requested this release;
- required CI checks pass on the exact head being merged;
- required human approval exists;
- no unresolved blocking finding remains on the pull request;
- evidence links open and show the claimed observations.

Any failure blocks the release. Report which condition failed and stop.

## Merge

Merge through the repository's protected path. Never force-push, rebase the
protected branch, or bypass branch protection.

## Deploy

Deploy the merged immutable revision — the merge result or its built
artifact, never the pre-merge head. Use the repository's own deploy path.

## Verify

Run the repository-owned health check against the deployed release.

On success: record the release identity and the rollback path, and capture
deployment evidence per `skill://evidence-packet`.

On failure: invoke the repository-owned rollback immediately. Verify the
restored health check and record which revision is running again. Capture
the failure evidence — health output, release identity, and the observed
defect — per `skill://evidence-packet`, then report the blocked release. Do
not retry the deploy without an operator decision.

You are done when the deployed release answers its health check and the
operator knows what is running and how to roll it back — or when a failed
release is rolled back, evidenced, and reported as blocked.

