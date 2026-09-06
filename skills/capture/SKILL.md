---
name: capture
description: Reconcile durable conversation findings with the project's trusted work record.
disable-model-invocation: true
argument-hint: "[optional project or scope]"
---

# Capture

Persist only durable decisions, defects, risks, and work. Do not create a
duplicate backlog item.

## Distill

Read the active conversation and project policy. For each candidate, state the
outcome, evidence, scope, consequence, open choice, owner, and proof. Classify
it as create, reconcile, or omit with a reason. Omit transient status and
unsupported ideas.

## Reconcile and write

Search the trusted record by subject and outcome. Update the existing owner;
create an item only when no owner exists. Link superseded and dependent work.
Store the smallest complete record, preserve exact evidence and boundaries, and
do not change product code.

Read changed items through the record's normal interface. Return created,
updated, linked, and omitted items with reasons.
