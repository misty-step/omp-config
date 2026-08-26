---
name: audit-simplifications
description: Find material whole-repository simplifications in data, state, control flow, and ownership.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Audit simplifications

This read-only audit finds complexity the system does not need. It does not edit,
test, commit, or push.

## Cover

Map every subsystem and cross-cutting owner. Record one row per boundary and mark
it `review` or `skip` with a reason. Include generated contracts, tooling, and
operator paths when they own behavior.

Done when no subsystem is hidden inside a catch-all row.

## Review

For each row, ask in order:

1. Can the requirement or path be deleted?
2. Can one representation, state, owner, or data path replace several?
3. Can a direct interface replace coordination or pass-through layers?
4. Can invalid states become impossible?
5. Does the repair reduce whole-system work, including migration and operations?

A finding needs exact symbols, current mechanism, evidence, smallest coherent
change, deletions, migration, risk, and proof. Style, naming, speculative
flexibility, and unsupported rewrites are not findings.

Done when every row has a grounded recommendation or skip.

## Validate and deliver

Recheck each finding against current source and callers. Deduplicate shared root
causes. Rank by deleted complexity, defect risk, and migration cost. Return the
coverage map, confirmed findings, rejected candidates, dependencies, and
ordered implementation slices.

Done when every recommendation can be implemented without another repository
survey.
