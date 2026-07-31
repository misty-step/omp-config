# /quality-operations eval waiver

expires: 2026-09-15

## Reason

This skill is an operator-invoked, multi-domain live loop. One run dispatches
inventory, audit, remediation, and verification lanes against a real
repository with real monitors, runbooks, and staging surfaces. A useful eval
needs a fixture repository with a seeded `.evidence/quality-operations/`
store, a fake monitor surface, and at least one intentionally broken domain.
Without those fixtures, the eval only tests whether the model repeats the
loop prose.

## Disposition

This skill is not exempt from the eval-coverage contract. When the waiver
expires, add an eval with a fixture repository containing a seeded trend
store and two planted gaps (a missing health probe, a stale runbook). Grade:
the run record validates against `references/run-artifact.md`, both gaps
appear as evidence-backed findings, the trend row is appended, and the
missing-data and verdict-cap rules hold.

Until then, use the schema examples in `references/run-artifact.md` as the
falsifier — they must stay parseable — and the omp-config gate for
frontmatter shape and config-contract integrity:

```bash
bin/check
```
