# /vision eval waiver

expires: 2026-09-15

## Reason

The skill uses conversational, multi-turn interrogation to produce VISION.md. A
single scripted fixture cannot replay the back-and-forth faithfully. It needs a
human-anchor design, the same class as multi-model skill-eval runs.

## Disposition

This skill is not exempt from the eval-coverage contract. This waiver is a
time-boxed deferral, not a permanent opt-out. When it expires, either land an
eval spec at `global/skills/vision/evals/vision-eval.md` (see
`global/skills/skill-eval/templates/eval-spec.md`) or renew this waiver with a
fresh reason and date. A stale, silently renewed waiver with no new reasoning is
itself a finding for `/harness-engineering`'s next skill-health audit.

No automated eval exists. Revisit when this skill changes. Per-skill proof runs
through `/skill-eval`.
