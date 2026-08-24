---
name: pulse
description: Generate an executive single-pane-of-glass HTML artifact of production vitality, work queues, codebase trajectory, and architectural topology.
disable-model-invocation: true
argument-hint: "[target-path] [--window=30d]"
---

# Pulse

Generate a self-contained, verifiable single-pane-of-glass HTML cockpit
documenting live production vitality, work queue topography, Git churn
trajectories, architectural submodules, and dual-persona philosophy critiques
(Linus Torvalds and John Ousterhout).

```text
probe prod -> query ledger -> trace git -> map architecture -> evaluate personas -> render html artifact
```

## Stance

- Production truth beats recorded intention. A green test or a closed ticket
  proves nothing about deployed reality. Probe the live surface.
- Deletions are progress; sprawl is technical debt. Measure churn as a
  simplification vector ($\text{Deletions} / \text{Additions}$).
- Codebase structure must reflect deep modules (Ousterhout) and direct data
  structures without speculative wrappers (Torvalds).
- The rendered artifact is a zero-dependency, self-contained HTML file. No
  external asset dependencies; viewable offline and in Herdr panes.

## 1. Probe Production Vitality

Query the authoritative runtime environment for the current target:

- **Target and Host**: Identify target host and deployment record from
  `estate/` or project configuration (`sanctum-host`, `canary`, or active
  droplet).
- **Deployed SHA**: Compare remote deployed Git commit SHA against local
  `HEAD`.
- **Live Probes**: Run active synthetic probes (HTTP `/healthz`, `/live`, socket
  ping, database WAL status) and capture latency ($p_{50}, p_{99}$) and response
  proof.
- **Exception Envelope**: Check error monitoring (Sentry CLI / logs) for
  unhandled panics or 5xx spikes in the active window (24h/7d). If Sentry or
  telemetry is unconfigured or unreachable, record `Unprobed` explicitly.

Completion criterion: Target host, deployed SHA match status, live probe table
with latencies, and exception count are settled with primary evidence.

## 2. Inspect Work Ledger & Thematic Topography

Query the project work ledger (Powder or repository issue tracking):

- **Active Themes**: Synthesize 2–4 overarching operational themes from
  current in-flight and upcoming work items (e.g. *“Zero-copy serialization”*,
  *“CAS lock idempotency”*).
- **Queue Breakdown**: Enumerate items in progress (`WIP`), takeable ready
  tasks, and recently settled/delivered milestones.
- **Velocity**: Track lead time and settled task throughput over the selected
  window.

Completion criterion: Work items grouped by theme and status (WIP, Ready,
Settled) with assigned agents/owners.

## 3. Extract Git Churn & Simplification Trajectory

Analyze Git history across the specified window (default `30d`):

- **Net Churn Trend**: Calculate weekly rolling lines added ($+$) and deleted
  ($-$). Exclude generated lockfiles, fixtures, and minified vendor blobs to
  prevent metric corruption.
- **Simplification Ratio**: Compute $\text{Lines Deleted} / \text{Lines Added}$.
  A ratio $> 1.0$ indicates net simplification; $< 1.0$ indicates net expansion.
- **Subsystem Churn Map**: Group churn by major directory/submodule (e.g.
  `internal/store`, `internal/transport`, `pkg/api`).
- **Hotspot Detection**: Identify top 3–5 frequently mutated files indicating
  structural fragility or boundary leaks.

Completion criterion: Weekly add/delete numbers, simplification ratio,
subsystem churn breakdown, and hotspot files computed directly from Git log.

## 4. Map Architectural Submodules & Thermal Footprint

Map the system's structural components and overlay recent mutation activity:

- **Topology Diagram**: Identify entrypoints (CLI/HTTP/RPC), core engines,
  storage engines, and external boundaries.
- **Heat Allocation**: Highlight nodes with their share of recent commit churn
  (e.g. High Heat $\ge 40\%$ churn, Medium Heat, Cold $\le 10\%$).
- **Coupling Assessment**: Note direct vs decoupled paths (e.g. ring buffers,
  isolated message channels, or tight foreign imports).

Completion criterion: Structural graph with nodes, links, boundaries, and
churn heat levels clearly specified.

## 5. Evaluate Architectural Personas

Perform two independent, blunt architectural evaluations:

### Torvalds First-Principles Lens (Data Structures & Directness)
- **Data Structure Reality**: Are core models clean, cache-friendly, and
  minimal, or bloated with indirect abstractions and unnecessary allocations?
- **Indirection Audit**: Are there single-implementation interfaces,
  pass-through wrappers, or speculative layers obscuring the data path?
- **Special Cases & Error Invariants**: Are edge cases handled by clean design
  invariants (e.g. pointer math, circular ring buffers) or masked with
  speculative branching and defensive wrapper noise?
- **Verdict & Score**: Numerical score (1–10) with direct, actionable
  recommendations.

### Ousterhout Philosophy Lens (Deep Modules & Information Hiding)
- **Module Depth**: Are subsystems deep (narrow, simple interface concealing
  substantial internal implementation) or shallow (thin wrappers that add cognitive
  load without simplifying callsites)?
- **Information Leakage**: Do internal implementation details (e.g. lock tokens,
  file offsets, low-level data structures) leak across boundary interfaces?
- **Errors Defined Out of Existence**: Are edge conditions defined out of
  existence by design, or are exceptions and error cascades passed up the call
  stack?
- **Verdict & Score**: Numerical score (1–10) with interface-simplification
  recommendations.

Completion criterion: Both persona cards contain explicit, source-grounded
findings, quotes, scores, and concrete recommendations.

## 6. Render Self-Contained HTML Cockpit

Assemble all collected data into a single, zero-dependency HTML file:

- **File Destination**: Write to `artifacts/pulse-YYYY-MM-DD.html` (or project
  reporting directory).
- **Visual Design**: Dark-mode terminal palette (`#0d1117`, `#161b22`, `#30363d`),
  crisp typography (monospace for hashes, metrics, and tables), responsive 12-column
  grid.
- **Visualizations**:
  - Inlined SVG bar chart for weekly additions vs deletions across the zero axis.
  - Inlined SVG / Mermaid topology map showing components and thermal highlights.
  - Subsystem churn bars and status pills.
- **Delivery**: Return the absolute path and file URL (`file://...`) and verify
  rendering in the browser tool or Herdr pane.

Completion criterion: Standalone HTML artifact generated, valid HTML5, zero
broken asset references, viewable directly in browser.
