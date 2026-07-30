# Assessment template

The assessment is the durable record of one audit-assess-remediate program.
Write it to `design-plans/design-audit/ASSESSMENT.md` in the audited repository.
Update the same file across phases; never fork a second assessment.

```markdown
# Design audit assessment — <product>

- Date started:
- Audited surfaces:
- Entrypoints exercised: <url — environment — start command>
- Target state: <DESIGN.md path and commit>
- Target-state scan: <pass | rejected — reason | not external>
- Named references consulted: <app — flow — pattern learned>

## Findings

| # | Phase | Surface | Problem | Evidence | Governing rule | Correction | Decision | Verdict |
|---|---|---|---|---|---|---|---|---|

## Evidence index

<path — width — what it shows>, one line per screenshot or artifact.

## Remediation record

| # | Change | Files | Landed change id | Evidence |
|---|---|---|---|---|

## Remaining

<gap — reason it remains>, or `None`.
```

Column rules:

- `Phase` is `source` or `rendered`.
- `Evidence` names a file path or session screenshot; a finding without evidence is deleted.
- `Governing rule` cites the `DESIGN.md` section or contract rule the finding violates.
- `Correction` states one change; a finding needing two corrections becomes two findings.
- `Decision` is `accepted`, `rejected`, or `deferred`, set by the operator.
- `Verdict` is `verified` or `remaining`, set only by the verify phase with named evidence.

When a phase does not apply — for example, no rendered surface exists — record `N/A` with the reason instead of deleting the section.
