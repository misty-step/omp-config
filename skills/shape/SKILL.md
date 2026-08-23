---
name: shape
description: Turn one rough idea into a groomed, option-tested, locked implementation spec.
disable-model-invocation: true
argument-hint: "[idea, ticket, or problem]"
---

# Shape

One idea becomes one buildable spec. No production edits.

```text
brainstorm -> brief -> groom -> map unknowns -> fan designs -> choose -> lock spec
```

## 1. Brainstorm and brief

Collect candidate outcomes before selecting a solution. Include doing nothing,
deleting the problem, and using the current interface directly. Group duplicate
ideas by the user problem they solve.

Name the user, problem, observed evidence, desired outcome, and reason to act
now. Separate facts, assumptions, and requests. Find the current system and
ledger state when they exist. Write `Unknown` when evidence is absent.

Completion criterion: One evidence-backed problem statement survives, and no
invented context remains.

## 2. Groom

Challenge each requirement. Delete anything without an owner, protocol,
production observation, or code invariant. Split the idea until one slice has:

- one user-visible or operator-visible outcome;
- one owner and one data path;
- explicit non-goals;
- a real-interface proof;
- a release and rollback boundary.

Defer unrelated cleanup and speculative flexibility. Record dependencies and
blocked prerequisites in the trusted ledger.

Completion criterion: One independently useful slice is ready for decisions.

## 3. Map unknowns

If a completed `/explore-unknowns` map does not cover this slice, stop and ask
the operator to run `/explore-unknowns` with the groomed problem statement.
Resume only from the completed map.

Every material choice must be closed by evidence or by the operator. Small
implementation facts can remain as builder checks. Product intent, scope,
compatibility, operating burden, spend, and irreversible choices cannot.

Completion criterion: The map has no open material choice.

## 4. Fan options

Dispatch at least three read-only design scouts in parallel. Give each the
problem, map, invariants, proof, and one distinct hypothesis:

1. delete or use the existing interface directly;
2. the smallest boring design;
3. a materially different data or ownership model.

Add a domain specialist only when the slice needs one. Each scout returns:
core data model, owners, state transitions, failure semantics, interface,
migration, proof, deletions, and the evidence that would falsify its option.

Completion criterion: Three genuinely different options account for every
invariant and material failure path.

## 5. Choose

Compare whole-system complexity. Prefer one owner per datum, illegal states
that cannot exist, deep modules, direct paths, and replaceable technology.
Reject options that move complexity to callers, operators, migration, or
recovery.

For a load-bearing or hard-to-reverse architecture, stop and ask the operator
to run `/torvalds-design-review` on the leading option. Resume from its verdict.
Present the choice, rejected options, and evidence to the operator. Record the
operator's decision.

Completion criterion: One option is selected with explicit tradeoffs.

## 6. Lock the spec

Produce one spec with this contract:

```markdown
# <Outcome>
## Problem and evidence
## User and job
## Decision and rejected options
## Data, ownership, and invariants
## Interfaces and behavior
## States, transitions, failures, and recovery
## Compatibility and migration
## Security and operational constraints
## Acceptance scenarios
## Test portfolio
## Product-surface QA matrix
## Release, rollback, and production signals
## Implementation slices
## Non-goals and reconsideration triggers
## Open builder checks
```

Acceptance scenarios cover happy, risky, boundary, illegal, interrupted, and
recovery paths. The QA matrix names each affected real surface, adjacent path,
fixture, action, and observable result. Implementation slices are independently
provable and ordered by dependency.

The operator must explicitly accept the spec. Silence, partial approval, and a
prototype preference are not acceptance. Store the accepted spec where the
project keeps durable decisions or on the trusted work item.

Completion criterion: The accepted spec lets a builder implement without
making a material product or architecture decision.