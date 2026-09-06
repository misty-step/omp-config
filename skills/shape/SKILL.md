---
name: shape
description: Turn an evidenced problem or boundary proposal into one accepted, buildable slice.
disable-model-invocation: true
argument-hint: "[idea, ticket, or problem]"
---

# Shape

Turn one evidenced problem into one independently useful slice. This is
design-only; do not edit production artifacts.

## Ground

Read the request, current system, binding decisions, and trusted work record.
State the user or operator, observed problem, desired outcome, and reason to
act. Separate facts, assumptions, and unknowns.

## Trace the boundary

For a proposed extraction or control surface, trace exports, callers,
dependencies, shared state, and release paths. Prefer deletion or an internal
reorganization when it removes the same coupling without a new release path.
Trace one representative outcome from the acting agent's seat: what it can
know, control, and observe at each decision. Expose information, control,
feedback, resource, and ownership gaps.

## Cut

Challenge every requirement. Keep the smallest slice with:

- one outcome, owner, authoritative data path, and coherent control surface;
- explicit invariants, state transitions, non-goals, and failure behavior;
- affected interfaces, callers, operations, and real-interface proof;
- release and rollback boundaries when the change warrants them.

Persisted formats, schemas, meanings, and defaults require migration, readback,
compatibility, and rollback evidence. An absent required migration blocks the
slice. Delete duplicate representations, pass-through layers, hidden state,
and speculative flexibility.

## Settle

Resolve implementation facts from source. Ask only about material human choices:
outcome, scope, compatibility, cost, operating burden, or irreversible action.
Compare alternatives only when they change a material outcome, risk, or burden.

For a load-bearing or hard-to-reverse design, dispatch one read-only review to
`torvalds-reviewer` with this packet: problem, workload, target and revision,
current design, binding constraints, accepted decisions, and primary evidence.
Ask whether data ownership, representations, state transitions, boundaries, and
caller burden solve the problem with less complexity than credible alternatives.
Check factual claims against supplied sources. Return verdict, strength or flaw,
evidence, migration risk, and the first reversible move.

## Lock

Write the accepted spec to the trusted record: problem and evidence; decision
and rejected alternatives; owners, invariants, interfaces, states, failures;
compatibility or migration; acceptance scenarios and proof; release, rollback,
non-goals, and ordered slices. Leave any unresolved material choice explicit.
