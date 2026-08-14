---
name: thermo-nuclear-code-quality-review
description: Grill, fix, verify, and re-review a completed change until no supported finding remains.
disable-model-invocation: true
---

# Thermo-Nuclear Code Quality Review

Run a closed repair loop:

```text
grill -> findings -> fix -> proof -> review again
```

## Boundary

Identify:

- requested outcome and acceptance;
- changed paths and affected callers;
- unchanged invariants;
- commands or scenarios that prove the change.

Read the complete relevant implementation, not only the diff. Keep the review
inside this boundary.

## Grill

Question each new requirement, layer, branch, state value, fallback,
compatibility path, seam, and option:

- Which outcome requires it?
- Which existing interface could replace it?
- Can it disappear?
- Who owns its state and transitions?
- Which failure or invalid state did it add?
- Does it fix the source or hide a symptom?

Audit:

- correctness, boundaries, errors, races, security, and real-surface behavior;
- obsolete paths, duplicate authority, leaked state, thin wrappers, special
  cases, and speculative flexibility;
- control flow, types, names, hidden invariants, duplication, and avoidable
  allocation, copy, serialization, or recomputation.

Counts support findings; they do not justify them. Use `grill-me` only when a
material product or design choice remains operator-owned.

## Findings

Each finding needs:

- exact file, symbol, or behavior;
- concrete failure or maintenance mechanism;
- evidence;
- smallest source repair;
- observable proof.

Exclude taste, cosmetic nits, and speculation. Zero findings is valid.

## Fix

Track every finding. Delete unnecessary code first. Then use the existing direct
interface or simplify the necessary design. Migrate every caller and remove
obsolete aliases, tests, comments, configuration, and documentation.

Fix the source. Do not suppress the warning or special-case the observed input.

## Prove and repeat

Run the narrowest real scenario for each repair, then applicable contract tests.
A failed check is a new finding.

Restart the review over the same boundary, including the fixes. Finish only when:

- no supported finding remains;
- every finding is fixed or invalidated by evidence;
- changed behavior and invariants pass;
- no obsolete path remains.

Report repaired findings, deleted complexity, exact proof, and the clean final
review. Name any external blocker; do not claim a clean review around it.
