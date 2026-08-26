---
name: refactor
description: Remove one evidenced architectural constraint without changing accepted behavior.
disable-model-invocation: true
argument-hint: "[module, subsystem, or debt target]"
---

# Refactor

A refactor earns its migration cost by deleting a real constraint, invalid
state, dual owner, or leaking boundary. Cleaner-looking code is not enough.

## Bound

Name the target, current friction, evidence, preserved behavior, owners,
callers, and proof. Isolate the work from the operator's checkout.

Done when one measurable architectural outcome is explicit.

## Redesign and migrate

Prefer deletion, one representation, one owner, and a deep direct interface.
Account for migration, operations, allocation, and hot-path cost. Implement the
smallest coherent cutover. Migrate every caller and delete obsolete adapters,
shims, state, configuration, and tests.

Done when the old path has no caller or owner.

## Prove and publish

Run affected contract checks and real-surface smoke scenarios. Compare behavior
with the baseline; add characterization only for an uncovered observable
contract. Inspect the diff for moved complexity.

Open an unmerged pull request with the constraint removed, design decision,
deletions, checks, evidence, risk, and rollback.

Done when behavior is preserved and the named constraint no longer exists.
