---
disable-model-invocation: true
name: quality
description: Ratchet one repository quality domain through evidence, decisions, repair, and independent proof.
argument-hint: "[controls|toolchain|tests|operations|architecture|product|design] [--audit-only|--remediate|--verify|--trends] [target]"
---

# /quality

Ratchet one selected domain from observed state to an explicit target. Keep the shared program here. Load only the selected domain reference.

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

Reject a missing or unknown domain. Do not load the other domain references.

## Select the mode

- Default `full`: run all six steps.
- `--audit-only`: stop after step 4. Execute no remediation.
- `--remediate`: load the latest assessment, then run steps 5 and 6 for findings with decision `remediate`.
- `--verify`: load the latest assessment, then run step 6 for remediated findings.
- `--trends`: use only with `operations`. Recompute its trend report without an audit or new run record.

## Ratchet program

1. **Scope.** Record the repository, revision, dirty state, selected domain, mode, and governing instructions. Load the domain reference. Complete when every required inventory surface has evidence or an explicit missing reason.
2. **Target.** Freeze measurable target claims before judgment. Each target names its failure mode and a credible falsifier. Complete when every inventoried surface has a selected target, a reasoned refusal, or a not-applicable decision.
3. **Audit.** Dispatch read-only `researcher`, `verifier`, or `designer` lanes as the domain reference directs. Give each lane the target, oracle, scope, and evidence contract. Complete when every selected target has `pass`, `gap`, or `missing` evidence.
4. **Assess.** Write `.evidence/quality/<domain>/assessment.json` first. Run `python3 "${PI_CODING_AGENT_DIR:-$HOME/.omp/agent}/skills/quality/scripts/validate-assessment.py" <assessment.json>`, then render `assessment.md` from the same data. Complete when validation passes and every finding has one decision: `remediate`, `waive`, `defer`, or `reject`.
5. **Remediate.** Give accepted findings to `builder` by independent slice or as one ranked packet with a two-round cap. Preserve every target and strength. Complete when each `remediate` finding has a landed change or an evidence-backed blocker.
6. **Verify.** Use a fresh, non-mutating `verifier`, or use `designer` for rendered design proof. Re-run the original falsifier and repaired path. Complete when every remediated finding has independent evidence and every preserved strength still holds.

## Shared decisions

- `remediate`: repair the gap now.
- `waive`: record the reason, approver, and expiry date.
- `defer`: record a durable ticket.
- `reject`: record why the evidence does not justify change.

A finding without evidence is not a finding. A remediation without independent proof remains open. A weaker gate, threshold, test, or target is not remediation.

## Completion Gate

Apply `global/references/verification-system-first.md` and `references/assessment.md`. Report the selected domain, mode, assessment paths, audited revision, findings by decision, exact proof, preserved strengths, blockers, and residual risk.
