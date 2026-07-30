---
disable-model-invocation: true
name: factory-apps
description: >
  Route Misty Step factory application capabilities across Canary, Powder,
  Landmark, Aesthetic, and mint. Use owned surfaces for observability, work
  state, release intelligence, design law, and credentialed outbound calls.
  Mode B has no active workflow plane; do not invent a replacement. Trigger:
  /factory-apps, /factory-stack.
argument-hint: "[canary|powder|landmark|aesthetic|mint|audit]"
---

# /factory-apps

Use the owned factory app before you invent local state, bespoke glue, or a
generic third-party workflow.
Product repos own the concrete skills and MCP servers.
omp-config imports those skills under `misty-*` aliases and manages MCP
registration in `global/mcp.json`.

## Router

| Need | App | First surface | Fallback |
|---|---|---|---|
| uptime, incidents, error timelines, health checks, service evidence, production debugging | Canary | `misty-canary`, `canary` on `PATH`, or API | the disabled Canary MCP is not a runtime route |
| backlog, issue cards, claims, relations, operator input requests, work status | Powder | Powder MCP when configured | the Powder product skill, CLI, API |
| release intelligence, versions, changelogs, release notes, release kit, fleet adoption | Landmark | `misty-landmark` and `landmark describe --json` / dry-run CLI/action paths | `docs/agent-integration.md`, `docs/fleet-integration-playbook.md` |
| UI/UX, Misty Step design law, tokens, static design registry, rendered design gate | Aesthetic | `misty-aesthetic`, `@misty-step/aesthetic` package, static API, law gate | `docs/ADOPTING.md`, `DESIGN.md` |
| event-triggered agents, reflex loops, durable runs | unavailable | Mode B has no active workflow plane; keep work in Mode A until a future product is named | do not invent a replacement |
| outbound API call needing a credential (API key, token, secret) | mint | `global/skills/mint/SKILL.md` — egress proxy contract (`X-Mint-Capability` header + `__mint.<service>.<name>__` placeholders) | `mint policy check`/`mint audit tail`/`mint alias list` CLI (operator-only) |

## Operating Rule

Use the owned app first. Follow these constraints:

- **Canary** — Query health, incidents, checks, and recent errors before you
  form a repo-local production hypothesis.
- **Powder** — Keep durable card state here, never in chat, TODO prose, or an
  ad-hoc markdown list.
- **Landmark** — Ask it to describe the repo. Do not write release intelligence
  from memory.
- **Aesthetic** — Use its tokens, recipes, registry, and law gate before you add
  one-off CSS vocabulary.
- **Mode B** — No active event plane is available for triggered, scheduled,
  durable, reflexive, or other unattended work. Keep ad-hoc operator work in
  Mode A and do not invent a replacement workflow service.
- **mint** — An agent never holds credential bytes.
  It carries a capability token and placeholders.
  mint resolves the secret at the proxy boundary.
  It is not in `.external/` yet because no vendorable `SKILL.md` exists.
  Read `global/skills/mint/SKILL.md` directly.

## Current Audit

`references/capability-audit-2026-07-03.md` is a historical capability audit.
Read `global/mcp.json` and the active harness config for current registration
truth before you change product repos or system config.

## Fleet Integration Standard

For active Misty Step repos, load `references/fleet-integration-standard.md`
before you claim a project is factory-integrated.
The standard defines the repo-level Canary receipt, Powder backlog, and
Landmark manifest/workflow evidence for runtime apps, libraries, and
non-release support repos.

## Gotchas

- A product repo can have an MCP implementation without this harness registering
  that MCP. Check `global/mcp.json` and the active harness config before you
  claim MCP availability.
- Do not add placeholder MCP servers. A broken registered tool is worse than a
  clear CLI/API fallback.
- Mode B has no active workflow plane or registered event-workflow MCP.
  Keep triggered and scheduled work in Mode A until a future product is named.
- Root product skills (`SKILL.md`) and portable product skills under
  `<repo>/skills/<name>/SKILL.md` serve app consumers.
  Repo-local `.agents/skills/*` usually provide QA, deploy, or dogfood runbooks
  for work inside that repo. Do not treat one as a substitute for the other.
