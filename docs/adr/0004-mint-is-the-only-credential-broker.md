# ADR 0004: Mint is the only credential broker

- Status: Accepted
- Date: 2026-07-31

## Context

This configuration previously named Agent Vault as the credential boundary.
The OpenRouter provider carried the `__OPENROUTER_API_KEY__` sentinel.
An Agent Vault service rule replaced `Authorization` inside a wrapper process.
The wrapper set proxy and CA trust environment variables for each session.

The workbench moved from macOS (Serenity) to Linux (Mirrodin) on 2026-07-31.
Agent Vault was never ported and is retired.
Every `openrouter/*` model failed with `401 Missing Authentication header`.

Mint is the live Misty Step credential broker at
`http://mint.tail5f5eb4.ts.net:4949` on the tailnet. Mint replaces valid
markers only in request headers and relays upstream responses unchanged.
It does not authenticate or authorize callers. Tailscale reachability and
dedicated-host custody are the entire security boundary.

## Decision

Mint is the only credential path for every agent on this machine.

- Providers call Mint directly: `http://mint.tail5f5eb4.ts.net:4949/proxy/https/<host>/<path>`.
- Configuration carries only exact `__mint.<alias>__` markers.
- The OpenRouter provider uses base URL
  `.../proxy/https/openrouter.ai/api/v1` and key marker `__mint.openrouter.default__`.
- Sessions need no wrapper process, proxy environment, or CA trust environment.
- The recipe runner keeps its proxy and CA environment allowlist as a generic
  operator passthrough only. Mint does not require it.
- Any caller that reaches Mint can use any loaded alias for any HTTP(S) destination.
- A completed 403 is an upstream response, not a Mint authorization decision.

`global/RULES.md` and `global/AGENTS.md` state this contract for every
session at every depth. All Agent Vault references in skills, docs, recipes,
and tests were replaced in the same change.

## Consequences

- The workstation holds zero vendor credential bytes. This guarantee is
  unchanged from the Agent Vault design.
- Credentialed calls work from any process that can reach Mint without a
  launch wrapper.
- Mint adds no per-caller authorization. Tailscale controls reachability.
- Mint records the observed TCP source address for value-free local audit only.
- Provider and product systems keep their own authorization behavior.
- Peer-harness lanes (pi, goose, opencode; council uses these) are
  Mint-routed per-tool: `~/.pi/agent/models.json`,
  `~/.config/goose/config.yaml` + `secrets.yaml`, and
  `~/.config/opencode/opencode.json`. Each holds the Mint base URL and the
  `__mint.openrouter.default__` placeholder; no `OPENROUTER_API_KEY`
  environment variable exists.

Verified 2026-07-31: `omp -p --model openrouter/deepseek/deepseek-v4-flash`
returned a genuine DeepSeek completion through Mint with no fallback.
Verified 2026-08-01: pi 0.83.0, goose 1.45.0, and opencode 1.18.11 each
returned a `LANE_OK` completion through the Mint route with no env vars.

## Reversal condition

Replace this decision only when a successor gives the same routine containment:
zero local vendor credential bytes and value-free client markers. Stronger
authorization requires a separate accepted product decision.
