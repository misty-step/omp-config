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
| Every-project floor, faces, onboarding, factory surfaces | `skill://foundation` |
| Broad architecture reshape toward a goal | `skill://refactor` + `skill://prune` |
| Single frozen-range review | `skill://code-review` |
| Persona browser QA | `skill://qa-users` |
| Live smoke of one claim | `skill://verify-live` |

Do not run `/quality` as a second foundation scorecard.
Do not load every domain reference "just in case".

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

Reject a missing or unknown domain.

## Select the mode

- Default `full`: steps 1–6.
- `--audit-only`: stop after assess.
- `--remediate`: load latest assessment; remediate + verify accepted findings.
- `--verify`: independent proof only for remediated findings.
- `--trends`: operations only; recompute trends without a new audit.

## Ratchet program

1. **Scope.** Repo, revision, dirty state, domain, mode. Inventory required surfaces.
2. **Target.** Freeze measurable targets and falsifiers before judgment.
3. **Audit.** Dispatch read-only `researcher`, `verifier`, or `designer` lanes as the domain directs.
4. **Assess.** Write `.evidence/quality/<domain>/assessment.json`. Validate with
   `python3 "${PI_CODING_AGENT_DIR:-$HOME/.omp/agent}/skills/quality/scripts/validate-assessment.py" <assessment.json>`,
   then render `assessment.md`. Each finding: `remediate` | `waive` | `defer` | `reject`.
5. **Remediate.** `builder` slices for `remediate` findings. Preserve strengths.
6. **Verify.** Fresh non-mutating `verifier` (or `designer` for rendered design).

A finding without evidence is not a finding.
Weakening a gate is not remediation.

## Completion Gate

Apply `global/references/verification-system-first.md` and `references/assessment.md`.
Report domain, mode, assessment paths, findings by decision, exact proof,
preserved strengths, blockers, residual risk.
