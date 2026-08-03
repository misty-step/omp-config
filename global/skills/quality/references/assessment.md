# Quality assessment contract

Write machine data first to `.evidence/quality/<domain>/assessment.json`. Run `python3 "${PI_CODING_AGENT_DIR:-$HOME/.omp/agent}/skills/quality/scripts/validate-assessment.py" <assessment.json>`. Render `assessment.md` from the same data.

## Ratchet rules

- Record the audited repository, revision, dirty state, mode, and selected domain.
- Account for every required inventory surface, including absent surfaces.
- Give every target a failure mode and falsifier, or refuse it with a reason.
- Give every finding non-empty evidence and one decision.
- Carry unresolved findings into the next assessment. Resolve them with proof or keep them open.
- Store domain-only data in `domain_data`. Do not change the shared fields.

## Decisions

| Decision | Required data |
|---|---|
| `remediate` | remediation change or blocker after execution |
| `waive` | reason, approver, and expiry date |
| `defer` | durable ticket |
| `reject` | evidence-based rejection reason |

The operator decides contested product scope. A delegated chief may decide within accepted authority. The program never invents approval.

## Markdown twin

Render these sections from the JSON data:

1. Run identity and selected target.
2. Inventory with explicit absences.
3. Targets, failure modes, falsifiers, and selection status.
4. Findings grouped by decision with evidence links.
5. Remediation and independent verification.
6. Preserved strengths.
7. Blockers and residual risk.

The Markdown twin must not add or omit a finding. On a mismatch, repair the JSON first and render again.
