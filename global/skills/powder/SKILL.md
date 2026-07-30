---
disable-model-invocation: true
name: powder
description: |
  Use when an agent must inspect, claim, update, request input for, or
  complete work cards in a Powder instance. Powder is a self-hostable,
  agent-first work board with durable cards, run sessions, activity, audit
  events, relations, optional proof, and human-in-loop states.
argument-hint: "[list-ready|claim|update-status|update-relations|request-input|complete-card]"
---

# Powder

Powder is a self-hostable work tool. It exposes one core through API, CLI, MCP,
and this skill. Treat cards as context objects with acceptance oracles, not
status rows. Store real card data in a deployed instance database, not in the
product repository. Read `VISION.md` before you change Powder's product scope,
card/run model, runner boundary, or self-hosting assumptions.

For local MCP use, set `POWDER_DB_PATH` to the instance SQLite database. For a
deployed instance, set both `POWDER_API_BASE_URL` and `POWDER_API_KEY`. Choose
exactly one mode: `POWDER_DB_PATH` or the remote pair
`POWDER_API_BASE_URL` plus `POWDER_API_KEY`. MCP refuses to start without one
complete mode. No ephemeral in-memory mode exists because claims and
completions must persist after exit.

By default, `powder-mcp` exposes only the agent persona. Set
`POWDER_MCP_TOOLSETS=admin` or `POWDER_MCP_TOOLSETS=all` before starting the
MCP subprocess to add operator/admin tools to the same server registration.
The server reads this value once at startup for MCP client cache stability.
Restart `powder-mcp` after you change it. Calls to hidden admin tools fail with
an error that names `POWDER_MCP_TOOLSETS`.

## Operating Contract

The MCP server `instructions` field is the source of truth for Powder's agent
operating contract. Clients receive it in the initialize response. Keep this
skill focused on harness setup, environment variables, and reference details.
When the workflow contract changes, update the server instructions first.
Keep the claim gate: cards without acceptance criteria cannot be claimed.

## Papercut intake

Papercuts record agent-reported UX friction as backlog cards. Use
`report_papercut` (MCP) or `powder papercut <body> --agent <label>
[--service <repo>]` (CLI) in both `--db` and remote modes. Keep this tool
small: one call, no claim, no dedup scan, and no fix. The reporting agent is
the audit actor. The server scrubs the body for secrets. The card carries the
`papercut` label. If `service` matches a repository entity, home the card
there. Otherwise, add a `service:<name>` label. Grooms sweep with

`list_cards label:papercut` (MCP) or `powder list-cards --label papercut` (CLI).

## Expected MCP Tools

Default agent persona (21 tools):

- `list_ready`: Return claimable cards from active repositories.
  Order cards so no card appears after another card that it transitively blocks.
  Use topological ordering over `blocks`/`blocked_by` among the returned set.
  Break ties by priority, age, and identifier.
  Optionally filter by `estimate` (`S`/`M`/`L`/`XL`).
  Keep eligibility direct-blocker-only (unchanged).
  Only true members of a `blocks`/`blocked_by` cycle lose topological ordering.
  Emit cycle members as a group in tie-break order at the cycle's own position.
  Name them in an additive `cycle_card_ids` field, computed over the full
  eligible set before `limit` truncation.
  Keep cards downstream of a cycle dependency-ordered after it.
  Use `get_card`'s `transitive_blocked_by`/`blocked_by_cycle` fields to explain
  a *blocked* card's chain past one hop.
- `list_cards`: Enumerate cards with optional status/repo/`estimate`/`label`
  filters.
  Include cards that `list_ready` never surfaces: `backlog`, cards with an
  unresolved `blocked_by` relation, and `done`/`shipped`/`abandoned`.
  Without a `status` filter, hide `done`/`shipped`/`abandoned` cards by default
  in both local `POWDER_DB_PATH` and remote `POWDER_API_BASE_URL` modes.
  Pass `include_terminal: true` to restore the full sweep.
  Use an explicit `status` filter (for example, `status: done`) to return
  matching cards regardless of `include_terminal`.
  Make `total_count` report the full matching count, including terminal cards.
  Do not make a hidden card appear nonexistent.
  Keep the two shortfalls separate in `hint`: "N more non-terminal cards (raise
  limit)" versus "N terminal hidden (include_terminal:true)".
  For a filtered query with no matches, name the active filter and board total,
  for example `0 matches for {status:done, repo:mint}; board has 214 cards`.
- `board_stats`: Return board-shape counts by status and repo, not card
  contents. Call this before `list_cards` when you need only the board shape.
- `create_card`: Create one card with optional acceptance criteria, proof plan,
  relations, parent (decomposing an epic), repository, estimate, and initial
  status. Return a minimal ack. Use `get_card` for full state.
  `related`/`blocks`/`blocked_by` set at creation mirror reciprocally onto each
  named peer that already exists (see `update_relations`). Tolerate a peer id
  that does not exist yet and do not mirror it.
- `list_repositories`: List repository entities with aliases, visibility, tier,
  import provenance, and status counts.
- `manage_claim`: Acquire, renew, heartbeat, release, or transfer a claim.
  Set `action` to `claim`, `renew`, `heartbeat`, `release`, or `transfer`.
  Remote API-key mode records the authenticated integration `principal`
  separately from the required `agent` worker label and returned `run_id`.
  One principal may coordinate multiple workers. Lease ownership follows that
  principal.
  This pre-1.0 MCP break removed the old `claim_card`, `renew_claim`,
  `heartbeat`, `release_claim`, and `transfer_claim` tools.
- `get_card`: Read one card with runs, activities, links, comments, and claim
  state. A parent card also returns bounded child summaries and a deterministic
  `epic_state` rollup packet with status counts, acceptance sums, child
  evidence with provenance, freshness, and parent/child mismatch flags.
  `detail` defaults to `concise`, with newest-first, most recent 20 per
  history section plus totals/hint when truncated. Pass `detail: detailed` for
  full history.
- `get_run`: Read one run with its card, activities, links, comments, and run
  state. `detail` defaults to `concise`, with newest-first, most recent 20 per
  history section plus totals/hint when truncated. Pass `detail: detailed` for
  full history.
- `list_awaiting_input`: List runs paused for human or agent input.
- `list_approvals`: List awaiting-input runs with card title, latest question
  text, run id, and approval-prefixed packet links. This is a review-focused
  view over the same runs that `list_awaiting_input` surfaces.
- `answer_input`: Append an actor-attributed answer and resume the run.
- `update_status`: Set a card to any status in one call and record an audit
  event.
- `check_criterion`: Mark one acceptance criterion checked or unchecked and
  audit actor/time. Return a minimal ack. Use `get_card` for full state.
- `update_relations`: Replace a card's `related`, `blocks`, and `blocked_by`
  relation lists, and/or set the hierarchy edge. `parent` links the card under
  an epic. `clear_parent` unlinks it. A hierarchy-only call leaves relation
  lists untouched. Parent edges never block. Child completion never completes
  the parent. Parent acceptance stays authoritative.
  **Relation writes are reciprocal and atomic**: mirror only ids added or
  removed against the card's prior lists. Mirror them onto each named peer that
  exists in the same transaction as the primary write. `related` is symmetric:
  A related X implies X related A. `blocks`/`blocked_by` mirror each other:
  A blocks X implies X is blocked_by A. Tolerate an id for a nonexistent card
  and do not mirror it. This is unchanged from prior behavior because relation
  targets have never been existence-checked.
  Run `powder relations-doctor --db <path>` (add `--repair` to fix) to find or
  repair graphs asymmetric from before this guarantee or from direct database
  writes that bypassed every face.
- `add_link`: Attach a PR, CI run, artifact, or reference URL to a card.
- `add_comment`: Attach an actor-attributed comment (`author`, `body` -- both
  required). Make it visible immediately via `get_card`/`get_run`. The server
  scrubs `body` for known secret shapes before storage.
- `append_work_log`: Append a high-frequency, fully-attributed work_log entry
  with `(agent, model, reasoning, harness, run_id, body)` while actively
  working a card. Call this often, not only at completion. The server scrubs
  `body` for known secret shapes before storage.
- `report_papercut`: File friction as soon as you feel it. Report too many
  tokens, too many calls, confusing errors, missing capability, or anything
  awkward. Required: `agent`, `body`. Optional: `service`, `model`, `harness`.
  The report creates a backlog card labeled `papercut`. Make one call. Do not
  stop working. Do not fix it yourself. Dedup happens at groom time. Grooms
  can sweep with `list_cards` filtered by `label: papercut`.
- `request_input`: Move the run to `awaiting_input` with the exact question.
- `complete_card`: Mark the card done and optionally attach proof.
- `update_card`: Patch title, body, acceptance, proof_plan, status, priority,
  or labels on an existing card (`PATCH /api/v1/cards/{id}`). Any
  authenticated actor may patch. Audit every patch with actor and field list.
  Recording an operator ruling never requires the admin key.

Admin add-on when `POWDER_MCP_TOOLSETS=admin` or `all` (9 tools):

- `upsert_repository`: Create or update repository settings.
- `merge_repository_alias`: Merge duplicate repo strings into one canonical
  repository and audit re-homed cards.
- `delete_repository`: Delete an unused repository entity.
- `create_event_subscription`: Create a signed webhook subscription.
- `list_event_subscriptions`: List webhook subscriptions without secrets.
- `disable_event_subscription`: Disable a webhook subscription and preserve
  delivery history.
- `list_dead_letters`: List webhook deliveries that exhausted retry attempts.
- `tail_events`: Read durable card events after an optional sequence cursor.
- `list_keys`: List API-key metadata without raw secrets or hashes.

## Instance CLI

`powder` supports remote mode for the full card and claim-lifecycle workflow.
Set `POWDER_API_BASE_URL` and `POWDER_API_KEY`, then omit `--db` for
`list-ready`, `list-cards`, `papercut`, `get-card`, `create-card`, `claim`,
`heartbeat`, `renew-claim`, `transfer-claim`, `release-claim`, `update-status`,
`check-criterion`, `add-link`, `add-comment`, `append-work-log`,
`request-input`, and `complete-card`. These commands operate against the
deployed instance. No separate "remote closeout" wrapper exists. The same
commands work unchanged against `--db`. `--db` always wins when supplied, so a
local smoke cannot accidentally mutate the deployed board.

Run `powder version` before a lane starts. It reports the git commit that built
the installed binary. A stale `~/.cargo/bin/powder` (one that predates a
command's remote-mode support) is then obvious. You will not see a bare
`missing --db` error for a command the checkout already covers.

To close a card against a deployed instance without a local database, run:

```sh
export POWDER_API_BASE_URL=https://powder.internal
export POWDER_API_KEY=sk_powder_...
powder get-card 001
powder add-link 001 --label pr --url https://github.com/misty-step/example/pull/1
powder append-work-log 001 --agent codex --body "narrowed the fix to one function" --model claude-sonnet-5
powder add-comment 001 --author codex --body "shipped, PR linked above"
powder complete-card 001 --proof https://github.com/misty-step/example/pull/1
```

`update-relations`, `get-run`, `list-awaiting-input`, `answer-input`,
`repository-*`, `import-github-issues`, `key-*`, and `subscription-*` remain
`--db`-only. These commands are bulk/admin operations or read paths without
remote-mode demand yet. If you omit `--db`, they fail with a bare
`missing --db`, not the command-specific transport error that remote-capable
commands return.

```sh
powder init-db --db ./data/powder.db --show-secret
powder list-ready --db ./data/powder.db --limit 10
powder repository-list --db ./data/powder.db --include-hidden
powder repository-upsert --db ./data/powder.db --name canary --aliases misty-step/canary --visibility visible --tier active --import-provenance manual
powder repository-merge-alias --db ./data/powder.db --alias misty-step/canary --into canary --actor operator
powder claim 001 --db ./data/powder.db --agent codex
powder heartbeat 001 --db ./data/powder.db --run run-id
powder renew-claim 001 --db ./data/powder.db --run run-id --ttl 3600
powder transfer-claim 001 --db ./data/powder.db --run run-id --to-agent codex --ttl 3600
powder release-claim 001 --db ./data/powder.db --run run-id
powder get-card 001 --db ./data/powder.db
powder update-relations 001 --db ./data/powder.db --related 002 --blocks 003 --blocked-by 000
powder relations-doctor --db ./data/powder.db  # report-only: lists cards whose blocks/blocked_by/related disagree with a peer
powder relations-doctor --db ./data/powder.db --repair --actor operator  # symmetrizes every found issue and audits each fix
powder update-status 001 --db ./data/powder.db --status in_progress
powder request-input run-id --db ./data/powder.db --question "Approve?"
powder list-awaiting-input --db ./data/powder.db
powder answer-input run-id --db ./data/powder.db --actor operator --answer approved
powder get-run run-id --db ./data/powder.db
powder complete-card 001 --db ./data/powder.db
```

## MCP Over HTTP

Set `POWDER_API_BASE_URL` and `POWDER_API_KEY` to run `powder-mcp` against a
live `powder-server` instead of a local SQLite file. Run this minimal local
smoke:

```sh
DB=/tmp/powder-http-smoke/powder.db
mkdir -p "$(dirname "$DB")"
KEY=$(powder init-db --db "$DB" --show-secret | awk -F '\t' '/bootstrap-key/ {print $4}')
powder create-card --db "$DB" --id smoke-proof --title "HTTP smoke" --acceptance "lifecycle works" --status ready
POWDER_DB_PATH="$DB" POWDER_AUTH_MODE=api-key POWDER_BIND_ADDR=127.0.0.1:4017 powder-server

POWDER_API_BASE_URL=http://127.0.0.1:4017 POWDER_API_KEY="$KEY" powder-mcp
```

For Harness Kit `factory-mcps`, use this remote entry shape:
`required_env_any: [[POWDER_API_BASE_URL, POWDER_API_KEY], [POWDER_DB_PATH]]`.
The factory remote variant must populate `POWDER_API_BASE_URL` and
`POWDER_API_KEY` from the Agents vault and run `powder-mcp`.

Registered MCP subprocesses (for example, a `bash -lc 'source ~/.secrets &&
exec powder-mcp'` server entry) resolve `POWDER_API_BASE_URL` from their own
launch environment. That value can differ silently from the operator's
interactive shell. A stale manual export is enough. Send an `initialize` call.
Compare `result.serverInfo.baseUrl` with your own `POWDER_API_BASE_URL` before
you treat an add-comment failure as a Powder bug. Two faces may point to
different deployments.

Agents that hit the HTTP API directly, without the CLI or MCP, can read
`GET /api/v1/routes` for the full route contract and example request bodies.
It names the fields that `POST /api/v1/cards` and
`POST /api/v1/cards/{id}/links` require. Use it instead of
deserialize-error trial-and-error.

### Key rotation and stale-key/stale-host runbook (powder-944)

At process boot, a registered `powder-mcp` subprocess captures
`POWDER_API_KEY` and `POWDER_API_BASE_URL`. A key rotation or deployment
hostname change does not update an already-running subprocess. It keeps sending
the old value until you restart it. Use one of these two methods:

- **Restart the MCP client** after any key rotation or host cutover. This
  always works and needs no configuration.
- Set `POWDER_API_KEY_CMD` to a shell command that prints a fresh key on
  stdout (for example, `security find-generic-password -a "$USER" -s
  powder-api-key -w`, or `op read op://Agents/POWDER_API_KEY__bridge/credential`).
  At boot, `powder-mcp` runs the command once. It runs the command once more
  the first time a request returns `401`. If the command resolves a different
  key than the failed key, `powder-mcp` retries with the new key. The caller
  does not see the rotation. `POWDER_API_KEY` remains the plain fallback.
  Leaving `POWDER_API_KEY_CMD` unset keeps the current behavior.

When rotation and retry both exhaust, or when `POWDER_API_KEY_CMD` is not set,
`powder-mcp` returns a `401` error. The error names the key prefix
`powder-mcp` used, matching the `list_keys`/`ApiKeySummary` prefix convention.
It tells the caller to restart the MCP client or configure
`POWDER_API_KEY_CMD`. After three or more consecutive `404`s on tool calls,
`powder-mcp` gives a distinct stale-host steer. `POWDER_API_BASE_URL` may point
to a stale host (a deployment cutover, powder-965's class of incident).
Restart the MCP client after fixing the URL.

## Response Evolution Contract

Treat status vocabulary changes as additive from the client's perspective.
`powder-core::CardStatus` rejects unknown values on writes. Therefore, the
server and store never persist invalid statuses. On read surfaces, clients
decode with `powder_api::ClientStatus`. An unrecognized value degrades only
that card and remains preserved as a raw string. A listing (`list_ready`,
`list_cards`, `board_stats`) must never hard-fail because one card carries a
future or retired status value. `get_card` and `get_run` return the server's
JSON verbatim, so they remain version-skew safe. When you add a status value,
deploy the server change first. Update clients at their own pace. The old
client must keep reading.

## Local Gate

```sh
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

## Red Lines

- Do not import from Gradient or Hermes `kanban.db`.
- Do not add personal or operator backlog data to the Powder repository.
- Do not treat exit zero as completion without a status update and audit trail.
