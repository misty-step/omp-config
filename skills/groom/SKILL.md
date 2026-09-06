---
name: groom
description: Reconcile a named backlog scope through only evidence-bearing review lenses.
disable-model-invocation: true
argument-hint: "[project, repository, board scope, or item IDs]"
---

# Groom

Reconcile the Operator's named Powder scope. Investigate only questions that
can change an item's disposition, priority, owner, or proof.

## Ground

Read affected items and direct blockers, duplicates, proofs, and owners. For
Misty Step, run `powder skill`. Read source, decisions, pull requests, or the
running product only when an item's disposition depends on that claim. State
the largest evidence mismatch and separate fact, inference, and operator choice.

## Select lenses

Choose only independent questions that can change the named decision:
agent control and feedback; release identity and recovery; deletable
representation or owner; executable control for recurring defects; missing
operating or domain fact; coupling at a proposed boundary; or a missing build,
test, release, or recovery prerequisite.

Dispatch selected read-only tasks in one batch, using `scout` unless a more
specific reader exists. Give each task the same scope, intent, evidence limit,
and output contract. Require exact evidence and the smallest correction.
Use `torvalds-reviewer` once only for a load-bearing or hard-to-reverse design.

## Reconcile

Merge supported findings, challenge unsupported work, merge duplicate ownership,
and prefer an existing interface. Ask one focused question only when product
intent remains open. Apply accepted Powder mutations without another approval
round; ask again only for added scope, cost, risk, or irreversible effect.
Preserve live leases, never take work merely to groom it, and read back changed
items and direct relations once.

Return changed, unchanged, and unresolved item IDs with reasons and the next
material choice.
