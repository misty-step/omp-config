# Quality Assessment Contract

Durable output contract for quality programs (`audit-quality-controls`, `quality-toolchain`, `quality-tests`, and future siblings).
One assessment contains one machine-readable JSON file and one human-readable Markdown twin, generated from the same data.
The assessment stores audits, decisions, remediation, and verification; every phase reads and writes it.
Gate definitions and proof rules live in `global/references/quality-gates.md`.

## Location and durability

- Write `.evidence/quality/<program>/assessment.json` and `assessment.md` in the audited repository.
- Use the exact program id: `audit-quality-controls`, `quality-toolchain`, or `quality-tests`.
- Commit both unless repository policy forbids it; then publish CI artifacts and record each artifact path in the run report.
- Assessments ratchet. Carry every unresolved prior finding forward or resolve it with a decision. A silently dropped finding weakens the gate; it is not progress.

## Machine-readable shape

```json
{
  "schema_version": "omp.quality-assessment.v1",
  "program": "quality-toolchain",
  "repository": "git@github.com:org/repo.git",
  "revision": "<commit sha audited>",
  "generated_at": "2026-07-30T00:00:00Z",
  "inventory": {
    "surfaces": [
      {"surface": "lint", "present": true, "detail": "eslint flat config, no max-warnings bound", "paths": ["eslint.config.js"]},
      {"surface": "hooks.pre-push", "present": false, "detail": "no pre-push hook configured", "paths": []}
    ]
  },
  "targets": [
    {"id": "lint.strict", "surface": "lint", "statement": "warnings are errors on changed code", "failure_mode": "silent quality drift lands on master", "source": "global/references/quality-gates.md"},
    {"id": "types.strict", "surface": "types", "statement": "mypy --strict on changed code", "failure_mode": "type holes ship unchecked", "source": "references/target-state.md"},
    {"id": "build.locked", "surface": "build", "statement": "base images and dependencies pinned", "failure_mode": "unreproducible builds", "source": "references/target-state.md"}
  ],
  "not_applicable": [
    {"surface": "torture", "reason": "short-lived batch CLI, no accumulated state"}
  ],
  "findings": [
    {
      "id": "F-001", "target": "lint.strict", "severity": "high",
      "observed": "eslint runs with --max-warnings=infinity",
      "evidence": [{"command": "npx eslint . --max-warnings 0", "exit_code": 1, "artifact": ".evidence/quality/quality-toolchain/lint-run.txt"}],
      "decision": "remediate", "waiver": null, "ticket": null,
      "remediation": {"change": "zero-warning on changed files, baseline ratchet for legacy", "verified_by": "gate lint.fast exit 0 + seeded violation exit 1"}
    },
    {
      "id": "F-002", "target": "types.strict", "severity": "med",
      "observed": "legacy module fails mypy --strict",
      "evidence": [{"command": "mypy --strict legacy/", "exit_code": 1, "artifact": ".evidence/quality/quality-toolchain/mypy-legacy.txt"}],
      "decision": "waive",
      "waiver": {"reason": "legacy module scheduled for deletion", "approver": "operator", "expires": "2026-10-31"},
      "ticket": null, "remediation": null
    },
    {
      "id": "F-003", "target": "build.locked", "severity": "low",
      "observed": "dev image pulls an unpinned base",
      "evidence": [{"command": "grep -n FROM Dockerfile.dev", "exit_code": 0, "artifact": ".evidence/quality/quality-toolchain/docker-base.txt"}],
      "decision": "defer", "waiver": null, "ticket": "POWDER-1234", "remediation": null
    }
  ],
  "gates": [
    {"id": "lint.fast", "command": "npm run lint:changed", "tier": "fast", "report": ".evidence/quality/quality-toolchain/lint-run.txt", "exit_code": 0, "seed": null, "falsifier_verified": true}
  ]
}
```

## Field rules

- `targets[].failure_mode` is mandatory. Delete a target with no real failure; do not audit it.
- `findings[].evidence` is mandatory and non-empty. A finding without a command transcript or file path is a declaration, not a finding.
- Set `gates[].falsifier_verified` true only after a seeded violation makes the gate fail during verification.
- `inventory.surfaces[]` holds every phase-1 fact, including absences (`present: false`). Later phases audit only named surfaces.
- Require `findings[].waiver` (`reason`, `approver`, `expires`) exactly when `decision` is `waive`; otherwise set it to null.
- Require `findings[].ticket` as a work-ledger reference exactly when `decision` is `defer`; otherwise set it to null.
- Use `gates[]` as the machine home for verification runs: put suite and gate transcripts in `report`, the disclosed seed in `seed` (null for seedless runs), and seeded-bug or seeded-violation results in `falsifier_verified`.

## Decisions

Every finding carries exactly one decision:

- **remediate** — accept it; close it only with a diff and a verifying gate run.
- **waive** — carry a reason, approver, and expiry date. An expired waiver becomes an open finding on the next assessment.
- **defer** — carry a ticket reference in the repository's work ledger.

Send contested or product-scope decisions to the operator. The program never invents approval.

## Human-readable twin

`assessment.md` renders the same data: summary counts by severity and decision; the targets table; findings grouped by surface with evidence links; the gates table with commands, seeds, and last exit codes; and waivers with approver and expiry.
Another agent must judge every claim from the packet without chat context (`global/references/verification-system-first.md`).
