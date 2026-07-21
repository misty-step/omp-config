# /next eval waiver

expires: 2026-08-01

## Reason

First proof exists but is not yet a committed eval spec: the 2026-07-21 skill null-case sweep A/B-tested `/next` (skill-on vs bare prompt, blind rubric grading) and it won 2 of 3 fixtures — verdict keep. Evidence: `~/Development/crucible/runs/local/skill-null-sweep/report.md`. The original plan to reuse `/orient`'s fixture harness is void: that same sweep cut `/orient`. Remaining work is porting the sweep fixtures into a durable spec here.

## Disposition

Not exempt from the eval-coverage contract — this waiver is a time-boxed
deferral, not a permanent opt-out. When it expires, either an eval spec lands
at `global/skills/next/evals/next-eval.md` (see `global/skills/skill-eval/templates/eval-spec.md`)
or this waiver is renewed with a fresh reason and date. A stale, silently
renewed waiver with no new reasoning is itself a finding for `/harness-engineering`'s
next skill-health audit.

No automated eval; origin Roster-era backlog (retired 2026-07-16); revisit when this skill changes. Per-skill proof runs through `/skill-eval`.
