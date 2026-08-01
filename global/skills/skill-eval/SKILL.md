---
disable-model-invocation: true
name: skill-eval
description: Prove that a harness skill beats no-skill with a falsifiable A/B eval, or retire it. Use the same model for skill-on and raw arms, grade blind, and return keep/adapt/cut. Use /eval-design for product or model eval design. Trigger: /skill-eval, /eval-skill, /prove-skill.
argument-hint: "[skill-name] [--generate|--run|--smoke]"
---

# /skill-eval

Build a falsifier. The same agent with the skill must beat the same agent without
it on a measurable outcome, or the skill is context tax. No-skill must be able to win.

An eval is a run with a grader, not a directory shape. Structural eval trees were
deleted as false proof in the 2026-06 consolidation; do not rebuild them. Start
with `global/skills/harness-engineering/references/mode-eval.md` and a current
first-party eval, not a frozen routing exemplar.

## Loop

1. **Name one claim.** State one falsifiable outcome beyond raw prompting. If no such claim exists, or raw prompting meets it, mark the skill for deletion and stop.
2. **Fix the task.** Use 2–3 frozen fixtures with prompt, repo SHA, and forbidden-edits list. Include one noise fixture and distinct failure modes.
3. **Run the A/B.** Use the same model and fixture:
   - **A:** install and invoke the skill.
   - **B:** use the bare sharp-operator instruction with the same repo access and no skill.
   - **C (optional):** use a credible alternative primitive, such as an external skill or Ponytail for simplicity pressure, only when one exists.
   Drive runs with `references/run-recipe.md`. Native-subagent smoke is free; `council.sh` with decorrelated families is serious.
4. **Grade blind.** Show artifacts and fixture, not arm identity. Use a different model family from workers. Run mechanical checks before taste.
5. **Verdict.** Pass only when A beats B paired on the claim across ≥2 of 3 fixtures. Label `keep`, `adapt`, `cut`, `needs-more-tasks`, or `graduate-to-Daedalus`.

## Graders

- **Objective:** Check non-empty sections, runnable oracle commands, cited paths at the SHA, gates, forbidden edits, and rendered artifacts. Push every possible check here.
- **Human:** The operator is ground truth for judgment-heavy deltas. Blind-grade at least one fixture per eval and anchor all checks to it. Taste-heavy skills need sign-off unless a recent anchor exists.
- **Agent:** Use a blind decorrelated model grader as proxy. Score 1–5 per claim dimension with one justification line and a different family from workers. Same-family smoke proves the loop, not the margin. Trust the margin only while it matches the anchor; fix the rubric when they disagree.

## Cadence

A full pass costs about 15–18 runs; do not gate every edit on it.

- Every `global/skills/<skill>/**` edit: cheap objective checks plus one-fixture native-subagent smoke.
- Contract-level claim or output-shape change: full A/B with decorrelated workers and all fixtures.
- Major model release: re-audit; a stronger raw model can erase the skill's edge.
- Continuous telemetry: check triggering and loaded-session cost; telemetry is context, not proof.
- Calibration: include ≥1 operator blind-graded fixture. Re-anchor when rubric, worker model, or proxy-versus-human divergence changes. Without a recent anchor, call automation unvalidated and do not quote its margin.

## Avoid

- Use a pass bar that can fail; ask what result would delete the skill.
- Tie every rubric dimension to the claim; prefer objective checks.
- Never use a self-graded family for the serious verdict.
- Use ≥2 fixtures with distinct failure modes; one fixture proves no generalization.
- Keep this skill minimal; send composition sweeps and model selection to Daedalus.
- Grade outcomes, not packet prose.
- Treat an unanchored agent judge as a proxy, not ground truth.

## Route

| Need | Load |
|---|---|
| Generate a new skill eval | `templates/eval-spec.md` |
| Blind grader prompt | `templates/grader-prompt.md` |
| Drive smoke and serious A/B runs | `references/run-recipe.md` |
| Eval protocol contract | `global/skills/harness-engineering/references/mode-eval.md` |
| Current first instance | `global/skills/dispatch/evals/dispatch-eval.md` |

## Verification

The eval spec lands at `global/skills/<skill>/evals/<skill>-eval.md` and mirrors
the design exemplar. Run evidence lands at
`.evidence/harness-evals/<skill>/<date>/`. Store sanitized artifacts and scored
receipts only; never store raw transcripts with secrets.

A real run produces both arms and a grader verdict that could have gone either way.
Every first-party skill carries an eval spec or a live, unexpired
`global/skills/<skill>/evals/WAIVER.md`. A waiver is time-boxed, not permanent.
New-skill scaffolding is defined in
`global/skills/harness-engineering/references/skill-design-principles.md`
("New Skill: Eval Scaffold Is Not Optional").
