# Mint wiring on this machine

This workstation holds **zero vendor credential bytes**. Every credentialed
API call from agents routes through the production mint broker over the
tailnet. Decided 2026-07-20 (mint-917 closeout); decision record + proof
chain: `misty-step/mint` → `docs/receipts/mint-laptop-tailnet-consumer-2026-07-20.md`.

## How it works

- **Identity:** the broker resolves this device's tailnet peer address via
  `tailscale whois` → actor `phrazzld@github`. No bearer, no local token —
  nothing an agent could leak.
- **Placeholders:** agent-visible config carries `__mint.<service>.<name>__`
  where a key would sit. The broker swaps in the real secret host-side,
  after the request leaves the agent.
- **Wiring points:**
  - `global/models.yml` — the `openrouter` provider's `baseUrl` targets the
    broker's `/proxy/https/openrouter.ai/api/v1` route; `apiKey` is the
    placeholder.
  - `~/.omp/agent/.env` — `MINT_BASE_URL` names the broker (tailnet IP:4949)
    for direct/skill callers.
- **Policy & budgets** live on the broker host
  (`/opt/mint/current/config/policy.yaml`): per-route allow rules with
  `require_placeholder`, `never_relay_credentials`, and call budgets
  (e.g. openrouter `/api/v1/*` max_calls 500). Default deny.

## Use it (agents)

Read `skill://mint`. Short form: send the vendor request to
`$MINT_BASE_URL/proxy/{scheme}/{host}/{path}` with the placeholder in the
auth header. Non-2xx codes are specific — 403 with
`require_placeholder_violation` means you put something key-shaped in a
header; 403 `default:deny` means the route isn't declared. Never fall back
to a raw key.

## Extend it (add a service)

On the broker host (ssh `mint`):
1. Add the secret alias (`secret://<service>/<name>`) to custody +
   `aliases.yaml`.
2. Add a policy rule for actor `phrazzld@github`: narrowest path that
   works, `require_placeholder: true`, a budget.
3. `mint policy check config/policy.yaml`, then SIGHUP the broker
   (atomic reload, last-known-good on failure).
4. Prove one live call from this machine and read its audit row:
   `mint audit tail --actor phrazzld@github`.

## Verify / audit

- `mint adoption scan <file>` (from the mint repo) proves a config surface
  carries no raw credentials.
- Every allow AND deny is an audit row on the host with a named reason —
  if a call misbehaves, read the audit before touching config.

## What NOT to do

- No raw vendor keys in `.env`, `models.yml`, `mcp.json`, shell exports, or
  "temporary" scripts. If a key ever appears in agent context, that is a
  mint-bypass bug: stop and flag it.
- The macOS root-broker install (`mint-local-*` scripts) is retired on this
  machine — its runner refuses real runs. Leftover-state sweeper:
  `sudo scripts/mint-local-teardown.sh` in the mint repo.

## Availability

Mint is a proxy, not a vault. Broker unreachable → calls fail closed, keys
never exposed. Host lost → rebuild from `deploy/` declarations and re-mint
vendor keys from their dashboards; you are never locked out of accounts you
own.
