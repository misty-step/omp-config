---
name: agent-ergonomics
description: Rework system designs and plans into one legible agent control surface.
disable-model-invocation: true
argument-hint: "[system, design set, or plan set]"
---

# Agent ergonomics

Treat the named scope as one system the agent must understand, control, observe,
and improve. Update its design documents and plans; leave production artifacts
unchanged.

## Ground the cockpit

Read the accepted outcome, current system, source design documents, plans, and
real interfaces. Identify the acting agent, system boundary, authoritative
state, available controls, feedback, operating constraints, and resource costs.
Separate observed facts, accepted decisions, assumptions, and open human
choices.

Trace one representative outcome end to end from the agent's seat. At each
choice, state what the agent can know, what it can do, and how it learns the
result.

Done when the trace exposes every material information, control, and feedback
gap inside the boundary.

## Recompose the system

Design one coherent tower of abstractions around clear owners, invariants,
state transitions, and narrow interfaces. Optimize for:

- progressive disclosure and exact context at each decision;
- direct, reversible controls with explicit preconditions;
- fast, inspectable feedback and loud boundary failures;
- one authoritative representation for each fact and decision;
- reusable evidence and knowledge that compound without stale caches;
- the least tool calls, context, coordination, computation, and operator work.

Challenge unsupported requirements first. Delete duplicate representations,
pass-through layers, hidden state, and compensating workflows before adding a
new mechanism. Compare alternatives only where they change a material outcome,
risk, cost, or operating burden.

Done when every remaining component pays for its state, boundary, and agent
attention, and every abstraction links to the layers above and below it.

## Rewrite the record

Update every in-scope design document and plan that the new system changes.
Make each decision authoritative in one place; replace obsolete decisions,
steps, diagrams, terminology, and cross-references in the same pass. Keep
implementation slices ordered by dependency, independently useful, and paired
with observable acceptance evidence.

Route unresolved product, compatibility, spend, operating, or irreversible
choices to the operator with evidence and one recommendation. Record settled
answers in the owning document.

Done when an implementation agent can proceed without reconstructing the
architecture or inventing a material decision.

## Drive the revised cockpit

Replay the representative outcome against the revised documents. Confirm that
each decision has sufficient context, each action has an unambiguous control,
each result is observable, and each durable fact has one owner. Check failure,
recovery, and the highest-cost resource path.

Return the changed records, deleted complexity, resulting system model, proof
from the replay, and any blocked human choice.

Done when the documents describe one operable system rather than an assemblage
of plans and components.
