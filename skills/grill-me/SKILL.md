---
name: grill-me
description: Grill unresolved operator-owned design choices before non-routine implementation. Skip tool-answerable facts and fully specified work.
license: MIT; modified from Matt Pocock's grill-me and grilling skills
---

# Grill Me

Resolve material choices before implementation.

## Gate

1. Inspect governing sources, code, runtime, and tools.
2. Try deletion and direct use before a new mechanism.
3. Proceed without an interview when evidence leaves one viable design.

## Interview

Build a decision tree. Ask the current frontier: all material choices whose
prerequisites are settled.

Use one `ask` call per frontier:

- Give 2–5 distinct options and one recommendation.
- State the behavior, cost, risk, or operating-burden difference.
- Include deletion, no change, or direct use when viable.
- Do not repeat settled questions or ask downstream questions early.

Apply the answers, prune invalid branches, and ask the next frontier. Question
scope, ownership, state, failure behavior, migration, security, compatibility,
and proof only when the answer can change the design.

## Exit

Stop when no material operator-owned choice remains. Show a compact lock:

- outcome and authority;
- accepted decisions and rejected alternatives;
- non-goals and invariants;
- proof and stop condition;
- remaining assumptions.

Proceed when the original request authorized implementation and the lock did not
expand scope. Require a new approval only for design-only work, material scope
growth, or a destructive choice.
