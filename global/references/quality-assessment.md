# Quality Assessment Contract

Durable output contract for audit-assess-remediate programs
(`quality-toolchain`, `quality-tests`, and future siblings).
One assessment is one machine-readable JSON file plus one human-readable
Markdown twin generated from the same data. The assessment is the program's
memory: audits, decisions, remediation, and verification all read and write it.

## Location and durability

- Write `.evidence/quality/<program>/assessment.json` and `assessment.md` in
  the audited repository. `<program>` is the program id exactly —
  `quality-toolchain` or `quality-tests` — never a shortened slug.
- Commit both unless repository policy forbids; then publish them as CI
  artifacts and record the artifact path in the run report.
- Assessments ratchet. A new assessment carries every unresolved prior finding
  forward or resolves it with a decision. A silently dropped finding is gate
  weakening, not progress.

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
      {
        "surface": "lint",
        "present": true,
        "detail": "eslint flat config, no max-warnings bound",
        "paths": ["eslint.config.js"]
      },
      {
        "surface": "hooks.pre-push",
        "present": false,
        "detail": "no pre-push hook configured",
        "paths": []
      }
    ]
  },
  "targets": [
    {
      "id": "lint.strict",
      "surface": "lint",
      "statement": "warnings are errors on changed code",
      "failure_mode": "silent quality drift lands on master",
      "source": "global/references/quality-gates.md"
    },
    { "id": "types.strict", "surface": "types", "statement": "mypy --strict on changed code", "failure_mode": "type holes ship unchecked", "source": "references/target-state.md" },
    { "id": "build.locked", "surface": "build", "statement": "base images and dependencies pinned", "failure_mode": "unreproducible builds", "source": "references/target-state.md" }
  ],
  "not_applicable": [
    { "surface": "torture", "reason": "short-lived batch CLI, no accumulated state" }
  ],
  "findings": [
    {
      "id": "F-001",
      "target": "lint.strict",
      "severity": "high",
      "observed": "eslint runs with --max-warnings=infinity",
      "evidence": [
        {
          "command": "npx eslint . --max-warnings 0",
          "exit_code": 1,
          "artifact": ".evidence/quality/quality-toolchain/lint-run.txt"
        }
      ],
      "decision": "remediate",
      "waiver": null,
      "ticket": null,
      "remediation": {
        "change": "zero-warning on changed files, baseline ratchet for legacy",
        "verified_by": "gate lint.fast exit 0 + seeded violation exit 1"
      }
    },
    {
      "id": "F-002",
      "target": "types.strict",
      "severity": "med",
      "observed": "legacy module fails mypy --strict",
      "evidence": [
        {
          "command": "mypy --strict legacy/",
          "exit_code": 1,
          "artifact": ".evidence/quality/quality-toolchain/mypy-legacy.txt"
        }
      ],
      "decision": "waive",
      "waiver": {
        "reason": "legacy module scheduled for deletion",
        "approver": "operator",
        "expires": "2026-10-31"
      },
      "ticket": null,
      "remediation": null
    },
    {
      "id": "F-003",
      "target": "build.locked",
      "severity": "low",
      "observed": "dev image pulls an unpinned base",
      "evidence": [
        {
          "command": "grep -n FROM Dockerfile.dev",
          "exit_code": 0,
          "artifact": ".evidence/quality/quality-toolchain/docker-base.txt"
        }
      ],
      "decision": "defer",
      "waiver": null,
      "ticket": "POWDER-1234",
      "remediation": null
    }
  ],
  "gates": [
    {
      "id": "lint.fast",
      "command": "npm run lint:changed",
      "tier": "fast",
      "report": ".evidence/quality/quality-toolchain/lint-run.txt",
      "exit_code": 0,
      "seed": null,
      "falsifier_verified": true
    }
  ]
}
```

Field rules:

- `targets[].failure_mode` is mandatory. A target that names no real failure
  is deleted, not audited.
- `findings[].evidence` is mandatory and non-empty. A finding with no command
  transcript or file path is a declaration, not a finding.
- `gates[].falsifier_verified` is true only after a seeded violation made the
  gate fail during verification.
- `inventory.surfaces[]` holds every phase-1 fact, absences included
  (`present: false`). Later phases audit only surfaces the inventory names.
- `findings[].waiver` (`reason`, `approver`, `expires`) is required exactly
  when `decision` is `waive`; otherwise null.
- `findings[].ticket` is a work-ledger reference, required exactly when
  `decision` is `defer`; otherwise null.
- `gates[]` is also the machine home for verification runs: suite and gate
  transcripts go in `report`, the disclosed seed in `seed` (null for seedless
  runs), and seeded-bug or seeded-violation results in `falsifier_verified`.

## Decisions

Every finding carries exactly one decision:

- **remediate** — accepted; closes only with a diff and a verifying gate run.
- **waive** — carries reason, approver, and expiry date. An expired waiver is
  an open finding on the next assessment.
- **defer** — carries a ticket reference in the repository's work ledger.

Contested or product-scope decisions go to the operator. The program never
invents approval.

## Human-readable twin

`assessment.md` renders the same data: summary counts by severity and
decision, the targets table, findings grouped by surface with evidence links,
the gates table with commands, seeds, and last exit codes, and waivers with
approver and expiry.
Another agent must be able to judge every claim from the packet without chat
context (`global/references/verification-system-first.md`).
