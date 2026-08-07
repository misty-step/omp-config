# Factory App Capability Audit - 2026-07-03

Scope: This snapshot covers live local checkouts for Canary, Powder, Landmark,
Aesthetic, Harness Kit, and the local Codex config.
Use it as an audit snapshot, not as a product status source. A former
event-plane capability is intentionally omitted; Mode B has no active owner.
Harness route update 2026-08-07: Powder MCP is not a runtime route. Use the `powder` skill with CLI/API only.

## Summary Matrix

| App | Role | Skills | MCP | SDK | Harness/system state | Gap |
|---|---|---|---|---|---|---|
| Canary | observability, uptime, incidents, health checks, error timelines | product root `SKILL.md`, imported as `misty-canary`; repo-local `canary-qa` and `canary-deploy` | implemented via `bin/canary mcp-server`; historically registered in factory MCP `global` profile | TypeScript SDK in `clients/typescript` | trusted project path exists; the global MCP catalog is authoritative | 2026-07-11: complete launcher entry; retired profile materializer is out of contract |
| Powder | backlog, issues/cards, claims, relations, operator input | root product `SKILL.md`, imported as the Powder product skill; repo-local `powder-qa` | product crate `powder-mcp` existed at audit time; harness does not register it | no SDK observed | trusted project path exists; skill + CLI/API is the harness route | SDK absent; harness MCP route removed 2026-08-07 |
| Landmark | release intelligence, versions, changelogs, release kit, fleet adoption | product root `SKILL.md`, imported as `misty-landmark`; dogfood skill remains contributor-facing | no MCP observed | no SDK observed | trusted project path exists; Harness preferred stack now says Landmark | no MCP/SDK; current product-owned surface is skill + CLI/action |
| Aesthetic | UI/UX system, Misty Step law, tokens, static registry | product root `SKILL.md`, imported as `misty-aesthetic` | no MCP observed | package/static API via `@misty-step/aesthetic` | trusted project path exists; Harness Kit imports product skill | CLI/MCP intentionally later per local vision |

## Evidence Read

- Canary:
  - `$HOME/Development/canary/README.md`
  - `$HOME/Development/canary/docs/factory-fleet-integration.md`
  - `$HOME/Development/canary/docs/compatibility-policy.md`
  - `$HOME/Development/canary/clients/typescript/package.json`
  - `$HOME/Development/canary/.agents/skills/canary-qa/SKILL.md`
  - `$HOME/Development/canary/.agents/skills/canary-deploy/SKILL.md`
- Powder:
  - `$HOME/Development/powder/SKILL.md`
  - `$HOME/Development/powder/AGENTS.md`
  - `$HOME/Development/powder/README.md`
  - `$HOME/Development/powder/crates/powder-mcp/Cargo.toml`
- Landmark:
  - `$HOME/Development/landmark/README.md`
  - `$HOME/Development/landmark/docs/agent-integration.md`
  - `$HOME/Development/landmark/docs/fleet-integration-playbook.md`
  - `$HOME/Development/landmark/skills/landmark-dogfood/SKILL.md`
  - `$HOME/Development/landmark/package.json`
- Aesthetic:
  - `$HOME/Development/aesthetic/README.md`
  - `$HOME/Development/aesthetic/docs/ADOPTING.md`
  - `$HOME/Development/aesthetic/docs/vision.md`
  - `$HOME/Development/aesthetic/law/README.md`
  - `$HOME/Development/aesthetic/package.json`
  - `$HOME/Development/aesthetic/DESIGN.md`
- Harness/system:
  - `$HOME/Development/harness-kit/skills/harness-engineering/references/preferred-stack.md`
  - `$HOME/.codex/config.toml` server names only; credential values were not copied
  - active Codex tool discovery for factory app MCP names

## System Configuration Finding

The local Codex config trusts the five app checkout paths.
The legacy MCP registry was retired in favor of the single
`global/mcp.json` catalog.

Do not register placeholder MCPs.
Register an MCP only when you know the real instance and auth source:

- Canary: command `bin/canary mcp-server`; registered in the `global` profile
  through a secret-free launcher that inherits env or reads
  `op://Agents/CANARY_ENDPOINT/credential` and
  `op://Agents/CANARY_API_KEY/credential`.
- Powder: harness uses `powder` CLI/API through the product skill. Do not
  register `powder-mcp`. At audit time a vault-backed MCP profile existed; that
  is not the current runtime route.
- Landmark: no MCP server observed; use CLI/action until the product exposes
  one.
- Aesthetic: no MCP server observed; use package/static API/law gate until the
  product exposes one.

## Remediated in Harness Kit

- Added the first-party `factory-apps` skill so future agents have an app-visible
  router for Canary, Powder, Landmark, and Aesthetic.
- Added product-owned external skill imports in `registry.yaml`:
  `misty-canary`, the Powder product skill, `misty-landmark`, and
  `misty-aesthetic`.
- Added the former factory MCP registry and `check-mcp-registry` so MCP policy
  becomes data, validation, and bootstrap. The global MCP catalog now owns the
  single catalog.
- Updated Harness Engineering preferred stack defaults:
  - Set Powder as the default backlog/work-state system.
  - Landmark replaced stale Landfall naming for release intelligence.
  - Made Canary production-debugging and consumer integration expectations
    explicit.
  - Set the Aesthetic default to package/static API/law, not only prose taste.

## Remaining Product Gaps

Resolve these gaps on clean product-repo branches or with concrete deployment
credentials:

- Decide whether Powder needs a small SDK or whether API/CLI is sufficient. MCP is not the harness route.
- Decide whether Landmark earns an MCP or whether CLI/action remains the right
  agent surface.
- Decide whether Aesthetic earns an MCP after repeated adoption work shows that
  it needs one beyond skill/package/static API.
- Keep complete launcher MCPs distinct from `external` bindings supplied by a
  consumer runtime. Direct role references remain the only binding layer.
  The retired profile materializer is not part of the product contract.
