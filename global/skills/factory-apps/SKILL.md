---
disable-model-invocation: true
name: factory-apps
description: >
  Route Misty Step factory application capabilities across Canary, Powder,
  Landmark, and the Mint credential broker. Use owned surfaces for
  observability, work state, release intelligence, and credentialed outbound
  calls. Mode B has no active workflow plane; do not invent a replacement.
  Trigger: /factory-apps, /factory-stack.
argument-hint: "[canary|powder|landmark|mint|audit]"
---

# /factory-apps

Use the owned factory app before you invent local state, bespoke glue, or a
generic third-party workflow.
Product repos own the concrete skills and live CLI/API surfaces. Disabled MCP implementations are not runtime routes.
omp-config imports those skills under `misty-*` aliases and manages MCP
registration in `global/mcp.json`.

## Router

| Need | App | First surface | Fallback |
|---|---|---|---|
| uptime, incidents, error timelines, health checks, service evidence, production debugging | Canary | `misty-canary`, `canary` on `PATH`, or API | the disabled Canary MCP is not a runtime route |
| backlog, issue cards, claims, relations, operator input requests, work status | Powder | `powder` CLI or API | no MCP route; skill + CLI/API only |
| release intelligence, versions, changelogs, release notes, release kit, fleet adoption | Landmark | `misty-landmark` and `landmark describe --json` / dry-run CLI/action paths | `docs/agent-integration.md`, `docs/fleet-integration-playbook.md` |
| event-triggered agents, reflex loops, durable runs | unavailable | Mode B has no active workflow plane; keep work in Mode A until a future product is named | do not invent a replacement |
| outbound API call needing a credential (API key, token, secret) | Mint broker | Route through `http://mint.tail5f5eb4.ts.net:4949/proxy/https/<host>/<path>` with a `__mint.<alias>__` marker; Mint replaces valid markers only in request headers | Keep provider interfaces generic; Tailscale controls reachability; this harness has no Mint MCP or skill |

## Operating Rule

Use the owned app first. Follow these constraints:

- **Canary** — Query health, incidents, checks, and recent errors before you
  form a repo-local production hypothesis.
- **Powder** — Keep durable card state here, never in chat, TODO prose, or an
  ad-hoc markdown list.
- **Landmark** — Ask it to describe the repo. Do not write release intelligence
  from memory.
- **Mode B** — No active event plane is available for triggered, scheduled,
  durable, reflexive, or other unattended work. Keep ad-hoc operator work in
  Mode A and do not invent a replacement workflow service.
- **Mint** — Mint is an unrestricted credential proxy at
  `http://mint.tail5f5eb4.ts.net:4949`. Use a value-free
  `__mint.<alias>__` marker in each credential header.
  Mint does not authenticate or authorize callers.
  Tailnet reachability and dedicated-host custody are the entire boundary.
  Any reachable caller can use any loaded alias for any HTTP(S) destination.
  This harness adds no Mint MCP or skill.

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
