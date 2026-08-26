---
name: torvalds-design-review
description: Ask one Torvalds-style critic whether a load-bearing design should exist in its current form.
disable-model-invocation: true
argument-hint: "[system, design, or solution]"
---

# Torvalds design review

Use this read-only review for a load-bearing or hard-to-reverse design. It asks
whether the system has the right data and ownership, not whether the diff is
polished.

## Bind

State the problem, workload, current design, data owners, invariants,
constraints, accepted decisions, assumptions, alternatives, and primary
evidence. Name the exact target and revision.

Done when the critic can judge the system without inventing context.

## Dispatch

Send exactly one complete packet to `torvalds-reviewer`. Ask: Would this system
be designed this way from scratch today? If not, what data structure, owner, or
boundary is fundamentally wrong? Require direct evidence, deleted complexity,
migration cost, and the first reversible move.

Done when the specialist returns one explicit verdict.

## Ground

Check the verdict's factual claims against the supplied primary records. Mark
unsupported claims without softening the central judgment. Return: direct
answer, load-bearing flaw or strength, evidence, rejected alternative, migration
risk, and first reversible action.

Done when the operator can accept, reject, or test the verdict.
