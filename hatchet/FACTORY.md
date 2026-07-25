# Hatchet factory loop

Naive-polling personal factory loop, built on the live canary. See
`FACTORY_LOOP_BRIEF.md` for the original brief this implements.

```
poll Powder for ready-for-dev work
  -> admit one card
  -> durable stages via the existing Hatchet workflow + OMP recipes
  -> stop at human approval (no auto-merge)
```

## What exists now (P0 — implemented)

`src/reconciler.ts` (`scripts/reconcile`, `npm run reconcile`) polls Powder on
`HATCHET_RECONCILE_INTERVAL_MS` (default 60s, minimum 5s) or once via
`--once`. `powder.mode` selects the intake strategy:

- **`single`** (default) — unchanged from the original canary. Reads exactly
  the configured `cardId` from Powder; triggers when its status equals
  `powder.readyStatus`.
- **`ready-queue`** — lists cards via `GET /api/v1/cards?status=<readyStatus>`
  (`src/powder-client.ts#createPowderReadyQueueReader`), optionally narrows to
  `powder.repositoryAllowlist`, and selects the first eligible card in
  response order (`src/reconciler.ts#selectReadyCard`, a pure function — see
  `tests/reconciler.test.ts`). At most one trigger attempt happens per
  reconcile tick, serial-factory style; the trigger call is the same
  `triggerConfiguredWorkflow` used everywhere else, now accepting an optional
  `{ cardId, repository }` override (`src/trigger-service.ts`) so ready-queue
  selection does not fork the admission/idempotency path.

Both modes share every existing safety property unchanged:

- Idempotency stays `cardId:headSha` (or an explicit key), still serialized
  through `withIdempotentTrigger` before HEAD is read.
- No new open-run detection: a ready card that already has a run in flight is
  not skipped by inspecting run state. Reconciliation instead relies on the
  existing idempotency dedupe — the second selection of the same
  `cardId:headSha` inside a tick, or across ticks, resolves to the stored
  mapping (`duplicate: true`) rather than starting a second run. Because the
  reconciler now also stops after one trigger attempt per tick, a
  first-in-queue card that is already a duplicate uses that tick without
  giving a fresh card a chance to run in the same pass; the next tick tries
  again from the top of the (possibly reordered) list.
- No merge, no deploy: the workflow terminal is unchanged — always
  `mergePerformed: false`, `operatorApprovalRequired: true`
  (`src/contracts.ts#evidencePacketSchema`).
- The webhook path (`src/powder-webhook.ts`) is untouched and still only
  supports the single configured card; it is not required for ready-queue
  polling to work.

## What is still human-gated (P1+ — not implemented here)

- **Open PR stage.** Nothing in this loop opens a pull request yet; that is
  a future recipe/stage, gated on an explicit operator decision about what
  "implement" should push and where.
- **CI watch / review feedback loop.** No stage currently polls CI status or
  feeds CI failures back into `remediate`.
- **Per-repository workspace checkout.** `cwd` is still one shared template
  value from the operator config (or the single-card config's `cwd`), not
  derived per selected repository. A ready-queue deployment across multiple
  repositories needs an explicit checkout/workspace-provisioning step before
  this scales past a single working tree; that step is out of scope for this
  slice and must be added deliberately, not inferred.
- **Merge/deploy.** `mergePerformed` stays hard-`false`. Turning any part of
  this loop into an auto-merge or auto-deploy pipeline requires an explicit
  operator policy change to the contract in `src/contracts.ts`, not a
  reconciler config flag.
- **Open-run detection.** Skipping a ready card that already has an
  active/open run mapping (instead of relying on idempotency dedupe after
  the fact) would need a state-store query keyed by `cardId` prefix; not
  built here, per brief step 3 ("skip if detectable; otherwise rely on
  idempotency duplicate detection").

Bitterblossom stays backburned; this loop does not touch it.
