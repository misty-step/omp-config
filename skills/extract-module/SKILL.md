---
name: extract-module
description: Map and design a subsystem extraction without changing production code.
disable-model-invocation: true
argument-hint: "[subsystem or module path]"
---

# Extract module

Extraction adds a boundary, release path, and migration. It is useful only when
those costs remove more coupling than they create. This skill produces a
blueprint, not code.

Walk these references in order. Finish one before opening the next:

1. `references/stage-1-coverage-coupling-map.md`
2. `references/stage-2-deletion-gate.md`
3. `references/stage-3-boundary-interface-design.md`
4. `references/stage-4-extraction-blueprint.md`

Use current source, callers, tests, generated contracts, build wiring, runtime
state, and release paths. Count both sides of every boundary. Reject the
extraction when a direct internal module removes the same problem with less
operational weight.

Done when the blueprint names the interface, owners, callers, migration,
deletions, package or repository boundary, validation, rollout, rollback, and
proof—or concludes that extraction should not happen.
