# Factory App Capability Audit - 2026-07-03

Scope: live local checkouts for Canary, Powder, Landmark, Aesthetic,
Bitterblossom, plus Harness Kit and the local Codex config. This is an audit
snapshot, not a product status source.

## Summary Matrix

| App | Role | Skills | MCP | SDK | Harness/system state | Gap |
|---|---|---|---|---|---|---|
| Canary | observability, uptime, incidents, health checks, error timelines | product root `SKILL.md`, imported as `misty-canary`; repo-local `canary-qa` and `canary-deploy` | implemented via `bin/canary mcp-server`; historically registered in factory MCP `global` profile | TypeScript SDK in `clients/typescript` | trusted project path exists; Roster now owns the canonical MCP catalog | 2026-07-11: complete Roster-launchable entry; retired profile materializer is out of contract |
| Powder | backlog, issues/cards, claims, relations, operator input | root product `SKILL.md`, imported as `misty-powder`; repo-local `powder-qa` | implemented in `crates/powder-mcp`; historically profile-gated for non-Adminifi/non-r90 repos | no SDK observed | trusted project path exists; Roster now owns the canonical MCP catalog and launcher | SDK absent; 2026-07-11 retired profile materializer is out of contract |
| Landmark | release intelligence, versions, changelogs, release kit, fleet adoption | product root `SKILL.md`, imported as `misty-landmark`; dogfood skill remains contributor-facing | no MCP observed | no SDK observed | trusted project path exists; Harness preferred stack now says Landmark | no MCP/SDK; current product-owned surface is skill + CLI/action |
| Aesthetic | UI/UX system, Misty Step law, tokens, static registry | product root `SKILL.md`, imported as `misty-aesthetic` | no MCP observed | package/static API via `@misty-step/aesthetic` | trusted project path exists; Harness Kit imports product skill | CLI/MCP intentionally later per local vision |
| Bitterblossom | ad-hoc supervised dispatch, Mode B reflex loops, durable runs | portable product skill in `primitives/skills/.external/misty-bitterblossom`, imported as `misty-bitterblossom`; repo-local dogfood skill | read-only MCP via `bb --config <plane> mcp serve`; registered in factory MCP `factory-ops` profile | no SDK observed | trusted project path exists; Harness Kit imports product skill and installs factory MCP registry | mutating MCP tools remain intentionally absent |

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
- Bitterblossom:
  - `$HOME/Development/bitterblossom/skills/bitterblossom/SKILL.md`
  - `$HOME/Development/bitterblossom/README.md`
  - `$HOME/Development/bitterblossom/AGENTS.md`
  - `$HOME/Development/bitterblossom/docs/spine.md`
  - `$HOME/Development/bitterblossom/.agents/skills/bb-dogfood/SKILL.md`
- Harness/system:
  - `$HOME/Development/harness-kit/skills/harness-engineering/references/preferred-stack.md`
  - `$HOME/.codex/config.toml` server names only; credential values were not copied
  - active Codex tool discovery for factory app MCP names

## System Configuration Finding

The local Codex config trusts the five app checkout paths. The former Harness
Kit MCP registry was later retired in favor of Roster's single
`primitives/mcps/registry.yaml` catalog.

Do not register placeholder MCPs. Register only when the real instance and
auth source are known:

- Canary: command `bin/canary mcp-server`; registered in the `global` profile
  through a secret-free launcher that inherits env or reads
  `op://Agents/CANARY_ENDPOINT/credential` and
  `op://Agents/CANARY_API_KEY/credential`.
- Powder: `powder-mcp`; registered for the `non-adminifi-non-r90` profile and
  configured from the Agents vault with `POWDER_API_BASE_URL` from
  `op://Agents/POWDER_ENDPOINT/URL` and `POWDER_API_KEY` from
  `op://Agents/POWDER_API_KEY__bridge/credential`.
- Bitterblossom: `bb --config <plane> mcp serve`; registered for the
  `factory-ops` profile using the local plane. The audited MCP is read-only.
- Landmark: no MCP server observed; use CLI/action until the product exposes
  one.
- Aesthetic: no MCP server observed; use package/static API/law gate until the
  product exposes one.

## Remediated In Harness Kit

- Added first-party `factory-apps` skill so future agents have an app-visible
  router for Canary, Powder, Landmark, Aesthetic, and Bitterblossom.
- Added product-owned external skill imports in `registry.yaml`:
  `misty-canary`, `misty-powder`, `misty-landmark`, `misty-aesthetic`, and
  `misty-bitterblossom`.
- Added the former factory MCP registry plus `check-mcp-registry` so MCP
  policy was data, validated, and bootstrapped; Roster now owns the single
  catalog.
- Updated Harness Engineering preferred stack defaults:
  - Powder is the default backlog/work-state system.
  - Landmark replaces stale Landfall naming for release intelligence.
  - Canary production-debugging and consumer integration expectations are
    explicit.
  - Aesthetic default references package/static API/law, not just prose taste.

## Remaining Product Gaps

These require clean product-repo branches or concrete deployment credentials:

- Decide whether Powder needs a small SDK or if API/CLI/MCP is sufficient.
- Decide whether Landmark earns an MCP or whether CLI/action remains the right
  agent surface.
- Decide whether Aesthetic earns an MCP after repeated adoption work proves it
  needs one beyond skill/package/static API.
- Keep complete Roster-launchable MCPs distinct from `external` bindings that
  a consumer runtime supplies. Direct role references remain the only binding
  layer; the retired profile materializer is not part of the product contract.
