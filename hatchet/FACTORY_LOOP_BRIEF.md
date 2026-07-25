# Hatchet factory loop — implementation brief

## Goal

Turn the live Hatchet canary into the **core personal factory loop** using **naive polling** first:

```
poll Powder for ready-for-dev work
  → admit one card
  → durable stages via existing Hatchet workflow + OMP recipes
  → stop at human approval (no auto-merge yet)
```

Do **not** depend on sophisticated webhooks or upstream oh-my-pi PRs.
Dispatched OMP agents/recipes do Powder/GitHub/CI work themselves.

## Live baseline (already exists)

- Engine + UI: Hatchet Lite on `127.0.0.1:8888`, worker API `7077`
- Workflow: `omp-pr-canary-v1`
- Stages: implement → adversarial_review → (remediate↔review)* → live_verify → terminal_evidence
- Terminal: always `mergePerformed:false`, `operatorApprovalRequired:true`
- Reconciler: `src/reconciler.ts` polls **one** configured card id from `local/operator.json`
- Recipes under `recipes/`
- Bitterblossom stays backburned

## Problem

Current reconciler/operator config is **single-card canary**, not a multi-card factory intake.
Need generalized polling intake over ready work without blowing the safety contract.

## Target slice (implement now)

### P0 — Multi-card ready poller (factory intake)

1. Extend operator config (version bump if needed) to support either:
   - `powder.cardId` (legacy single), or
   - `powder.query` / list mode: poll cards in `ready` (or configured status) for allowed repos.
2. Prefer smallest change:
   - Add `powder.mode: "single" | "ready-queue"`
   - `ready-queue` lists ready cards from Powder API (reuse powder-client patterns)
   - Filter by optional `repositoryAllowlist`
   - Trigger at most one new run per reconcile tick (serial factory; slots already 1)
   - Idempotency remains `cardId:headSha`
3. Skip cards that already have an open/active run mapping if detectable; otherwise rely on idempotency duplicate detection.
4. Keep webhook path intact but not required.
5. Document operator.json example for ready-queue mode.
6. Tests for pure selection/trigger logic with mocked Powder client.

### P1 — Document next stages (code comments or short FACTORY.md) without implementing merge/deploy yet

Next after this slice:
- open PR stage recipe
- CI watch / review feedback loop
- merge/deploy only after explicit operator policy change (`mergePerformed` currently hard-false)

## Constraints

- No upstream oh-my-pi PR work
- No Bitterblossom revival
- No weakening idempotency, head checks, or approval terminal
- No auto-merge
- Prefer extending existing files over new framework
- Skip unrelated refactors
- Run focused vitest for touched tests; no full monorepo gates outside hatchet package

## Acceptance

1. With ready-queue config, reconciler `--once` can select a ready card and attempt trigger (mockable test proves selection ordering/filters).
2. Single-card mode still works.
3. README or `FACTORY.md` states the polling factory loop and what is still human-gated.
4. Exact commands run and results reported.
