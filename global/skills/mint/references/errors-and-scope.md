# mint — errors and honest scope

Read the status code. Do not retry blindly.

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

Read mint's own `VISION.md` before you assume that a capability ships today.

- Only the egress HTTP proxy mode exists. No typed-action broker or secretless
  protocol proxy exists; `VISION.md` declares both, but neither is built.
- Backing stores today include the macOS keychain for local development and one
  service-private file per alias in production. Systemd
  `LoadCredentialEncrypted=` delivers the production file on the dedicated
  DigitalOcean node. The broker's ordinary request path does not call 1Password.
  It does not carry raw `MINT_SECRET_*` values in its environment. OpenBao remains
  future work.
- Deployed auth uses tailnet-whois (mint-924): your identity is your machine's
  tailnet peer address. Shared-secret capability auth remains only for loopback
  dev `mint serve`. No auth path exists yet for non-tailnet callers, such as DO
  App Platform apps or GitHub Actions CI. That is mint-911's OIDC work; do not
  improvise it.
- Only flat two-segment aliases (`secret://<service>/<name>`) exist. Hierarchical
  names do not exist.
- `approval_required` policy rules currently **deny** the call outright. No
  human-tap escalation exists yet. The call returns a `403`, never a
  pending/approval response.
- No hot reload exists. Restart `mint serve` after policy or capability changes.
- No SDK face exists yet. The MCP face shipped; see `operator-surfaces.md`.
