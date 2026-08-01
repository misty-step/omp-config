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
`http://mint.tail5f5eb4.ts.net:4949` (tailnet-only; WireGuard is the
transport encryption). Mint authenticates callers by Tailnet WhoIs,
substitutes value-free placeholders at egress, scrubs responses, and audits
each effect. Its policy file is the grant.

## Decision

Mint is the only credential path for every agent on this machine.

- Providers call Mint directly: `http://mint.tail5f5eb4.ts.net:4949/proxy/https/<host>/<path>`.
- Configuration carries only `__mint.<service>.<name>__` placeholders.
- The OpenRouter provider uses base URL
  `.../proxy/https/openrouter.ai/api/v1` and key `__mint.openrouter.default__`.
- Sessions need no wrapper process, proxy environment, or CA trust environment.
- The recipe runner keeps its proxy/CA environment allowlist as a generic
  operator passthrough only; Mint does not require it.
- A Mint 403 means the actor, service, method, or path is not authorized.
  Widen the grant in Mint policy; never work around the boundary.

`global/RULES.md` and `global/AGENTS.md` state this contract for every
session at every depth. All Agent Vault references in skills, docs, recipes,
and tests were replaced in the same change.

## Consequences

- The workstation holds zero vendor credential bytes; that guarantee is
  unchanged from the Agent Vault design.
- Credentialed calls work from any process on the tailnet host without a
  launch wrapper; the 401 class of failure is gone.
- Authorization moves from local service rules to central Mint policy;
  changing a grant requires a Mint policy deploy.
- Actor identity is per-host Tailnet WhoIs (`moomooskycow@github` on
  Mirrodin); management routes stay with `phrazzld@github`.
- Peer-harness lanes that expect an `OPENROUTER_API_KEY` environment
  variable (pi, goose, opencode, council) remain broken here until they are
  taught the Mint base URL or retired.

Verified 2026-07-31: `omp -p --model openrouter/deepseek/deepseek-v4-flash`
returned a genuine DeepSeek completion through Mint with no fallback.

## Reversal condition

Replace this decision only when a successor broker gives the same or a
stronger guarantee: zero local credential bytes, value-free client
placeholders, per-caller identity, and an auditable central grant.
