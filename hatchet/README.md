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
  replays resolve the stored v2 input/run before reading HEAD; legacy
  single-recipe checkpoints require a new key.
- `src/recipe-runner-adapter.ts` accepts the Hatchet runner flags and invokes
  the shared `startRecipeTask` API directly under Bun. It suppresses progress
  stdout, requires exactly one strict `runnerTerminalSchema` object in final
  assistant text, and emits only that JSON object.
- The opaque runner receives a positive environment allowlist: locale/TLS
  process keys plus the explicit `OMP_RECIPE_*` launch selectors. Hatchet
  tokens and unrelated worker environment never cross the adapter boundary.
- Cancelling a run kills the runner's whole process group. The adapter maps
  process signals to the shared runner abort/stop path, which reaps OMP and
  removes its fresh runtime/config/session root.

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
