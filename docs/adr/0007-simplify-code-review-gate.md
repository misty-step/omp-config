# ADR 0007: Simplify code review gate and dynamic lane composition

- Status: Accepted
- Date: 2026-08-05

## Context

The current code review gate (`bin/review_gate.py`, `bin/review_packet.py`, `bin/review_runner.py`, `bin/review_receipt.py`) was designed as a harness-neutral evidence protocol. It contains significant accidental complexity:

1. **Redundant packet layer:** `review_packet.py` re-serializes git diffs into redacted, chunked, digest-framed files. The local bare-word hint regex (`AUTOREVIEW_TRANSPORT_RISK_HINT`) short-circuits before the vendored classifier and false-blanks prose lines containing words like `credential` or `secret`.
2. **Harness-less runner engine:** `review_runner.py` builds temp git workspaces and adapter attestations to invoke standalone CLI engines. This duplicates OMP native agent dispatch.
3. **Rigid 3-pass requirement:** `review_receipt.py` requires exactly three fixed reviewers (`autoreview`, `thermo-nuclear-review`, `thermo-nuclear-code-quality-review`). This leaves the `ponytail` critic (mandated by `global/RULES.md`) un-gated and forces prose changes to run code-heavy reviewers.

An audit confirmed that reviewers in OMP are native subagents operating in read-only worktrees. Git already provides content-addressed diffs.

## Decision

Re-architect the code review gate around native OMP agent dispatch and dynamic lane plans.

### 1. Unified verifier model (Option A)

All reviewer lanes use the native `verifier` agent envelope (`global/agents/verifier.md`). `ponytail` uses the native `ponytail` agent envelope (`global/agents/ponytail.md`).

### 2. Dynamic lane composition with integrity floor

1. **Floor classifier:** `review_common.py` defines `floor_plan(paths)` as a pure function returning the minimum required reviewer lanes for a diff.
2. **Plan freezing:** `review_gate.py freeze` receives `old_oid`, `new_oid`, and optional extra lanes from a closed catalog. It writes `planned_lanes` into `.omp/review-freeze.json` and includes it in `bundle_digest`.
3. **Receipt recording:** `review_gate.py record` verifies that submitted passes match `planned_lanes` exactly.
4. **Verification:** `review_gate.py verify` recomputes `floor_plan` from git paths and checks:
   $$\text{floor\_plan} \subseteq \text{frozen\_plan} \land \text{submitted\_passes} == \text{frozen\_plan}$$
   It also re-verifies skill hashes and worker model declarations.

### 3. Lane catalog and router table

| Change Class | Touch Pattern | Required Floor Lanes |
|---|---|---|
| Trivial | Typo, docs-only per `review_scope` | Waiver path |
| Prose | `*.md`, doctrine, config | `autoreview`, `thermo-nuclear-code-quality-review` |
| Executable Code | `bin/**`, `*.py`, `*.ts`, hooks | `autoreview`, `thermo-nuclear-review`, `ponytail` |
| High-Stakes | Auth, secrets, gates, migrations, harness | `autoreview`, `thermo-nuclear-review`, `thermo-nuclear-code-quality-review`, `ponytail` |
### 4. Packet and runner deletion

Delete `bin/review_packet.py` and `bin/review_runner.py`. Reviewers read `git diff` directly in read-only worktrees checked out at `new_oid`. Remove the bare-word redaction hint regex.

## Consequences

- Deletes ~700 lines of accidental complexity in `bin/review_packet.py` and `bin/review_runner.py`.
- Eliminates false-positive diff redaction on doctrine and documentation prose.
- Enforces `ponytail` complexity audit on all substantive code changes per `global/RULES.md`.
- Dynamically scales review latency and cost based on change risk class.
- Cryptographically binds the dynamic lane plan into `bundle_digest`, preventing agents from dropping required floor lanes.

## Reversal Condition

Re-introduce packet framing only if a non-OMP harness without direct git worktree access becomes an active review worker.
