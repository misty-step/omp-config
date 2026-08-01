---
disable-model-invocation: true
name: quality-operations
description: |
  Audit, assess, and remediate operational quality — reporting, visibility,
  observability, incident preparedness, runbooks, drills, evidence retention —
  with comparable trend evidence per run.
argument-hint: "[repo] [--audit-only|--remediate|--trends]"
---

# /quality-operations

Run one audit-assess-remediate loop for operational quality in one target repository.
The loop covers seven fixed domains: `reporting`, `visibility`, `observability`,
`incident-preparedness`, `runbooks`, `drills`, and `evidence-retention`.
Every run writes comparable artifacts keyed by repository, PR, SHA, branch,
tool version, and timestamp.

- `references/run-artifact.md` — artifact layout and machine-readable schemas.
- `references/trend-governance.md` — trend storage, reports, baseline and
  threshold governance, retention, privacy, and failure behavior.
- `references/domain-audits.md` — per-domain measurable targets, probes, and
  remediation routes, including the drill safety rule.

Do not use this loop for one live production failure; route that to `cassandra`.
Do not use it to design gate mechanics; `/ci` owns gates, and this loop consumes
their reports as evidence.

## Modes

- Default: full loop — inventory, target, audit, assess, remediate, verify,
  delta audit. Steps 1–6 record `mode: "full"`; the step-7 delta audit writes
  its own run record with `mode: "delta"`. `delta` is a loop step, never a
  CLI flag.
- `--audit-only`: stop after the assessment artifacts and trend row. Propose
  remediation; execute none. Records `mode: "audit-only"`.
- `--remediate`: start from the latest recorded assessment; skip
  re-inventory. Records `mode: "remediate"`.
- `--trends`: recompute the trend report from stored rows; audit nothing and
  write no run record.

Run records store `mode` ∈ `full | audit-only | remediate | delta`
(`references/run-artifact.md`).

## Loop

The lead owns intent, target state, ranking, synthesis, and integration.
Delegate per the Shared Operating Spine (Act) and the `dispatch` skill.
Critics and auditors get the artifact and the oracle only — never the lead's
reasoning trail (Shared Operating Spine: Prove).

1. **Inventory.** Dispatch `scout` for a bounded map or `magellan` for a broad
   sweep of current state per domain: report surfaces, ledgers, monitors,
   incident docs, runbooks, drill records, and evidence directories. Lanes
   return cited sources, not judgment.
2. **Target.** The lead writes one measurable target state per domain from
   `references/domain-audits.md` and the committed `baseline.json`. A target
   without a number or a binary probe is not a target.
3. **Audit.** Dispatch audit lanes per domain group. Live probes use `qa` with
   `verify-live`. Observability queries use the Canary CLI/API through
   `factory-apps`. Drills obey the safety rule in `references/domain-audits.md`.
   Every finding carries evidence: exact command, output path, screenshot, or
   log excerpt. A lane that cannot probe returns `missing` with a reason; it
   never guesses a status.
4. **Assess.** The lead writes `run.json`, `findings.ndjson`, and
   `assessment.md`, then appends one row to `trends.ndjson`. Machine artifacts
   come first; the human report cites them.
5. **Remediate.** The lead ranks accepted gaps into one findings packet.
   Dispatch `fixer` for the packet. Dispatch `builder` for structural work that
   a packet cannot carry. A waived finding records a reason and an expiry date.
6. **Verify.** An independent `qa` lane re-runs the exact failed probes against
   live behavior. An author lane never verifies its own remediation.
7. **Delta audit.** Re-audit the remediated domains at the new SHA and append
   the delta row, so the trend store records the improvement as data.

## Storage and governance

All run artifacts live in the audited repository under
`.evidence/quality-operations/`. The trend store is a git-tracked, append-only
NDJSON file. Use no broker, database, or hosted service. Adding one requires
measured need: a named query or fan-out load, with numbers, that flat files
cannot serve. Baselines and thresholds move only by ratchet
(`global/references/quality-gates.md`): committed, reasoned, never lowered to
create a pass.

## Completion Gate

`global/references/verification-system-first.md` defines the shared proof
contract. This loop adds:

- **Run record:** `run.json` and the trend row are written; every key field is
  present; missing data is explicit with a reason, never absent.
- **Findings:** every finding is evidence-backed; every remediated finding was
  re-verified live by an independent lane.
- **Trend:** the report names regression, improvement, variance, and missing
  data against prior rows, or names the empty history.

A run whose trend row is unwritten is not complete. Subagent confidence is not
evidence.
