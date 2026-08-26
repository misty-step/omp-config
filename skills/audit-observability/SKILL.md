---
name: audit-observability
description: Audit whether operators can detect, explain, and recover material system failures.
disable-model-invocation: true
argument-hint: "[repo-or-system]"
---

# Audit observability

Observability exists to answer: what failed, who was affected, which release
caused it, and how to recover. An installed SDK or green health check does not
prove those answers. This audit is read-only.

## Bound the system

Record the repository, revision, dirty state, deployed identities, environments,
components, stores, dependencies, owners, and exclusions. Use repository and
infrastructure authority before inference. Run only safe read probes.

Done when every material runtime and operator boundary is accounted for.

## Map failures to signals

For each component and material failure path, trace:

`failure -> producer -> transport -> backend -> query -> alert -> owner -> recovery`

Keep health, errors, logs, traces, metrics, release identity, and product signals
separate. Verify semantics, correlation, redaction, sampling, retention,
freshness, cost, and tenant boundaries. Mark claims as observed, source-proven,
inferred, unavailable, or drifted.

Done when each failure path has evidence or an explicit gap.

## Judge coverage

A finding states the failed operator question, mechanism, impact, current
control, primary evidence, smallest repair, owner, and proof. Prioritize silent
failure, wrong release identity, missing correlation, sensitive-data exposure,
and recovery without evidence. Do not recommend a vendor before the required
signal and owner are clear; research current provider behavior when a choice is
necessary.

Done when every finding is evidence-backed and deduplicated.

## Deliver

Return the controlling verdict, system map, coverage matrix, findings,
context/redaction contract, provider decisions, alert routes, and a
deletion-first remediation plan. Each slice names files, data paths, migration,
validation, rollout, rollback, and acceptance proof. Do not implement it.

Done when a builder can close each material gap without rediscovering the
system.
