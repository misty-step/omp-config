---
name: groom
description: Reconcile a named backlog scope through only the evidence-bearing review lenses.
disable-model-invocation: true
argument-hint: "[project, repository, board scope, or item IDs]"
---

# Groom

Groom the Operator's named scope. Investigate only questions whose answers can
change an item's disposition, priority, owner, or proof.

## Ground

Read the affected items and their direct blockers, duplicates, proofs, and
owners. For Misty Step, run `powder skill`. Read source, decisions, pull
requests, or the running product only when an item's disposition depends on the
claim.

State the largest mismatch between the board and current evidence. Separate
fact, inference, and Operator choice.

Done when the controlling items, relations, and unresolved decision are
explicit.

## Select lenses

Select only independent lenses that can change the named decision. Typical
lenses ask:

- Can the acting agent understand, control, and observe the workflow?
- Can an operator identify the failed release, impact, and recovery action?
- Can the system delete a representation, owner, state, or coordination path?
- Does a recurring decidable defect justify an executable control?
- Is a non-obvious operating or domain fact missing from its owning document?
- Does a proposed module boundary remove more coupling than it creates?
- Is one missing build, test, release, or recovery control blocking safe change?

Dispatch one read-only subagent per selected lens in one batch. Use `scout`
unless a more specific read-only agent exists. Give every task the same scope,
accepted intent, evidence boundary, and output contract. Require exact evidence,
the smallest coherent correction, and a clean result when no finding survives.
Skip repository mutation, board mutation, formatters, linters, and project-wide
test suites.

Use `torvalds-reviewer` once only when the scope contains a load-bearing or
hard-to-reverse design. No minimum lens or agent count applies.

Done when each selected lens has a decision-changing reason and no two lenses
own the same question.

## Reconcile

Synthesize the supported findings into backlog, roadmap, and vision
implications. Challenge unsupported work, merge duplicate ownership, and prefer
an existing interface or owner.

Ask one focused question when product intent remains open. Once the Operator
settles it, apply the reversible Powder mutations without another approval
round. Ask again only for added scope, cost, risk, or irreversible effect.

Use current CLI help. Preserve live leases and never take work merely to groom
it. Batch accepted mutations, then read back the changed items and their direct
relations once.

Return changed, unchanged, and unresolved item IDs with reasons and the next
material choice.

Done when the scoped decisions are stored, no lease changed, and readback
matches the accepted outcome.
