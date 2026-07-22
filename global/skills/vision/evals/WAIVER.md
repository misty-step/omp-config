# /vision eval waiver

expires: 2026-09-15

## Reason

Conversational, multi-turn interrogation to produce VISION.md; a single scripted fixture can't faithfully replay the back-and-forth. Needs a human-anchor design, same class as `council`.

## Disposition

Not exempt from the eval-coverage contract — this waiver is a time-boxed
deferral, not a permanent opt-out. When it expires, either an eval spec lands
at `global/skills/vision/evals/vision-eval.md` (see `global/skills/skill-eval/templates/eval-spec.md`)
or this waiver is renewed with a fresh reason and date. A stale, silently
renewed waiver with no new reasoning is itself a finding for `/harness-engineering`'s
next skill-health audit.

No automated eval; origin Roster-era backlog (retired 2026-07-16); revisit when this skill changes. Per-skill proof runs through `/skill-eval`.
