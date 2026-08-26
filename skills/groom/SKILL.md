---
name: groom
description: Reconcile the backlog with product direction, code reality, and deliberate tradeoffs through conversation.
disable-model-invocation: true
argument-hint: "[project, repository, or board scope]"
---

# Groom

Grooming is a conversation about the portfolio, followed by exact ledger
readback. It does not claim work or change product code.

## Establish reality

Read [`../backlog/ASSESS.md`](../backlog/ASSESS.md) and perform every step.
Present its snapshot compactly before proposing a board change.

Done when the operator can see the complete board, its evidence limits, and the
largest mismatch between the board and current reality.

## Walk the portfolio

Take the highest-leverage mismatch first. State the evidence and current
interpretation in a few sentences. Ask one focused question per turn and let
the answer determine the next question. If the operator requests a batch, group
only independent choices.

Cover each material branch before closing:

- **fit** — missing outcomes, stale premises, duplicates, delivered work,
  drafts, false blockers, and work that no longer matters;
- **product** — the user, painful outcome, durable vision, current direction,
  and the concrete use bar that makes the product worth operating;
- **reality** — capabilities that exist, what is verified or deployed, rough or
  unreliable paths, and design or operational constraints visible in source
  and the real interface;
- **balance** — which capability unlocks a named outcome, which polish repairs a
  valuable existing path, and which system change removes owners, states, data
  paths, migration burden, or operator work.

Treat vision as the durable destination, direction as the present strategic
bet, and the codebase as current fact. Take product strategy from accepted
operator decisions; otherwise mark the exact unknown.

Done when every theme has an explicit fit with vision, direction, and current
reality, or one named open choice.

## Apply taste

Challenge each item in this order:

1. What accountable user or operator outcome and evidence require it?
2. Can the item, requirement, or obsolete path be removed?
3. Can one existing interface, owner, representation, or data path satisfy it?
4. Is capability work necessary for the use bar, or does the existing path need
   correctness, operability, or polish first?
5. Does the proposed design reduce whole-system complexity six months out?

Keep necessary complexity at the edge that earns the product value.
Architectural novelty, aesthetic rewrites, speculative flexibility, and age by
itself are insufficient reasons for work. Keep priority as an explicit
discussion output: Powder list order remains creation order, and titles and
blockers retain their real meanings.
Done when each in-scope item has a reasoned disposition: keep, update,
abandon, merge into one owner, report delivered, or leave unknown.

## Reconcile decisions

As the operator settles a choice, add the exact Powder operation to a visible
change set. Once the choice and consequence are explicit, apply reversible
board edits without a second approval ceremony. Ask again only when the
operation would add scope, risk, cost, or an irreversible effect that the
conversation did not settle.

Use the board's normal CLI and current `--help`:

- strengthen incomplete titles, specs, repositories, and direct blockers;
- create missing work only when no existing item owns the outcome;
- merge duplicates by updating the surviving item, noting its ID on the
  duplicate, and abandoning the duplicate with its history intact;
- abandon unsupported or superseded work with the reason recorded;
- report delivered items with their cited proof for the owning worker or delivery
  step; `powder done` requires an active worker lease;
- leave a live-held item with its holder; record the proposed change rather than
  taking, releasing, or editing it;
- never take a job merely to groom it.

After each mutation, read the item through `powder show`. At the end, read the
full in-scope list again and reconcile the counts and relations against the
opening snapshot.
Return updated, created, abandoned, merged, delivered-unclosed, unchanged, and
unresolved items, with IDs and reasons. State the resulting product direction
and the next material operator choice. Keep any recommended sequence in the
report rather than storing invented rank.

Done when every accepted decision is stored and verified, no lease changed,
state totals reconcile, and every unresolved human choice is explicit.