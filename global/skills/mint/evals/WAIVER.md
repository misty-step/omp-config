# mint eval waiver

expires: 2026-09-30

## Reason

mint's claim — an agent causes an authorized vendor effect while never seeing
the real credential — is already proven by an executable falsifier, not a skill
A/B: `scripts/mint-probe.sh` in the mint repo (plus its CI job) asserts the
agent-shaped caller never sees the secret, the audit log never contains it, and
a policy-denied call reaches the vendor zero times. A skill-level A/B over that
same claim would duplicate the probe without adding decorrelated evidence.

## Disposition

Time-boxed deferral, not a permanent opt-out. When it expires, either an eval
spec lands at `primitives/skills/misty-mint/evals/mint-eval.md` (template:
`primitives/skills/skill-eval/templates/eval-spec.md`) proving the *skill* (not
the probe) changes agent behavior — e.g. that the skill-on arm routes through
mint where the raw arm inlines a key — or this waiver is renewed with a fresh
reason and date. A silently renewed waiver is itself a finding for
`/harness-engineering`'s next skill-health audit.
