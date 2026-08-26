---
name: shape
description: Turn one rough idea into an accepted, buildable slice.
disable-model-invocation: true
argument-hint: "[idea, ticket, or problem]"
---

# Shape

Shape prevents builders from inventing product or architecture decisions. It
turns one evidenced problem into one accepted slice. It makes no production
edits.

## Ground

Read the request, current system, binding decisions, and trusted work record.
State the user or operator, observed problem, desired outcome, and reason to act.
Separate facts from assumptions. Mark missing evidence as unknown.

Done when one evidence-backed problem statement remains.

## Cut

Challenge every requirement. Prefer deletion or the current interface. Keep the
smallest independently useful slice with:

- one outcome, one owner, and one data path;
- explicit invariants and non-goals;
- affected interfaces and failure behavior;
- real-interface proof;
- release and rollback boundaries when applicable.

Any persisted format, schema, meaning, or default change is high risk. It needs
migration, readback, compatibility, and rollback proof. A required but absent
migration blocks the slice.

Done when unrelated cleanup and speculative flexibility are outside the slice.

## Settle

Resolve implementation facts from source. Ask the operator only about material
human choices: outcome, scope, compatibility, spend, operating burden, or an
irreversible action. Present concrete options, evidence, tradeoffs, and a
recommendation in one concise question set.

Compare alternatives only when the choice is real. Include deletion, direct use
of the current interface, and the smallest boring design. Request
`/torvalds-design-review` only for a load-bearing or hard-to-reverse design.

Done when no material choice remains open.

## Lock

Write the accepted spec with: problem and evidence; decision and rejected
alternatives; data owners and invariants; interfaces and behavior; states and
failures; compatibility or migration; acceptance scenarios; proof; release and
rollback; non-goals; ordered slices.

The operator must accept the spec. Store it in the project's trusted record.

Done when a builder can implement without making a material product or
architecture decision.
