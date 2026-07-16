# mint — errors and honest scope

## Errors — read the status code, don't retry blind

| Status | Meaning | What it means for you |
|---|---|---|
| `401` | No tailnet identity resolved for your connection | mint could not `tailscale whois` your real peer address — you are off-tailnet, coming through a laundering hop (`tailscale serve`/443, some proxy), or the node is unknown. Fix your network path; no header you send can change this. (Loopback dev `mint serve` only: a missing/invalid `X-Mint-Capability` token also 401s.) |
| `403` | No matching policy rule (deny-by-default), or the matched rule has `approval_required: true` | mint made **zero** upstream calls either way. Ask the operator for a policy rule (or for the human-tap approval mint doesn't implement yet) — don't retry. |
| `429` | Over budget (`max_calls` exceeded) | Session/rule call budget is exhausted. Stop calling this service until budget resets or is raised. |
| `503` | Circuit breaker open for that host | The upstream host has been failing repeatedly; mint is short-circuiting. Back off. |
| `504` | Upstream request timed out | The vendor didn't respond in time. Safe to retry with backoff. |

Every response body — including denials — is scrubbed of known-sensitive JSON
fields (`access_token`, `refresh_token`, `private_key`, `client_secret`,
`api_key`) before it reaches you.

## What mint doesn't do yet (honest scope)

See mint's own `VISION.md` before assuming a capability beyond what ships today.

- Only the egress HTTP proxy mode exists — no typed-action broker, no
  secretless protocol proxy (both declared in VISION.md, neither built).
- Backing stores today: the macOS keychain for local development and one
  service-private file per alias in production, delivered through systemd
  `LoadCredentialEncrypted=` on the dedicated DigitalOcean node. The broker's
  ordinary request path does not call 1Password and does not carry raw
  `MINT_SECRET_*` values in its environment. OpenBao remains future work.
- Deployed auth is tailnet-whois (mint-924): your identity is your machine's
  tailnet peer address. Shared-secret capability auth survives only for
  loopback dev `mint serve`. There is NO auth path yet for non-tailnet
  callers (DO App Platform apps, GitHub Actions CI) — that is mint-911's
  OIDC work, not something to improvise around.
- Only flat two-segment aliases (`secret://<service>/<name>`) — no
  hierarchical names.
- `approval_required` policy rules currently **deny** the call outright. There
  is no human-tap escalation yet; it comes back as a `403`, never a
  pending/approval response.
- No hot reload — policy and capability changes require restarting `mint serve`.
- No SDK face yet (the MCP face shipped — see `operator-surfaces.md`).
