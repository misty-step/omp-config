---
name: release
description: Finalize one pull request, merge it, deploy it, prove production, and recover on failure.
disable-model-invocation: true
argument-hint: "[pull request]"
---

# Release

A release is complete when the exact reviewed change works in production. A
timer does not prove that. `/release` authorizes the named pull request's normal
merge and deploy plus one ordinary rollback. It does not authorize candidate
mutation, unrelated changes, history rewrites, force-pushes, or tags.

## Finalize

Record the exact pull request head. Read its accepted intent, complete diff,
affected contracts, current comments and formal review state, checks, and
linked evidence.

Inspect every changed file and enough surrounding code to judge each addition.
Require no unnecessary debug or diagnostic code, dead or scaffold code,
temporary flags or shims, unsupported fallbacks, speculative defenses, exposed
state, interface fields, or abstractions. Treat migration or backfill logic as
a Blocker only when the rollout contract proves it is no longer needed.
Preserve purposeful observability, error handling, security, accessibility,
supported compatibility, documented flags, and active migration paths.

Require the repository's existing applicable validation and real-surface proof
for that exact head.

Require one current independent review result for that head. A Blocker must be
caused or worsened by the change and make release unsafe. One bounded
whole-change review is the default. Review a repair only; repeat the whole
review only when the repair materially changes the risk surface. Require one
focused security review when the change crosses a trust boundary.

Confirm or reject every current actionable finding with evidence. A supported
Blocker returns the candidate to its delivery owner. Any resulting head starts
Finalize again; non-blocking observations do not expand this release.

Confirm repository-owned deploy, health, smoke, and rollback paths apply.
Require migration and rollback proof for persisted-state changes.

Done when the exact head is clean, proved, independently reviewed, and has no
unresolved Blocker.

## Ship

Immediately before merge, confirm the head and current review state again. A
changed head or supported Blocker returns to Finalize.

Merge through the repository's normal path using the hosting platform's
expected-head condition. Record the platform merge revision and verify that it
maps to the reviewed head. Wait for existing post-merge checks. A wrong merge
identity or failed post-merge check stops before deploy and uses the
repository's normal source rollback when available.

Deploy the verified merged artifact through the owned path. Record an immutable
runtime identity, artifact digest, deployment record, or equivalent evidence
that binds it to the merge revision. A wrong or unknown artifact, failed deploy,
or failed identity check is red and enters Recover.

Done when production runs the intended artifact, recovery has started, or a
pre-deploy failure is safely owned.

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

Preserve the failure evidence. Run one authorized repository-owned production
rollback or reinstall the prior artifact. Verify the restored identity, health,
smoke, state, and affected surfaces. Tell the operator what failed and what
changed.

A fix-forward requires a separately accepted pull request and a new `/release`
invocation. If recovery fails or the runtime identity is unknown, stop mutation
and escalate.

Done when production is healthy on a known revision or the incident is safely
owned.

## Report

Return the final head and merge revision, cleanup gate, validation and
production proof, review result, deployed identity, and recovery action if any.
