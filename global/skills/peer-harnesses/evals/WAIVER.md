# /peer-harnesses eval waiver

expires: 2026-08-01

## Reason

Reference/routing skill (peer-CLI capability map). The falsifiable claim is routing correctness, structurally identical to the already-proven routing-eval pattern (`primitives/skills/skill-eval/examples/routing-eval.md`, run 15/15 while it lived in `/design`) — next in line to adapt that harness with a peer-harness-specific answer key.

## Disposition

Not exempt from the eval-coverage contract — this waiver is a time-boxed
deferral, not a permanent opt-out. When it expires, either an eval spec lands
at `primitives/skills/peer-harnesses/evals/peer-harnesses-eval.md` (see `primitives/skills/skill-eval/templates/eval-spec.md`)
or this waiver is renewed with a fresh reason and date. A stale, silently
renewed waiver with no new reasoning is itself a finding for `/harness-engineering`'s
next skill-health audit.

Tracked by Powder `workbench-003`; per-skill proof runs through `/skill-eval`.
