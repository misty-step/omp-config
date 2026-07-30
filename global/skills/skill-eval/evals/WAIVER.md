# /skill-eval eval waiver

expires: 2026-09-29

## Reason

Bootstrapping problem: This meta-skill authors every other skill's eval in this
pass. Its claim is proven empirically by the catalog-wide loop it produces.
Defer formal self-eval until the loop completes at least one full pass.

## Disposition

This skill is not exempt from the eval-coverage contract. This waiver is a
time-boxed deferral, not a permanent opt-out. When it expires, either land an
eval spec at `global/skills/skill-eval/evals/skill-eval-eval.md` (see
`global/skills/skill-eval/templates/eval-spec.md`) or renew this waiver with a
fresh reason and date. A stale, silently renewed waiver with no new reasoning is
itself a finding for `/harness-engineering`'s next skill-health audit.

No automated eval exists. Revisit when this skill changes. Per-skill proof runs
through `/skill-eval`.
