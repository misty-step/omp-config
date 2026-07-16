---
name: factory-apps
description: |
  Route Misty Step factory application capabilities. Use when choosing,
  auditing, integrating, or operating Canary, Powder, Landmark, Aesthetic,
  Bitterblossom, or mint: production observability, incidents, health
  checks, error logging, backlog/work-card state, release intelligence,
  UI/UX system adoption, event-triggered agent workflows, or routing a
  credentialed outbound API call through the agent credential broker.
  Trigger: /factory-apps, /factory-stack.
argument-hint: "[canary|powder|landmark|aesthetic|bitterblossom|mint|audit]"
---

# /factory-apps

Use the owned factory app before inventing local state, bespoke glue, or a
generic third-party workflow. Product repos own the concrete skills and MCP
servers; Roster imports those skills under `misty-*` aliases and manages MCP
registration in `primitives/mcps/registry.yaml`.

## Router

| Need | App | First surface | Fallback |
|---|---|---|---|
| uptime, incidents, error timelines, health checks, service evidence, production debugging | Canary | Canary MCP when registered | `misty-canary`, `canary` on `PATH`, API |
| backlog, issue cards, claims, relations, operator input requests, work status | Powder | Powder MCP when configured | `misty-powder`, CLI, API |
| release intelligence, versions, changelogs, release notes, release kit, fleet adoption | Landmark | `misty-landmark` and `landmark describe --json` / dry-run CLI/action paths | `docs/agent-integration.md`, `docs/fleet-integration-playbook.md` |
| UI/UX, Misty Step design law, tokens, static design registry, rendered design gate | Aesthetic | `misty-aesthetic`, `@misty-step/aesthetic` package, static API, law gate | `docs/ADOPTING.md`, `DESIGN.md` |
| event-triggered agents, reflex loops, durable runs | Bitterblossom | `misty-bitterblossom`, `bb` CLI/API | product plane config; MCP source exists but is not registered in interactive harnesses |
| outbound API call needing a credential (API key, token, secret) | mint | `primitives/skills/misty-mint/SKILL.md` — egress proxy contract (`X-Mint-Capability` header + `__mint.<service>.<name>__` placeholders) | `mint policy check`/`mint audit tail`/`mint alias list` CLI (operator-only) |

## Operating Rule

Use the owned app first (per the router); the non-obvious constraints:

- **Canary** — query health, incidents, checks, and recent errors before
  forming any repo-local hypothesis about production.
- **Powder** — durable card state lives here, never in chat, TODO prose, or an
  ad-hoc markdown list.
- **Landmark** — ask it to describe the repo rather than hand-writing release
  intelligence from memory.
- **Aesthetic** — use its tokens, recipes, registry, and law gate before adding
  one-off CSS vocabulary.
- **Bitterblossom** — only when the work is Mode B (triggered, scheduled,
  durable, reflexive, event-driven). Ad-hoc operator work stays Mode A.
- **mint** — an agent never holds credential bytes; it carries a capability
  token plus placeholders and lets mint resolve the secret at the proxy
  boundary. Not in `.external/` yet (no vendorable `SKILL.md`) — read
  `primitives/skills/misty-mint/SKILL.md` directly.

## Current Audit

`references/capability-audit-2026-07-03.md` is the historical capability
audit. For current registration truth, read `primitives/mcps/registry.yaml` and
the active harness config before changing product repos or system config.

## Fleet Integration Standard

For active Misty Step repos, load
`references/fleet-integration-standard.md` before claiming a project is
factory-integrated. The standard defines the repo-level Canary receipt,
Powder backlog, and Landmark manifest/workflow evidence expected for runtime
apps, libraries, and non-release support repos.

## Gotchas

- A product repo having an MCP implementation does not mean this harness has
  that MCP registered. Check `primitives/mcps/registry.yaml` and the active
  harness config before claiming MCP availability.
- Do not add placeholder MCP servers. A broken registered tool is worse than a
  clear CLI/API fallback.
- Bitterblossom's MCP implementation remains in the product, but its interactive
  harness registration is disabled. Mode B workloads use the CLI/API and do not
  depend on a per-thread stdio child.
- Root product skills (`SKILL.md`) and portable product skills under
  `<repo>/skills/<name>/SKILL.md` are for consumers of the app. Repo-local
  `.agents/skills/*` are usually QA/deploy/dogfood runbooks for work inside
  that repo. Do not treat one as a substitute for the other.
- Bitterblossom dispatch and run control go through the CLI/API unless
  the product changes.
