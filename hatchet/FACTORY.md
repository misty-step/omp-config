# Hatchet factory loop

Naive-polling personal factory loop, built on the live canary. See
`FACTORY_LOOP_BRIEF.md` for the original brief this implements.

```
poll Powder for ready-for-dev work
  -> admit one card whose run is not already in flight and has no open PR
  -> durable stages via the existing Hatchet workflow + OMP recipes
  -> open a pull request after `implement`, post review/fix findings to it
  -> land on merged, awaiting_operator_approval, review_blocked, or
     verification_failed
```

## What exists now

`src/reconciler.ts` (`scripts/reconcile`, `npm run reconcile`) polls Powder on
`HATCHET_RECONCILE_INTERVAL_MS` (default 60s, minimum 5s) or once via
`--once`. `powder.mode` selects the intake strategy:

- **`single`** (default) — reads exactly the configured `cardId` from Powder;
  triggers when its status equals `powder.readyStatus` and the card is not
  already live.
- **`ready-queue`** — lists cards via `GET /api/v1/cards?status=<readyStatus>`
  (`src/powder-client.ts#createPowderReadyQueueReader`), narrows to
  `powder.repositoryAllowlist` when set, and walks the eligible cards in
  response order (`src/reconciler.ts#eligibleReadyCards`, a pure function —
  see `tests/reconciler.test.ts`). The trigger call is the same
  `triggerConfiguredWorkflow` used everywhere else, now accepting an optional
  `{ cardId, repository, card }` override (`src/trigger-service.ts`) so
  ready-queue selection does not fork the admission path.

Both modes now share the same open-run and open-PR check
(`src/reconciler.ts#inspectLiveness`), run before every trigger attempt:

- It asks the engine for a run already in flight on that card
  (`src/run-liveness.ts#findInFlightRun`).
- It asks GitHub for an already-open pull request on the card's branch
  (`src/github.ts#findOpenPullRequestForCard`) — a card whose work already
  sits in an open PR is waiting on a human, not on the factory, and without
  this check the reconciler would re-run it every tick forever.
- **`single`** mode skips the tick when either check is positive.
- **`ready-queue`** mode walks candidates in order: a card parked on an open
  PR is skipped over (so one unreviewed PR can't starve the rest of the
  queue); a card with a genuinely in-flight run, or one whose liveness lookup
  fails, consumes the tick rather than letting a later card jump ahead. At
  most one new run is triggered per reconcile tick either way.

Both modes also share every other safety property:

- One run per card at a time. The engine's live run status decides whether a
  card is busy, so a terminal run — including a failed one — releases it.
  Hatchet's own `idempotency` config would enforce this at the engine, but the
  deployed `hatchet-lite v0.94.10` accepts and ignores that field (measured:
  both `ttl` and `status` strategies produced two run ids for one key), so a
  short dispatch lock covers the window until a new run is queryable.
- Every run opens (or reuses) a pull request itself, right after `implement`
  completes, and posts review/fix findings to it as they happen
  (`src/pr-workflow.ts`, lines ~166–181). A stage never pushes or runs `gh`.
  The run lands on one of four terminal states — `merged`,
  `awaiting_operator_approval`, `review_blocked`, `verification_failed`
  (`src/contracts.ts#terminalStateSchema`). A packet is only allowed to claim
  `merged` when `pr.autoMerge` is `true` and GitHub reports a green check
  status for the exact final commit (`src/contracts.ts#evidencePacketSchema`,
  `src/pr-workflow.ts` merge decision). `autoMerge` defaults `false`
  (`prSettingsSchema`) and no operator config deployed today sets it to
  `true`, so in practice every run still ends on operator approval, a
  blocked review, or a failed verification — but the loop itself no longer
  guarantees that; it is a config choice, not a hard-coded terminal.
- The `adversarial_review` -> `remediate` loop already reads CI for the
  fixer: `src/pr-workflow.ts#fixerContext` pulls the pull request's check
  conclusion for the current commit into the remediation task as an
  informational note (best-effort — an unreadable or stale status degrades
  to a note rather than failing the run). This is a one-shot read per fix
  round, not a wait/poll loop: nothing blocks on CI turning green before
  `live_verify` runs, and the merge decision at the end takes its own
  separate, authoritative read of the same checks.
- The webhook path (`src/powder-webhook.ts`) is untouched and still only
  matches events against the single configured `cardId`; it is not involved
  in ready-queue polling. It is also not currently usable at all — see
  "Known-broken: the webhook daemon" below.

## What is still manual / out of scope

- **Per-repository workspace checkout.** `cwd` is still one shared template
  value from the operator config (or the single-card config's `cwd`), not
  derived per selected repository. A ready-queue deployment across multiple
  repositories needs an explicit checkout/workspace-provisioning step before
  this scales past a single working tree; that step is out of scope for this
  slice and must be added deliberately, not inferred.
- **Turning on `autoMerge` is a deliberate config edit**, not a loop
  behavior: nothing in the reconciler or trigger path decides when merging is
  safe beyond the green-check-on-final-commit guarantee `evidencePacketSchema`
  enforces once `pr.autoMerge` is set to `true` for an operator config.

## Known-broken: the webhook daemon

The factory currently runs three launchd daemons: `reconcile`, `worker`, and
`webhook` (`launchd/*.plist.in`, installed via `scripts/install-launchd`).
The webhook daemon has never processed a real Powder event, and it cannot
start fresh under the operator config it is currently deployed against.

`scripts/webhook` (`src/webhook-server.ts`) calls
`createPowderCardReader(operatorConfig)` at startup. That function throws
unless the config has a `cardId` (`src/powder-client.ts`: "operator config
cardId is required for single-card mode"). The deployed webhook config,
`local/operator-wildcard.json`, is a `"mode": "ready-queue"` config and has
no `cardId` field. Launching the webhook process fresh against that file —
on crash, `launchctl kickstart`, a `scripts/install-launchd webhook`
reinstall, or a reboot — fails immediately with that error. The webhook
instance that is alive right now only survived because it was started before
`local/operator-wildcard.json` was switched over to ready-queue mode; nothing
under `local/` shows any evidence of it ever having triggered a run from a
real Powder event.

This is recorded as a known-broken state, not intended behavior. No fix or
timeline is tracked here.

Bitterblossom stays backburned; this loop does not touch it.
