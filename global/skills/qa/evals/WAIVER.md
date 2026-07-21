# /qa eval waiver

expires: 2026-08-30

## Reason

Highly app-shape-dependent (browser walk vs API replay vs CLI smoke vs library build); no single small fixture app exists in-repo yet to drive every route through.

## Disposition

Not exempt from the eval-coverage contract — this waiver is a time-boxed
deferral, not a permanent opt-out. When it expires, either an eval spec lands
at `global/skills/qa/evals/qa-eval.md` (see `global/skills/skill-eval/templates/eval-spec.md`)
or this waiver is renewed with a fresh reason and date. A stale, silently
renewed waiver with no new reasoning is itself a finding for `/harness-engineering`'s
next skill-health audit.

No automated eval; origin Roster-era backlog (retired 2026-07-16); revisit when this skill changes. Per-skill proof runs through `/skill-eval`.
