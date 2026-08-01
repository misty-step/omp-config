---
disable-model-invocation: true
name: powder
description: |
  Use when an agent must inspect, claim, update, request input for, or complete
  Powder work cards. Powder is a self-hostable, agent-first work board with
  durable cards, runs, relations, audit events, and proof.
argument-hint: "[list-ready|claim|update-status|update-relations|request-input|complete-card]"
---

# Powder

Powder is a self-hostable work board exposed through the `powder` CLI and API.
Use it for durable cards, claims, relations, runs, operator input, audit events, and closeout.
Treat cards as context objects with acceptance criteria and proof, not status rows.
Store cards in the deployed database, not this repository, chat, TODO prose, or ad-hoc markdown.
Read `VISION.md` before changing scope, card/run model, runner boundary, or self-hosting.

## Routing

- Use Powder for ordinary Misty Step work state, cards, claims, relations, input requests, and status.
- Use Habitat for Adminifi and R90 work. Never use Powder for the R90 work ledger.
- Powder MCP is disabled and is not a runtime route. Use the `powder` CLI or API.
- Claim one card before mutation. Use the full repository label, such as `misty-step/canary`.
- Keep production health and incidents in Canary. Keep release intelligence in Landmark.
- Do not create local ticket files or a second durable work ledger.

## Setup and connection

Select exactly one mode:

- Local SQLite: set `POWDER_DB_PATH` to the instance database.
- Remote API: set `POWDER_API_BASE_URL` to
  `http://mint.tail5f5eb4.ts.net:4949/proxy/https/<host>/<path>`.
  Set `POWDER_API_KEY` to the value-free `__mint.powder.default__`
  placeholder (alias `secret://powder/default`).

No in-memory mode exists; claims and completions must survive exit.
Mint identifies callers through Tailnet WhoIs.
Mint policy owns authorization at the upstream boundary.
Use no wrapper, proxy environment, CA environment, or local key bytes.
`--db` selects SQLite and overrides remote variables; local smoke commands cannot mutate the deployed board.
Run `powder-server` with `POWDER_DB_PATH`, `POWDER_AUTH_MODE=api-key`, and `POWDER_BIND_ADDR` for HTTP.

Remote-capable `powder` commands omit `--db` when remote variables are set:
`list-ready`, `list-cards`, `papercut`, `get-card`, `create-card`, `claim`, `heartbeat`, `renew-claim`, `transfer-claim`,
`release-claim`, `update-status`, `check-criterion`, `add-link`, `add-comment`, `append-work-log`, `request-input`, and
`complete-card`. The same commands work with `--db`; no remote closeout wrapper exists.
The `--db`-only commands are `update-relations`, `get-run`, `list-awaiting-input`, `answer-input`, `repository-*`,
`import-github-issues`, `key-*`, and `subscription-*`. Without `--db`, they fail with `missing --db`.

## Card lifecycle and safety

Cards without acceptance criteria cannot be claimed.

Inspect card and run before mutation. Confirm acceptance, proof, repository, relations, and claim state.
Claim before changes. Supply `agent`; retain `run_id`.
Remote API leases belong to the authenticated principal, not the worker label.
One principal may coordinate workers. Renew or heartbeat claims; release or transfer on ownership change.
Append attributed work logs throughout work. Add attributed links and comments.
Request input with the exact question. Resume only after an answer.
The server scrubs known secret shapes from stored bodies.
Use `update-status` and `check-criterion` to record state and acceptance changes.

Relation writes are reciprocal and atomic.
`related` is symmetric. `blocks` and `blocked_by` mirror each other.
Missing peer IDs are tolerated and are not mirrored.
Parent edges never block. Child completion never completes the parent. Parent acceptance remains authoritative.
Use `powder relations-doctor --db <path>` to report graph mismatches; add `--repair` to fix and audit each one.

Close cards only through `complete-card` or `update-status`. Attach proof and shipping evidence.
Do not treat process exit zero as completion without a status update and audit trail.

## Red lines

- Do not import `kanban.db` from Gradient or Hermes.
- Do not add personal or operator backlog data to the Powder repository.
