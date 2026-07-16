---
name: deliver
description: |
  Deliver one routed ticket end to end: make the contract executable, build
  the smallest coherent change, prove the live outcome, review it, and leave
  it merge-ready or ship when explicitly asked. Use for "deliver this",
  "build this ticket", "make it merge-ready", "take this end to end".
  Trigger: /deliver.
argument-hint: "[ticket|description]"
---

# /deliver

Take one work card from intent to durable proof. `/deliver` is the composer;
the specialist skills own shaping, verification, review, CI, and closeout.

## Contract

- Read the routed card, current code, repository contracts, and existing proof
  surface. The card's goal, acceptance oracle, relations, and status outrank
  remembered thread state.
- Name the observable outcome and falsifier before editing. No executable
  oracle means write the small one or route to `/shape`; no oracle means no
  delivery.
- Reuse the repository's existing seam. If the target is too tangled to change
  safely, make the smallest behavior-preserving pre-factor as a separate
  reviewable unit.
- Identify the live verification driver that can prove the change to a future
  reviewer. If the outcome needs live proof and no driver exists, establish
  that driver before the feature.

## Compose only what the work needs

| Signal | Route |
|---|---|
| Goal, acceptance, or tradeoff is unresolved | `/shape` |
| External facts would change the design | `/research` |
| Product identity or long-lived direction is unsettled | `/vision` |
| Running behavior needs proof | `/qa` |
| Non-trivial diff needs fresh-context judgment | `/code-review` |
| The repository gate is absent, weak, or red | `/ci` |
| Independent heavy lanes materially shorten the critical path | `/sprites` |
| Delivery exposed a reusable repo-technical lesson | `/compound` after proof |

Do not invoke a specialist as ceremony. Invoke it when its oracle is needed.

## Execute the contract

1. Make the cheapest credible check fail on the missing behavior: a test,
   replay, benchmark, browser path, consumer build, or acceptance assertion.
2. Implement the smallest coherent change that makes it pass. Delete obsolete
   paths and migrate callers cleanly; no compatibility shadow unless the card
   requires one.
3. Exercise the live driver after each meaningful milestone. A narrow unit
   check cannot substitute for the user or operator path named by the card.
4. When implementation reveals an off-plan edge, choose the conservative
   option and record the changed contract or risk coordinate in the shape/card.
   If it invalidates the outcome or oracle, stop and re-shape rather than
   rationalizing drift.
5. Once it works, refactor at three altitudes: simplify the diff, improve or
   remove the seam it exposed, and card only larger product moves that do not
   belong in this delivery.

For disputed proof loops, load
`primitives/shared/references/verification-system-first.md`. For public API,
CLI, UI, performance, compatibility, migration, or operator-workflow changes,
load `primitives/shared/references/works-critique.md` before pre-ship review.

## Prove and land

- Run `/qa` against the live shape and retain reviewable evidence where the
  repository keeps receipts.
- Run `/code-review` with the diff and oracle, not the author's reasoning
  trail. Resolve every blocking finding, then re-prove affected behavior.
- Run the repository gate. Strengthen it only when the likely regression is
  in scope and the existing gate would miss it.
- Commit by concern using the repository's convention and push when the
  workflow requires it. Default stop is merge-ready; merge/deploy only when
  the operator asked for shipped work.
- Reconcile the routed card with exact proof links or commands. Chat, a green
  aggregate, or an unlinked screenshot is not completion evidence.

## Completion Gate

Apply the Shared Operating Spine (`Prove`; `Durable State and Closeout`). Add:

- deviation ledger, or `none`;
- live path exercised and retained evidence;
- review and gate dispositions;
- residual risk; and
- `/compound` offer when the lesson is reusable.

## Gotchas

- **Stale card:** if the outcome already shipped, reconcile the card instead
  of delivering it twice.
- **Spec drift:** re-shape when the oracle changed; do not call drift a minor
  deviation.
- **Self-review:** fresh critics get the artifact and oracle only (Shared
  Operating Spine: `Prove`).
- **Lane confetti:** preserve outcome-shaped ownership. Parallelize independent
  boundaries, not tiny pre-shredded tasks.
