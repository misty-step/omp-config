# /harness-engineering eval waiver

expires: 2026-08-30

## Reason

This self-referential meta-skill builds and audits the skill catalog's own eval
coverage, including this waiver pass.
Author fixtures outside the working session to avoid circularity.

## Disposition

This waiver is not exempt from the eval-coverage contract.
It is a time-boxed deferral, not a permanent opt-out.
Before it expires, add an eval spec at
`global/skills/harness-engineering/evals/harness-engineering-eval.md`.
Use `global/skills/skill-eval/templates/eval-spec.md`.
Otherwise, renew this waiver with a fresh reason and date.
A stale waiver that renews silently without new reasoning is itself a finding
for `/harness-engineering`'s next skill-health audit.

No automated eval exists; revisit this when the skill changes.
Per-skill proof runs through `/skill-eval`.
