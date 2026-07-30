# /harness-engineering eval

Test whether a skill improves agent outcomes.
Do not test whether its prose sounds reasonable.

Load `../../../shared/references/verification-system-first.md` when you design
the eval.
The eval verifies an agent-behavior claim.
Make the task, transcript, outcome, grader, evidence packet, and cadence
explicit.

## Protocol

Every eval has these pieces:

1. **Task** — representative prompt and repo fixture/context.
2. **Transcript** — tool calls, intermediate artifacts, and final answer.
3. **Outcome** — the final state or artifact the skill was supposed to create.
4. **Graders** — pass/fail commands, static checks, rubric judge, or human
   calibration notes.
5. **Cadence** — when this eval reruns: one-off shape evidence, pre-merge gate,
   model-upgrade audit, or recurring Mode B benchmark lane.

Prefer objective outcome graders first:
commands run, files created, tests pass, evidence paths exist, and forbidden
edits are absent.
Use rubric or model judges only for judgment-heavy outputs.
Calibrate them against human examples.

## How to run one

Run A/B trials in worktrees.
Spin one agent on the task with the skill installed.
Spin one agent without the skill, or with the candidate revision.
Then ask a fresh comparison agent to grade both outputs against the rubric.
The comparison agent must not know which output is which.
Use two or three task instances instead of one.
Use a different model family for the grader and workers.

## Boundaries

- Structural eval trees do not prove behavior; the 2026-06 consolidation
  deleted them.
  An eval is a run with a grader, not a directory shape.
- A benchmark without a baseline, variance note, or threshold is not an eval
  result.
  It is a transcript waiting for a grader.
- The cheapest valid eval is live telemetry plus judgment:
  did the skill trigger when it should, and did sessions that loaded it end
  better?
  Use harness-native invocation logs plus Powder receipts.
- HarnessX-style trace evolution is review-only here.
  A Mode B/eval lane may propose typed harness edits from sanitized traces.
  No source edit ships without held-out tasks, the full omp-config gate, fresh
  critic review, and human approval.
  Candidate patches are artifacts, not self-merging workers.
- Serious, repeated eval work, such as benchmarking agent compositions or
  selecting models for a recurring workflow, belongs in Daedalus's arena loop,
  not ad-hoc here.
