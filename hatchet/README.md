# Hatchet canary (local durable orchestration)

Local, auth-disabled Hatchet engine that runs one durable workflow
(`omp-pr-canary-v1`) as the coarse durable-stage layer above the opaque OMP
runner. Hatchet owns stage sequencing and retry/cancel semantics. Every run
opens a pull request right after `implement` completes and ends in one of
four terminal states: `merged`, `awaiting_operator_approval`,
`review_blocked`, or `verification_failed`. Merging is an explicit operator
opt-in (`pr.autoMerge` plus a GitHub-reported green check status for the
exact final commit) that defaults off; no operator config deployed today
turns it on, so in practice every run still lands on human approval, a
blocked review, or a failed verification. Powder remains the day-to-day
approval authority.

## Contract

- Stages: `implement -> adversarial_review -> (remediate -> adversarial_review)* -> live_verify -> terminal_evidence`.
- Input carries five strict, distinct paths under `recipePaths`; each stage selects
  only its own compiled bundle. Remediation is capped at 2 rounds; a third
  block ends the run in `review_blocked`.
- The workflow publishes the branch and opens (or reuses) the pull request for
  a card itself, right after `implement` — a stage never pushes or runs `gh`
  (`src/pr-workflow.ts`). Review and fix-round findings are posted to that
  pull request as they happen. Terminal states are `merged`,
  `awaiting_operator_approval`, `review_blocked`, or `verification_failed`
  (`src/contracts.ts` `terminalStateSchema`). A packet is only allowed to
  claim `merged` when `pr.autoMerge` is `true` and GitHub reports a green
  check status for that exact commit; the schema (`evidencePacketSchema`)
  refuses any packet that claims a merge without both.
- Admission is one run per card at a time. The authority is the engine's live
  run status, so a terminal run — including a failed one — releases its card
  and the next trigger is admitted. A short local lock covers only the gap
  between dispatch and the run becoming visible to that query.
- `src/recipe-runner-adapter.ts` accepts the Hatchet runner flags and invokes
  the shared `startRecipeTask` API directly under Bun. It suppresses progress
  stdout, requires exactly one strict `runnerTerminalSchema` object in final
  assistant text, and emits only that JSON object.
- The opaque runner receives a positive environment allowlist: locale/TLS
  process keys plus the explicit `OMP_RECIPE_*` launch selectors. Hatchet
  tokens and unrelated worker environment never cross the adapter boundary.
- Cancelling a run kills the runner's whole process group; the adapter maps
  process signals to the shared runner's own abort/stop path, which reaps OMP
  and removes its fresh runtime/config/session root in the common case. That
  in-process cleanup is not the durable guarantee: an adapter subprocess can
  die (OS-delivered SIGTERM, SIGKILL, crash) before its own async cleanup
  finishes. `invokeRunner` (`src/runner.ts`) additionally pre-creates a
  private 0600 receipt file per launch, hands the child only its path via
  `OMP_RECIPE_RUNTIME_RECEIPT`, and the adapter's `onPrepared` hook
  (`global/lib/recipe-task-runner.ts`) writes the runtime root into it
  immediately after prepare — well before any RpcClient/model work starts.
  After the child is reaped, `invokeRunner` always re-reads that receipt,
  validates the path is exactly `<realpath(tmpdir())>/omp-recipe-task-<uuid>`,
  and removes it (then the receipt itself) regardless of how the child exited
  or whether its own cleanup already ran — idempotent, and independent of the
  adapter completing gracefully.

## Layout

- `compose.yaml` — `postgres:15.6` + pinned
  `ghcr.io/hatchet-dev/hatchet/hatchet-lite-dev:v0.94.10`, `SERVER_DEFAULT_ENGINE_VERSION: V1`,
  official `/ready` healthcheck, ports bound to `127.0.0.1` only.
- `scripts/quiet-entrypoint.sh` — generates local-only 0600 encryption keys,
  auth-cookie secret, and (since this build runs `hatchet-admin authdisabled`)
  a worker token, all under `local/hatchet-config/` (bind-mounted, gitignored).
  Suppresses upstream startup noise so container logs never carry secrets.
- `scripts/start` | `stop` | `status` | `cancel-run` | `replay-run` | `worker`
  | `trigger` | `webhook` | `reconcile` — operator entry points. `stop` runs
  `docker compose down` **without** `--volumes`: the named Postgres volume
  (`omp-hatchet-postgres-v09410`) and `local/hatchet-config` survive a
  stop/start cycle, so workflow history is queryable again after restart.
- `src/` — TypeScript SDK client, durable workflow and stage orchestrator,
  Hatchet process runner, the direct shared-runner adapter, the PR workflow
  and GitHub client, run admission and durable execution state, webhook/
  reconciler, and operator CLIs.
- `scripts/recipe-runner` — Bun entry point for the adapter. The stage runner
  uses it by default; `OMP_RECIPE_RUNNER` remains an explicit test/operator
  override.
- Root `hatchet-*.recipe.json` files — canonical `omp.recipe.v1` sources.
  They select existing `global/skills` paths; they do not copy or catalog
  skills. `hatchet/recipes/*.md` holds the stage-specific instructions.
- `local/recipes/<stage>/` — gitignored compiled bundles used by the worker.
- `fixtures/` + `tests/` — deterministic process fixtures plus focused
  contract, workflow, adapter, environment, cancellation, and replay tests.
- `local/` — gitignored Hatchet configuration, execution checkpoints,
  compiled bundles, and operator configs. Never commit it.

## Running it

```sh
scripts/start                         # start the engine; preserve volumes/history
scripts/worker                        # foreground managed worker; adapter is the default
npm run trigger -- --config local/operator.json
npm run status -- --run-id <id>
npm run cancel -- --run-id <id>
npm run replay -- --run-id <id>       # resume a run from its last checkpoint (src/cli/replay.ts)
scripts/stop                          # stop engine; preserve volumes/history
```

Run the worker under a process supervisor or terminal that owns its lifecycle;
do not daemonize it by hand. `npm run build && npm test` runs the focused
Hatchet typecheck and test suite.

## Powder moved-to-ready ingress

Powder signs the exact raw JSON body in `X-Signature-256` as
`sha256=<hex HMAC-SHA256>`. The accepted envelope is
`powder.card_event.v1` with `event_type: "moved-to-ready"`, a stable
`event_id`, the ready card snapshot under `card`, and the status transition
under `change`. Powder retries one delivery with the same event id up to six
times. The receiver acknowledges unrelated cards without triggering so a
global moved-to-ready subscription does not retry them.

The configured card is re-read from Powder before admission. A delayed event
for a card that has already left `ready` is acknowledged without a run.
Powder events do not carry a repository HEAD, so webhook and reconciliation
both let the shared trigger snapshot current HEAD; admission is then one run
per card at a time, so a duplicate delivery returns the run already in flight
rather than starting a second one.

**This webhook path is currently non-functional in the deployed environment
— see "Known-broken: the webhook daemon" below.**

Runtime configuration stays under ignored `local/`:

- `local/operator-wildcard.json` adds `powder.baseUrl`,
  `powder.apiTokenFile`, and `powder.readyStatus`.
- The base URL is the Mint proxy URL for the deployed Powder origin.
- The token file contains only the approved Mint placeholder, never credential
  bytes. The operator config, token file, and
  `local/powder-webhook-secret` must be mode `0600`.

## Factory intake: single-card vs ready-queue

`scripts/reconcile` (`src/reconciler.ts`) supports two `powder.mode` values.
See `FACTORY.md` for the end-to-end polling factory loop and what stays
human-gated.

- `"single"` (default, omit `powder.mode` for the existing behavior) polls
  exactly the one card at `cardId`/`repository`. `local/operator.json` is a
  single-card example.
- `"ready-queue"` lists cards via `GET /api/v1/cards?status=<readyStatus>`
  instead of reading one fixed id. `cardId`/`repository` become optional at
  the top level (they still supply the shared `cwd`/`task`/`recipePaths`
  template and an optional fallback `repository` for cards that omit `repo`).
  `local/operator-wildcard.json` is the deployed ready-queue config.

Both modes now check the same liveness signal before triggering
(`src/reconciler.ts#inspectLiveness`): the engine for a run already in flight
on that card (`src/run-liveness.ts#findInFlightRun`), then GitHub for an
already-open pull request on the card's branch
(`src/github.ts#findOpenPullRequestForCard`). Single mode skips the tick when
either is true. Ready-queue mode walks its eligible cards
(`src/reconciler.ts#eligibleReadyCards`) in listed order: a card parked on an
open pull request is skipped over so it can't starve the rest of the queue; a
card with a genuinely in-flight run, or one whose liveness lookup fails,
consumes the tick instead of letting a later card jump ahead. At most one new
run is triggered per reconcile tick either way.

```json
{
  "version": 1,
  "repository": "misty-step/fallback-repo",
  "recipePaths": {
    "implement": "/Users/phaedrus/Development/omp-config-buzz-omp/hatchet/local/recipes/implement",
    "adversarial_review": "/Users/phaedrus/Development/omp-config-buzz-omp/hatchet/local/recipes/adversarial-review",
    "remediate": "/Users/phaedrus/Development/omp-config-buzz-omp/hatchet/local/recipes/remediate",
    "live_verify": "/Users/phaedrus/Development/omp-config-buzz-omp/hatchet/local/recipes/live-verify",
    "terminal_evidence": "/Users/phaedrus/Development/omp-config-buzz-omp/hatchet/local/recipes/terminal-evidence"
  },
  "cwd": "/Users/phaedrus/Development/omp-config-buzz-omp/hatchet/local/factory-workspace",
  "task": "Implement the claimed card's acceptance criteria.",
  "powder": {
    "baseUrl": "http://mint.tail5f5eb4.ts.net:4949/proxy/https/sanctum.tail5f5eb4.ts.net:10001",
    "apiTokenFile": "/Users/phaedrus/Development/omp-config-buzz-omp/hatchet/local/powder-api-token",
    "readyStatus": "ready",
    "mode": "ready-queue",
    "repositoryAllowlist": ["misty-step/omp-config", "misty-step/fallback-repo"]
  }
}
```

`powder subscription-*` is database-only. For a deployed Powder instance,
`scripts/create-powder-subscription.mjs` uses the configured Mint proxy, creates
exactly the `moved-to-ready` subscription, and writes the one-shot signing
secret directly to `local/powder-webhook-secret` with `0600` mode. It prints
only the non-secret subscription record:

```sh
scripts/create-powder-subscription.mjs \
  https://<tailnet-host>:<https-port>/webhook/powder
```

Expose loopback port `8099` with Tailscale Serve on a dedicated HTTPS port.
Never use `tailscale funnel`:

```sh
tailscale serve --bg --yes --https=<https-port> http://127.0.0.1:8099
curl --fail https://<tailnet-host>:<https-port>/health
```

## Persistent LaunchAgents

Tracked templates under `launchd/` install three user agents with explicit
working directory, PATH, ignored config paths, and log paths:

- `com.misty-step.omp-hatchet-worker`: `KeepAlive` worker.
- `com.misty-step.omp-hatchet-webhook`: `KeepAlive` loopback webhook.
- `com.misty-step.omp-hatchet-reconcile`: `--once` every 300 seconds.

**Known-broken: the webhook daemon.** All three agents are installed, but the
webhook one is not usable today. `scripts/webhook` (`src/webhook-server.ts`)
requires a `cardId` in its operator config (it calls
`createPowderCardReader`, which throws without one —
`src/powder-client.ts`). The deployed config it points at,
`local/operator-wildcard.json`, is a ready-queue config with no `cardId`. A
fresh start of the webhook process under that config fails immediately;
whatever webhook instance is currently alive only survived because it was
started before that config was switched to ready-queue mode, and there is no
record anywhere under `local/` of it ever having triggered a run from a real
Powder event. This is a known-broken state, not intended behavior — see
`FACTORY.md` for detail; no fix or timeline is tracked here.

Render and validate without loading anything:

```sh
scripts/install-launchd --render-only
```

Load auxiliary services independently. For worker handoff, first prove the
Hatchet engine is healthy, stop the prior supervisor-owned worker, then load
the launchd worker. Never overlap two workers:

```sh
scripts/install-launchd webhook reconcile
# stop the prior supervised worker here
scripts/install-launchd worker
launchctl print "gui/$(id -u)/com.misty-step.omp-hatchet-worker"
```

Focused ingress checks:

```sh
npm run build
npx vitest run tests/powder-webhook.test.ts tests/reconciler.test.ts
scripts/reconcile --once
scripts/probe-powder-webhook.mjs http://127.0.0.1:8099/webhook/powder
```
