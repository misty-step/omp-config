# /mcp-design eval

The one claim `mcp-design` must earn: **given a bloated or proposed MCP server
surface, the skill makes an agent produce a smaller, persona-scoped, measured
scan/read/write design with bounded outputs where raw prompting defaults to
REST-shaped tools or generic best-practice prose.**

This is a `mode-eval` A/B run. Arms: A = `/mcp-design` installed and invoked;
B = raw same-model prompt; C = relevant public `mcp-builder` skill where
allowed. Grade blind, objective first, judge with a different model family than
the workers.

## Fixtures

Each fixture supplies a frozen tool catalog or design brief plus a measurement
packet. The arm returns a proposed tool catalog, response contracts, and proof
loop. No implementation edits.

| # | Prompt | Repo @ SHA | Forbidden edits | What it stresses |
|---|---|---|---|---|
| 1 | "Audit this Powder work-board MCP: 31 tools, `list(20)` ~14k tokens, `list(50)` ~31.5k, full objects in lists, duplicate criteria text, null fields, unbounded work logs. Redesign the surface." | roster fixture TBD | any source edit | scan vs read split, byte-field measurement, duplication/null deletion, bounded append-only reads |
| 2 | "Design an MCP server for a bug tracker API with issues, comments, projects, labels, and writes. Agents keep choosing the wrong issue tool." | synthetic API fixture TBD | any source edit | outcome tools vs REST mirror, namespacing, CRUD consolidation vs split |
| 3 | "Review this proposal: add dynamic server-side tool discovery toggles to reduce default context, plus full JSON list responses for compatibility." | github-mcp-server dynamic-discovery notes TBD | any source edit | rejects server-side dynamic discovery, assigns discovery/offload to harness, preserves stable toolsets |

## Objective Checks

- [ ] Names the persona and default job before changing the catalog.
- [ ] Classifies tools or tasks into scan/read/write.
- [ ] Produces list contracts where list output is a strict subset of get/read.
- [ ] Specifies pagination or limits for every growing surface.
- [ ] Removes or flags duplicated text, null/default fields, pretty-print bloat,
      and unneeded URLs in list outputs.
- [ ] Gives a measurement loop: `tools/list` schema tokens plus representative
      stdio `tools/call` bytes/tokens by field.
- [ ] Requires paired eval or transcript comparison for format/tool-shape
      changes.
- [ ] Does not recommend server-side dynamic discovery as the primary fix.

## Rubric

| Dimension | 5 | 1 |
|---|---|---|
| Design compression | Smaller default toolset with explicit persona and justified exceptions | Keeps or expands the full endpoint catalog |
| Response discipline | Clear scan/read/write return shapes and bounds | Vague "return concise data" advice |
| Measurement | Concrete stdio token/byte audit and eval metrics | Generic "run tests" or no falsifier |
| Agent steering | Tool descriptions, errors, truncation, and instructions steer next calls | Descriptions are developer docs or errors are opaque |
| Source fidelity | Uses current spec/research constraints without false citations | Cites stale or unverified claims as facts |

## Pass Condition

Arm A beats B on at least 2 of 3 fixtures for response discipline and
measurement, ties-or-wins every objective check, and does not lose source
fidelity. A no-op skill fails because raw prompting usually states
"agent-friendly tools" but omits the byte audit, list subset contract, and
dynamic-discovery caveat.

## Human Anchor

The operator blind-grades fixture 1 because it is grounded in a real Powder MCP
audit. Record the verdict here after the first run. PENDING - no run yet.

## Cadence

- Edit-time: run fixture 1 as a fresh-agent smoke on any `mcp-design` body edit.
- Contract change: full 3-fixture A/B with decorrelated judge.
- Major MCP spec or frontier-model release: refresh `references/sources.md` and
  rerun at least fixtures 1 and 3.

## Run Log

No run yet. Spec seeded 2026-07-08 with the first skill commit.
