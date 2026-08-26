---
name: audit-choices
description: Expose consequential choices an implementation made without changing code or blocking delivery.
disable-model-invocation: true
license: MIT; from dzhng/skills audit-choices
---

# Audit choices

Working code can hide product and architecture decisions the operator never
made. This audit makes those choices visible. It is read-only and never blocks.

## Trace

Read the request, accepted decisions, implementation history, diff, and running
behavior. Find choices made where the evidence or specification allowed more
than one material answer. Ignore routine implementation facts.

Done when every material invented choice has an owner and source.

## Judge

Classify each choice:

- **Sound:** follows evidence or an accepted invariant.
- **Unsound:** conflicts with evidence, intent, or system ownership.
- **Needs operator:** changes outcome, scope, compatibility, spend, burden, or irreversible risk.
- **Deferred:** reasonable but outside this change.

Do not turn code style or speculative alternatives into choices.

Done when each verdict names its evidence and consequence.

## Record

Append concise entries to the work item's durable decision record. Each entry
states the choice, why it arose, evidence, verdict, consequence, and next owner.
Route repeated material ambiguity to `/shape`. Consolidate superseded entries
when the work ships.

Return the ledger location and a count by verdict. Make no production edit.

Done when a future builder can distinguish accepted design from accidental
implementation.
