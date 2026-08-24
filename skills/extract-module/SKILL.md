---
name: extract-module
description: Multi-stage investigation for extracting a subsystem into an isolated package or repository.
disable-model-invocation: true
argument-hint: "[subsystem or module path]"
---

# Extract Module

Splitting multiplies boundaries. A boundary without a map is a guess; a map
without a deletion pass is a heavier guess. This skill produces the
investigation artifact — coupling map, pruned scope, interface contract,
dependency matrix, and phased cutover blueprint — before any extraction edit.

Implementation is a separate task that starts only after the blueprint is
complete. Read `skill://ast-grep` for structural search; use `lsp references`
for symbol-aware fan-in and fan-out.

```text
coverage & coupling map -> deletion gate -> boundary & interface -> extraction blueprint
```

Default to the invocation target. When none is named, take the subsystem or
directory the operator names in the first reply.

## The Pipeline

Walk four stages in order. **When you enter a stage, read its reference file
and follow it.** Finish the stage in front of you before opening the next.

1. **[Coverage & coupling map](references/stage-1-coverage-coupling-map.md)** —
   discover subsystems, measure fan-in vs fan-out, trace leakages, and surface
   circular imports.
2. **[Deletion gate](references/stage-2-deletion-gate.md)** — shrink scope:
   delete speculative abstractions, single-impl interfaces, dead flags, and
   pass-through adapters before designing the split.
3. **[Boundary & interface design](references/stage-3-boundary-interface-design.md)** —
   define the minimal public API, internalize private state, and build the
   third-party dependency matrix.
4. **[Extraction blueprint & phased cutover](references/stage-4-extraction-blueprint.md)** —
   Phase 1 in-tree isolation, Phase 2 workspace package, Phase 3 external
   package or standalone repository.

The walk ends with the assembled artifact from
[artifact templates](references/artifacts.md) in the operator's hands.

## Rules

- Walk stages in order. No extraction edit until Stage 4's blueprint is
  complete and every stage's completion criterion is met.
- Fan-in and fan-out come from `lsp references` and structural search — not from
  import-line counts alone. Cite symbol paths and file:line evidence.
- The deletion gate runs before boundary design. A split that preserves dead
  weight is not a split; it is a move.
- Every leakage (type, constant, config key, test fixture, error string) is
  named with an owner: **extract**, **caller adapts**, **delete**, or **shared
  kernel** — never "figure out later".
- Circular imports block extraction. Record each cycle with its participating
  modules; the blueprint names the break strategy before cutover.
- Claims about the codebase cite files actually read. Invented coupling is a
  failed investigation.
- Stop at stage boundaries that need operator judgment on scope, ownership, or
  cutover target (in-tree vs workspace vs external). Implementing is a
  separate task.
