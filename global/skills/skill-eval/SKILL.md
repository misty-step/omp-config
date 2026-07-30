---
disable-model-invocation: true
name: skill-eval
description: |
  Prove that a harness skill beats no-skill with a falsifiable A/B eval, or
  retire it. Name the one claim the skill must earn. Run it skill-on versus raw
  with the same model. Grade blind. Return a keep/adapt/cut verdict. Use
  /eval-design instead when you design an eval for a product or model.
  Use when: "eval this skill", "does this skill help", "prove the skill beats
  no skill", "write an eval for a skill", "skill A/B", "skill regression test".
  Trigger: /skill-eval, /eval-skill, /prove-skill.
argument-hint: "[skill-name] [--generate|--run|--smoke]"
---

# /skill-eval

Build the falsifier for a skill. A skill earns its place only when an agent
**with** it produces measurably better outcomes than the same agent **without**
it. Otherwise it is context tax. This skill designs, runs, and maintains that
proof. The proof must allow **no-skill won**.

An eval is a *run with a grader*, never a directory shape. Structural eval trees
were deleted as false proof in the 2026-06 consolidation. Do not rebuild them.
Start from the protocol contract at
`global/skills/harness-engineering/references/mode-eval.md` and a current
first-party eval, not a frozen routing exemplar.

## The loop

1. **Name the one claim.** Every skill earns exactly one load-bearing, falsifiable
   claim. State what it makes true that raw prompting does not. For examples:
   design: "a blind philosophy bench yields structurally distinct options where
   raw prompting yields one layout in costumes"; shape: "a stranger builds the
   right thing from the packet". Write a sentence that could be wrong. If you
   cannot name the claim, or raw prompting already meets it, mark the skill as a
   deletion candidate. Say so and stop. That is a valid, cheap eval result; it is
   not a failure to produce one.
2. **Fix the task.** Use 2–3 fixtures that stress the claim differently. Each
   fixture is a frozen prompt + a repo pinned at a SHA + a forbidden-edits list.
   One fixture is noise; cover the claim’s failure modes, not one happy path.
3. **Run the A/B.** Use the same model and fixture for both arms:
   - **A** — install and invoke the skill.
   - **B** — use raw input: the bare instruction a sharp operator would type,
     with the same model and repo access, without the skill.
   - **C (optional)** — use a credible alternative primitive (external skill,
     Ponytail for simplicity pressure). Add C only when one exists; A-vs-B is
     the floor.
   Drive the run per `references/run-recipe.md`. Native-subagent smoke is free;
   `council.sh` plus decorrelated families is the serious run.
4. **Grade blind, objective first.** Show the grader the artifacts and fixture,
   never the arm identity. Use a *different model family* from the workers.
   Mechanical checks before taste (see Graders below).
5. **Verdict + disposition.** Pass only when A beats B paired on the claim
   across ≥2 of 3 fixtures. Label the skill: `keep` / `adapt` / `cut` /
   `needs-more-tasks` / `graduate-to-Daedalus`. The verdict decides whether the
   skill has the right to exist, not whether it has a vanity score.

## Graders — three tiers, and the human is the gold

- **Objective first** (scriptable, ~free, every edit): Check that sections are
  present and non-empty, the oracle is a runnable command rather than "it should
  work", cited paths resolve at the SHA, the gate passes, forbidden edits are
  absent, and artifacts render. These checks fail without a judge. Push every
  possible check into this tier.
- **Human judgment is the ground truth** for the judgment-heavy delta. The
  operator decides a spec's buildability, a design's taste, or a critique's bite.
  Most skills need human input, not only a model. The human must sign off the
  keep/adapt/cut decision on a taste-heavy skill, unless a grader has a *recent*
  human anchor (see Cadence). At minimum, the operator blind-grades one fixture
  per eval. Use that grade as the anchor for all other checks.
- **The agent rubric is a calibrated proxy, not the judge.** Use a blind,
  decorrelated model grader to run the rubric often and cheaply. It approximates
  operator taste and drifts. Score 1–5 per dimension tied to the claim. Give one
  line of justification. Score blind with a different family from the workers.
  A worker grading its own family flatters itself. Same-family smokes prove that
  the loop fires, not the margin. Trust the margin only while it matches the
  human anchor. When proxy and human disagree, the rubric or claim is broken.
  Fix the grader; do not overrule the human.

## Cadence — match cost to stakes

A full pass is ~15–18 runs (paid, slow). Do not gate every edit on it.

- **Every `global/skills/<skill>/**` edit** → run cheap objective checks and a
  1-fixture native-subagent smoke. This catches gross regressions for free.
- **Contract-level change** (the skill's claim or output shape moved) → run a full
  A/B with decorrelated workers and all fixtures. The skill changed; re-earn the
  claim.
- **Major model release** → re-audit. *This is the point of the eval.* A stronger
  bare model erodes every skill's edge. A skill that beat raw on the old model
  may be railroading on the new one. Use the eval to find skills to retire.
- **Continuous** → use telemetry to ask whether the skill triggered when it
  should and whether loaded sessions cost more than they returned. Telemetry is
  context, not proof.
- **Calibration (the human anchor)** → include ≥1 fixture that the operator
  graded blind in every eval. Trust the agent grader only while its verdict
  matches that anchor. Re-anchor when the rubric changes, the worker model
  upgrades, or proxy-vs-human last diverged. Without a recent anchor, the
  automated verdict is unvalidated. Say so instead of quoting the margin.

## Gotchas

- **Falsifier that can't fail.** A pass bar that the skill always clears is false
  proof. Before running, ask: what result tells me to delete this skill? If no
  result can, the eval is decoration.
- **Vague rubric.** A vague rubric lets the grader approve the skill arm without
  cause. Tie every dimension to the claim. Prefer an objective check to a rubric
  line whenever one exists.
- **Self-graded family.** When the grader shares the worker's model family, the
  margin inflates. Use a smoke-only waiver, never the serious verdict.
- **One fixture.** A single task proves nothing about generalization. Use ≥2
  fixtures that span the claim's distinct failure modes.
- **Eval bloat.** Keep this skill minimal. Serious, repeated arena work
  (composition sweeps, model selection) graduates to Daedalus. Do not expand
  this repository into a benchmark platform.
- **Grading prose, not outcomes.** "The packet reads well" is not the claim.
  "A cold lane built the feature from the packet" is. Grade the outcome that the
  skill promises.
- **Agent judge ≠ ground truth.** The rubric grader proxies operator taste. An
  unanchored proxy approves without cause. Anchor it to a blind human grade or
  do not quote the margin.

## Route

| Need | Load |
|---|---|
| generate a new skill's eval | `templates/eval-spec.md` |
| blind grader prompt | `templates/grader-prompt.md` |
| drive the A/B (smoke + serious) | `references/run-recipe.md` |
| eval protocol contract | `global/skills/harness-engineering/references/mode-eval.md` |
| current first instance | `global/skills/dispatch/evals/dispatch-eval.md` |

## Verification

The eval spec lands at `global/skills/<skill>/evals/<skill>-eval.md` and mirrors
the design exemplar. Run evidence lands at
`.evidence/harness-evals/<skill>/<date>/`. Store sanitized artifacts and scored
receipts only. Never store raw transcripts with secrets.

A run is real only when it produces both arms and a grader verdict that could
have gone the other way.

Every first-party skill carries either an eval spec or a live, unexpired
`global/skills/<skill>/evals/WAIVER.md`. A waiver is a time-boxed deferral, not a
permanent opt-out. The exact new-skill scaffolding steps live in
`global/skills/harness-engineering/references/skill-design-principles.md`
("New Skill: Eval Scaffold Is Not Optional").
