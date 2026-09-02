---
name: groom
description: >
  Investigate a named backlog scope through the default design lenses,
  then reconcile the board with product direction and evidence.
disable-model-invocation: true
argument-hint: "[project, repository, board scope, or item IDs]"
---

# Groom

Groom the operator's named scope. The default is a deep investigation from
every default lens. Explicit conversational context may narrow that scope,
including to one ticket or decision.

## Default lenses

Dispatch one subagent per required lens in a single batch. Each agent reads
`skill://<name>` first and reports only on the named scope.

Always, unless the operator names a smaller set:

- `agent-ergonomics`
- `audit-observability`
- `audit-simplifications`
- `custom-linters`
- `core-docs`
- `extract-module`
- `foundation`

These use `scout` unless a more specific read-only agent exists.

`torvalds-design-review` stays in the default set as a conditional bounded
reviewer. Send one packet to `torvalds-reviewer` only when the named scope
contains a load-bearing or hard-to-reverse design. Skip it when none is in
scope.

The operator may add lenses. Drop a default lens only when the operator
names a smaller set.

Skip formatters, linters, and project-wide suites in the batch. Do not
mutate the board or the repository during Understand.

## Understand

Use [`../backlog/SKILL.md`](../backlog/SKILL.md) to read the affected items
and direct relations.

Run the default lens batch. Synthesize findings into backlog, roadmap,
and vision implications.

State the largest mismatch between the board and current evidence. Ask one
focused question when product intent remains open.

Done when the operator can decide the named issue.

## Reconcile

Challenge unsupported work, merge duplicate ownership, and prefer an existing
interface or owner. Once the operator settles a choice, apply its reversible
Powder mutations without another approval ceremony. Ask again only for added
scope, cost, risk, or irreversible effect.

Use current CLI help. Preserve live leases and never take work merely to groom
it. Batch the accepted mutations, then read the changed items and their direct
relations once.

Return changed, unchanged, and unresolved item IDs with reasons and the next
material choice.

Done when the scoped decisions are stored, no lease changed, and readback
matches the accepted outcome.
