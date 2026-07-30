# /groom eval waiver

expires: 2026-08-30

## Reason

Backlog scope is nondeterministic by design because it follows the live backlog.
An objective grader needs a frozen backlog fixture with a known-good target diff.
Author the fixture and diff before grading.

## Disposition

This waiver remains subject to the eval-coverage contract.
Treat it as a time-boxed deferral, not a permanent opt-out.
When it expires, add an eval spec at
`global/skills/groom/evals/groom-eval.md` (see
`global/skills/skill-eval/templates/eval-spec.md`) or renew this waiver with a
fresh reason and date.
Treat a waiver that is stale, silently renewed, and lacks new reasoning as a
finding for `/harness-engineering`'s next skill-health audit.

Do not run an automated eval. Revisit when this skill changes.
Run per-skill proof through `/skill-eval`.
