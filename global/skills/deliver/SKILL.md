---
disable-model-invocation: true
name: deliver
description: Deliver one accepted repository change through live proof, independent review, and durable closeout.
argument-hint: "[ticket|description]"
---

# /deliver

Deliver one accepted outcome. The live authority outranks remembered context.

## Contract

1. **Ground.** Read the work card, repository contracts, relevant code, existing proof, and worktree state. Do not delete, revert, overwrite, or restage unrecognized files, hunks, or commits. Complete when the authority, scope, and current state are explicit.
2. **Bound.** Name the observable outcome and cheapest credible falsifier before editing. If no executable oracle exists, stop and reshape the authority or ask the operator. Complete when the falsifier can prove the requested behavior remains wrong.
3. **Prepare proof.** Name the live driver that exercises the changed surface. Build the driver first when live proof is required and none exists.
4. **Change.** Modify the highest-leverage owning layer through an existing seam. Keep one coherent change. Complete when every caller uses the new path.
5. **Erase.** Delete only replaced implementation, stale comments, obsolete configuration, dead tests, and superseded rules. Never delete the delivered change or its proof. Keep compatibility only when the authority requires it.
6. **Exercise.** Run the live driver after meaningful milestones and after review fixes. A narrow unit check cannot replace the named live path.

## OMP routes

The chief owns intent, acceptance, integration, and final judgment. A `builder` executes one accepted implementation and never redispatches.

| Need | Route |
|---|---|
| Goal, acceptance, or tradeoff remains unresolved | `designer` with `groom`; chief or operator accepts |
| External facts can change the design | read-only `researcher` with `research` |
| Product identity or durable direction remains unsettled | `designer` with `groom` (vision); chief or operator accepts |
| Running behavior needs proof | `verifier` with `verify-live` |
| A substantive diff needs independent judgment | non-mutating `verifier` with `code-review` |
| The repository gate is absent, weak, or red | `ci` |
| Independent remote lanes shorten the critical path | `sprites` |

Route only when the named oracle is required. Load `global/references/works-critique.md` for public surfaces, compatibility, migrations, performance, or operator workflows.

## Prove and close

1. Give the finished artifact, diff, and oracle to a fresh verifier. Do not give the author's reasoning trail.
2. Resolve every blocking finding. Re-run the affected live driver.
3. Run the repository gate after live behavior works. Never weaken or bypass a gate, threshold, test, or invariant.
4. Record the authority, changed paths, live entrypoint, exact commands, observed results, review disposition, gate disposition, deviations, and residual risk. A deviation ledger may say `none` only when it is empty.
5. If delivery produced one reusable repo-technical lesson, write or update one file under `docs/solutions/` using `global/references/learnings.md`. Skip near-duplicates.
6. Reconcile the governing GitHub Issue when one exists. Stop at merge-ready unless the operator explicitly requests merge or deploy.

Chat alone is not completion evidence. A green aggregate without the exact command and observed result is not proof. Apply `global/references/verification-system-first.md` when proof design is disputed. Complete when a future reviewer can reproduce the live result from the durable record.
