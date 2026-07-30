# /refactor eval waiver

expires: 2026-08-30

## Reason

This waiver needs a seeded, nontrivial messy-codebase fixture with a live-test loop.
Authoring one fixture large enough to stress the three-altitude claim remains open.

## Disposition

Do not treat this waiver as exempt from the eval-coverage contract.
This waiver defers the eval for a fixed time.
It does not provide a permanent opt-out.
When it expires, add an eval spec at `global/skills/refactor/evals/refactor-eval.md`.
See `global/skills/skill-eval/templates/eval-spec.md`.
Otherwise, renew this waiver with a new reason and date.
A stale waiver that renews without new reasoning is itself a finding for `/harness-engineering`'s next skill-health audit.

Run no automated eval until this skill changes.
Per-skill proof runs through `/skill-eval`.
