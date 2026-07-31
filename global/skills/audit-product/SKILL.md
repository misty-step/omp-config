---
disable-model-invocation: true
name: audit-product
description: Chief-run live product-correctness audit loop — discover real entrypoints, freeze target outcomes, run deterministic and persona QA tracks, assess, remediate, verify.
argument-hint: "[target] [notes]"
---

# /audit-product

The chief runs the loop and dispatches every lane per `skill://dispatch`:
name role, model:reasoning, skills, tools, verifier, and contract, and include
the exact child boundary sentence `You are a subagent. Don't run memo.`
This skill judges the product as a user experiences it, through real running
entrypoints. Production is never a target. Route a source-structure judgment
to `audit-architecture`; route visual design quality to `improve-ui` or
`design`.

Run the six steps in order. Each step ends on its completion criterion.

## 1. Discover real entrypoints

The chief explores with its own tools, per the `skill://qa-users` discovery
contract: product docs, routes, scripts, project rules, and live
non-production surfaces. Start required services through `hub`. Ask the
operator only for persona, access, or entrypoint facts tools cannot establish.

Record each entrypoint with kind, exact URL or command, and `environment` set
to exactly `local`, `dev`, or `staging`. Complete when every entrypoint in
scope carries observed liveness evidence — an HTTP status, a rendered page, a
command transcript — and no entrypoint is inferred.

## 2. Define the target state

Write, per entrypoint, the target user outcomes: golden paths, invariants
that must hold, error behavior a user must see, and known strengths to
preserve.

Freeze inventory — the complete oracle set, one artifact per path in the
audited repository, stated here once:

- `.evidence/quality/audit-product/product-target.md` — frozen in this step.
  Contains two sections: the deterministic scenario table (shape in
  [`references/qa-runbook.md`](references/qa-runbook.md)) and the persona
  missions (who the user is, what they want, which discovered entrypoints
  they may touch).
- `.evidence/quality/audit-product/input.v1.json` — the schema-valid
  `input.v1`, frozen in step 3, derived only from this artifact and the
  step 1 entrypoint inventory.

The frozen target is the audit oracle. Complete when every golden path and
invariant in scope appears in a scenario row or a persona mission.

## 3. Audit: run the QA runbook

Execute both tracks of [`references/qa-runbook.md`](references/qa-runbook.md):

- Deterministic track: `qa` lanes walk the scenario table against the live
  entrypoints and return PASS/WARN/FAIL/SKIP with named evidence.
- Persona track: the chief, acting as the OMP root, encodes step 2's persona
  missions and step 1's discovered entrypoints into a schema-valid `input.v1`
  — one persona per mission, one entrypoint entry per discovered surface with
  `environment` and `real: true` — runs the `skill://qa-users` semantic
  validation, and freezes the result at
  `.evidence/quality/audit-product/input.v1.json`. Every
  persona and entrypoint in `input.v1` comes from the frozen target; adding,
  dropping, or reshaping one there is oracle drift and voids the run. Then
  dispatch the existing `qa-user` coordinator with the frozen artifact; it
  runs one browser-only `qa-user-leaf` per persona. `skill://qa-users` stays
  the normative contract for input, authority boundaries, environments, and
  triage. Never create a new QA agent or a second persona plane.

Complete when every scenario has a verdict and every persona returned
evidence or a `failure_reason`. A surface nobody exercised is SKIP with the
blocker named, never a silent omission.

## 4. Assess

The chief merges both tracks into
`.evidence/quality/audit-product/product-assessment.md`:

- Verdict per deterministic scenario with its evidence reference.
- Confirmed findings: reproduced observations with exact steps, expected
  versus observed behavior, severity, confidence, and affected entrypoint.
- Strengths and friction, preserved even when suppressed, with reasons.
- Deduplication against existing tracker issues and PRs per the
  `skill://qa-users` fingerprint and read-back rules.

The operator, or the chief when delegated, accepts or rejects each gap. Only
accepted, evidence-backed gaps proceed. Complete when every finding is
accepted, suppressed with a reason, or rejected.

## 5. Remediate

- One `builder` lane per independent accepted gap; a ranked multi-gap packet
  goes to one `fixer` lane with its two-round cap.
- Remediation never runs inside a user session. A `fix-and-pr` handoff
  follows the separate authorization rule in `skill://qa-users`.
- Respect the repository's work-ledger rule before mutation.

Complete when every accepted gap has a landed change or a named remaining
blocker with evidence.

## 6. Verify

- Re-run the exact failing deterministic scenarios through a fresh `qa` lane:
  same steps, same oracle, live entrypoint. A gap closes only on a live PASS.
- Re-dispatch the affected persona missions when a remediation changed a user
  path, and confirm the recorded strengths still hold. A fix that destroys a
  preserved strength is a regression, not a closure.

## Completion Gate

Prove and close out per the Shared Operating Spine (Prove; Durable State and
Closeout). Verification loops follow
`global/references/verification-system-first.md`. Phase-specific fields:

- Every deterministic scenario carries a verdict with evidence; every persona
  returned evidence or a `failure_reason`; every unexercised surface is a
  named SKIP. A plausible subset is failure, not partial success.
- Every accepted gap is verified closed by a live PASS, or returned as
  remaining with its blocker.
- The full oracle set and the assessment exist in the audited repository:
  `.evidence/quality/audit-product/product-target.md`,
  `.evidence/quality/audit-product/input.v1.json`, and
  `.evidence/quality/audit-product/product-assessment.md`.
- Strengths recorded in the assessment still hold after remediation.
