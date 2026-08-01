---
disable-model-invocation: true
name: audit-product
description: Chief-run live product audit: discover entrypoints, freeze outcomes, run QA, assess, remediate, and verify.
argument-hint: "[target] [notes]"
---

# /audit-product

Dispatch through `skill://dispatch`. Name role, model:reasoning, skills, tools,
verifier, and contract. Include the exact child boundary sentence
`You are a subagent. Don't run memo.`
Judge real entrypoints; never target production. Route source structure to
`audit-architecture`; route visual quality to `improve-ui` or `design`.

## Audit spine

1. **Discover real entrypoints.** Under `skill://qa-users`, inspect docs, routes, scripts, rules, and live non-production surfaces; start via `hub`; ask only for unavailable persona, access, or entrypoint facts. Record kind, exact URL or command, and `environment` exactly `local`, `dev`, or `staging`. Require HTTP status, rendered page, or command transcript. Never infer.
2. **Define target.** Record each entrypoint's golden paths, invariants, user-visible errors, and strengths. Freeze:
   - `.evidence/quality/audit-product/product-target.md`: [`references/qa-runbook.md`](references/qa-runbook.md) scenario table plus persona missions (user, goal, reachable entries).
   - `.evidence/quality/audit-product/input.v1.json`: schema-valid `input.v1`, freeze in step 3, derive only from target and step 1 inventory.
   Put every golden path and invariant in a scenario row or mission. The target is the oracle.
3. **Audit.** Run both [`references/qa-runbook.md`](references/qa-runbook.md) tracks:
   - Deterministic: `qa` runs each scenario live and returns `PASS`, `WARN`, `FAIL`, or `SKIP` with named evidence.
   - Persona: the OMP root encodes step 2 missions and step 1 entries in `input.v1`: one persona per mission and one entry per surface, with `environment` and `real: true`. Validate and freeze with `skill://qa-users`. Any addition, drop, or reshape voids the run. The existing `qa-user` coordinator runs one browser-only `qa-user-leaf` per persona from the artifact. Its contract governs input, authority boundaries, environments, and triage. Never create another QA agent or persona plane.
   Require every scenario verdict and every persona evidence or `failure_reason`. Mark an unexercised surface `SKIP` with its blocker.
4. **Assess.** Merge tracks into `.evidence/quality/audit-product/product-assessment.md`. Record scenario verdict/evidence; findings: steps, expected/observed behavior, severity/confidence, and entrypoint; strengths, friction, and suppression reasons. Deduplicate tracker issues/PRs with `skill://qa-users` fingerprint/read-back. Have the operator or delegated chief accept, suppress with reason, or reject each finding. Only accepted evidence-backed gaps proceed.
5. **Remediate.** Route independent gaps to `builder`; a ranked packet to `fixer` with a two-round cap. Never mutate in a user session. Apply `fix-and-pr` authorization in `skill://qa-users`; respect the work-ledger rule. Require landed change or blocker evidence.
6. **Verify.** A fresh `qa` reruns each failing scenario with the same steps, oracle, and live entrypoint; close on live `PASS`. Redispatch personas for changed paths. A destroyed strength is a regression, not closure.

## Completion Gate

Follow the Shared Operating Spine and `global/references/verification-system-first.md`.
- Gate: every scenario has verdict/evidence; every persona has evidence or `failure_reason`; every unexercised surface has `SKIP` and a blocker. A plausible subset fails.
- Verify every accepted gap with live `PASS` evidence or a named blocker.
- Keep the three artifacts named above. Confirm strengths still hold.
