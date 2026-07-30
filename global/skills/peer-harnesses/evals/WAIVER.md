# /peer-harnesses eval waiver

expires: 2026-08-01

## Reason

This skill maps peer-CLI capability and routing. Its falsifiable claim is routing
correctness. The claim matches the proven routing-eval pattern
(`global/skills/skill-eval/examples/routing-eval.md`, run 15/15 while it lived
in `/design`). Adapt that harness with a peer-harness-specific answer key.

## Disposition

This waiver is not exempt from the eval-coverage contract. It defers coverage
for a limited time. Before it expires, add an eval spec at
`global/skills/peer-harnesses/evals/peer-harnesses-eval.md` (see
`global/skills/skill-eval/templates/eval-spec.md`), or renew this waiver with a
new reason and date. Treat a stale waiver without new reasoning as a finding
for `/harness-engineering`'s next skill-health audit.

No automated eval exists. Revisit when this skill changes. Run per-skill proof
through `/skill-eval`.
