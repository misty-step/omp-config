---
disable-model-invocation: true
name: quality
description: |
  Ratchet one repository quality domain through evidence, decisions, repair,
  and independent proof. Not a substitute for /foundation (floor) or /refactor
  (architecture rewrite). Trigger: /quality.
argument-hint: "[controls|toolchain|tests|operations|architecture|product|design] [--audit-only|--remediate|--verify|--trends] [target]"
---

# /quality

Ratchet **one** selected domain from observed state to an explicit target.
Keep the shared program here. Load only the selected domain reference.

## Boundaries

| Need | Use instead |
|---|---|
| Every-project floor, faces, onboarding, factory surfaces | `/foundation` |
| Broad architecture reshape toward a goal | `/refactor` + `/prune` |
| Single frozen-range review | `/code-review` |
| Persona browser QA | `/qa-users` |
| Live smoke of one claim | `/verify-live` |

Do not run `/quality` as a second foundation scorecard.

## Select the domain

| Domain | Load when selected |
|---|---|
| `controls` | `references/controls.md` |
| `toolchain` | `references/toolchain.md` |
| `tests` | `references/tests.md` |
| `operations` | `references/operations.md` |
| `architecture` | `references/architecture.md` |
| `product` | `references/product.md` |
| `design` | `references/design.md` |

Reject a missing or unknown domain. Do not load other domain references.

## Select the mode

- Default `full`: steps 1–6.
- `--audit-only`: stop after step 4.
- `--remediate`: load latest assessment; run steps 5–6 for `remediate` findings.
- `--verify`: run step 6 for remediated findings.
- `--trends`: operations only; recompute trends without a new audit.

## Ratchet program

1. **Scope.** Record repo, revision, dirty state, domain, and mode. Load the domain reference.
   Done when every required inventory surface has evidence or an explicit missing reason.
2. **Target.** Freeze measurable targets and falsifiers before judgment.
   Done when every inventoried surface has a selected target, reasoned refusal, or n/a.
3. **Audit.** Dispatch read-only `researcher`, `verifier`, or `designer` lanes as the domain directs.
   Done when every selected target has `pass`, `gap`, or `missing` evidence.
4. **Assess.** Write `.evidence/quality/<domain>/assessment.json`. Run
   `python3 "${PI_CODING_AGENT_DIR:-$HOME/.omp/agent}/skills/quality/scripts/validate-assessment.py" <assessment.json>`,
   then render `assessment.md`.
   Done when validation passes and every finding has one decision:
   `remediate` | `waive` | `defer` | `reject`.
5. **Remediate.** Give `remediate` findings to `builder` by independent slice.
   Done when each has a landed change or evidence-backed blocker.
6. **Verify.** Fresh non-mutating `verifier` (or `designer` for rendered design).
   Done when every remediated finding has independent evidence and preserved strengths hold.

A finding without evidence is not a finding. Weakening a gate is not remediation.

## Completion Gate

Apply `global/references/verification-system-first.md` and `references/assessment.md`.
Report domain, mode, assessment paths, findings by decision, exact proof,
preserved strengths, blockers, and residual risk.
