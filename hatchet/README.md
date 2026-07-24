# Hatchet canary (local durable orchestration)

Local, auth-disabled Hatchet engine that runs one durable workflow
(`omp-pr-canary-v1`) as the coarse durable-stage layer above the opaque OMP
runner. Hatchet owns stage sequencing and retry/cancel semantics; Powder
remains the approval authority; the workflow never merges and always ends in
a human-approval-required terminal state.

## Contract

- Stages: `implement -> adversarial_review -> (remediate -> adversarial_review)* -> live_verify -> terminal_evidence`.
- Input carries five strict, distinct paths under `recipePaths`; each stage selects
  only its own compiled bundle. Remediation is capped at 2 rounds; a third
  block ends the run in `review_blocked`.
- Terminal states are `awaiting_operator_approval`, `review_blocked`, or
  `verification_failed`. Every evidence packet sets `mergePerformed: false`
  and `operatorApprovalRequired: true`.
- Idempotency is keyed by `cardId:headSha` or an explicit key. Admission is
  serialized before mutable HEAD validation. Concurrent and completed-run
  replays resolve the stored v2 input/run before reading HEAD. Lock owner
  metadata recovers dead-process locks, never steals a live-owner lock, and
  bounds active-lock waits instead of hanging an ingress request. Legacy
  single-recipe checkpoints require a new key.
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
- `scripts/start` | `stop` | `status` | `cancel-run` | `worker` | `trigger` |
  `webhook` | `reconcile` — operator entry points. `stop` runs
  `docker compose down` **without** `--volumes`: the named Postgres volume
  (`omp-hatchet-postgres-v09410`) and `local/hatchet-config` survive a
  stop/start cycle, so workflow history is queryable again after restart.
- `src/` — TypeScript SDK client, durable workflow and stage orchestrator,
  Hatchet process runner, the direct shared-runner adapter, idempotency/state,
  webhook/reconciler, and operator CLIs.
- `scripts/recipe-runner` — Bun entry point for the adapter. The stage runner
  uses it by default; `OMP_RECIPE_RUNNER` remains an explicit test/operator
  override.
- Root `hatchet-*.recipe.json` files — canonical `omp.recipe.v1` sources.
  They select existing `global/skills` paths; they do not copy or catalog
  skills. `hatchet/recipes/*.md` holds the stage-specific instructions.
- `local/recipes/<stage>/` — gitignored compiled bundles used by the worker.
- `fixtures/` + `tests/` — deterministic process fixtures plus focused
  contract, workflow, adapter, environment, cancellation, and replay tests.
- `local/` — gitignored Hatchet configuration, execution/idempotency
  checkpoints, compiled bundles, and operator configs. Never commit it.

## Running it

```sh
scripts/start                         # start the engine; preserve volumes/history
scripts/worker                        # foreground managed worker; adapter is the default
npm run trigger -- --config local/operator.json
npm run status -- --run-id <id>
npm run cancel -- --run-id <id>
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
for a card that has already left `ready` is acknowledged without a run. Powder
events do not carry a repository HEAD, so webhook and reconciliation both let
the shared trigger snapshot current HEAD and derive the same `cardId:headSha`
key. Duplicate delivery returns the stored run; it never reruns completed work.

Runtime configuration stays under ignored `local/`:

- `local/operator-wildcard.json` adds `powder.baseUrl`,
  `powder.apiTokenFile`, and `powder.readyStatus`.
- The base URL is the Mint proxy URL for the deployed Powder origin.
- The token file contains only the approved Mint placeholder, never credential
  bytes. The operator config, token file, and
  `local/powder-webhook-secret` must be mode `0600`.

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
npx vitest run tests/powder-webhook.test.ts tests/idempotency.test.ts
scripts/reconcile --once
scripts/probe-powder-webhook.mjs http://127.0.0.1:8099/webhook/powder
```
