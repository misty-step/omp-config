# Vendored external skills

Copied upstream skill bodies. Not local authorship.

## Rules

1. `registry.yaml` lists every committed vendor pin.
2. Each vendor dir has `.sync-meta.json` (commit, license hash, payload hashes).
3. Every pin names live consumers under `global/`.
4. `bin/check` fails on registry/receipt/payload/license/consumer drift.
5. Do not edit vendored payload bytes in place. Re-pin upstream instead.

## Keep set (2026-08-07)

| Vendor | Why |
|---|---|
| cursor-thermos | Review gate leaves |
| openclaw-autoreview | Review gate autoreview helper |
| dietrich-ponytail | `/ponytail` + refactor |
| mattpocock-skills | writing-for-agents, grilling, wayfinder, codebase-design, improve-codebase-architecture, plus domain-modeling and setup-matt-pocock-skills (required by wayfinder) |
| misty-aesthetic/canary/landmark | factory-apps |
| anthropic-frontend-design | document/render |
| vercel-agent-browser + dogfood | verify-live / harness create |
| julius-caveman | groom/refactor tone |
| nous-creative-ideation | groom optional creative pass |

## Explicit non-goals

Do not vendor bulk catalogs (full Matt pack, obra packs, Leon kits, random OpenAI skill zoos) without a named consumer path in this repo. Prefer a thin local skill over a fat upstream tree.

## Advance a pin

Fetch upstream at an immutable SHA, replace payload + `.sync-meta.json` + registry pin together, run `bin/check`.
