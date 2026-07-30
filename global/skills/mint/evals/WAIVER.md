# mint eval waiver

expires: 2026-09-30

## Reason

mint's claim says that an agent causes an authorized vendor effect without seeing
the real credential. An executable falsifier already proves this claim, not a
skill A/B: `scripts/mint-probe.sh` in the mint repo and its CI job assert that the
agent-shaped caller never sees the secret, the audit log never contains it, and
a policy-denied call reaches the vendor zero times. A skill-level A/B over the
same claim would duplicate the probe without adding decorrelated evidence.

## Disposition

Time-boxed deferral, not a permanent opt-out. When it expires, either land an
eval spec at `global/skills/mint/evals/mint-eval.md` (use the template
`global/skills/skill-eval/templates/eval-spec.md`) that proves the *skill*, not
the probe, changes agent behavior. For example, prove that the skill-on arm
routes through mint while the raw arm inlines a key. Or renew this waiver with a
fresh reason and date. A silently renewed waiver is itself a finding for
`/harness-engineering`'s next skill-health audit.
