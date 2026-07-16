---
name: eval-design
description: |
  Design an LLM/agentic eval that can change a decision — a task + a model or
  agent under test producing fresh output + a grader — and separate real
  capability evals from instrumentation (linters, CI gates, KPIs). For proving a
  harness skill earns its keep, use /skill-eval instead. Use when: designing or
  critiquing an eval, building an eval corpus, designing or calibrating an
  LLM-as-judge, or comparing models/harnesses on a measured capability.
  Trigger: /eval-design.
argument-hint: "[capability|decision] [--corpus|--judge|--compare]"
---

# /eval-design

Build an eval that can change a decision, or don't build it. An eval is a **task
+ a model or agent under test that produces fresh output + a grader that scores
that output**, run over a corpus, with an interval on every rate, calibration on
every model-judge, and a noise-floor check on every comparison. Anything that
scores a *fixed artifact* (a lint pass, a snapshot diff) or a *past metric* (a
dashboard KPI, a CI trend) is **instrumentation, not an eval** — useful, but it
can't tell you whether a model or agent is *capable*, because nothing fresh was
produced against a task. Shipping instrumentation and calling it an eval is the
most common failure this skill prevents.

For proving a harness skill beats no-skill, use `/skill-eval` — the
skill-specific A/B specialization of this design method.

The statistics live in Crucible, the enforcement + evidence engine underneath
this skill; `references/crucible-map.md` maps each design step to its Crucible
surface. Never re-implement the statistics in prose — point into Crucible.

## The demarcation test (run this first)

Before designing anything, answer three questions. A "no" means you have
instrumentation, a KPI, or a unit test — valuable, but not an eval. Say so and
stop, or reshape it into a real eval.

1. **Is there a decision?** Name the decision the number will change — ship this
   prompt, pick model A over B, accept this harness change. No downstream
   decision → a metric, not an eval.
2. **Is fresh output produced against a task?** The model/agent must *generate*
   something in response to a task. Grading a checked-in file, a git-history
   trend, or a static rule is instrumentation.
3. **Does a grader score that output against a defensible standard?** "The build
   is green" is a gate. "The agent's patch resolves the issue, judged against a
   reference, at 62% ± 6%" is an eval.

## The design sequence

Size the effort to the stakes — a prompt tweak needs a light pass, a
model-selection decision under budget needs the full treatment. The order is
fixed.

### 1. Decision → capability
State the decision, then the **one capability under test** as a falsifiable
claim: "agent resolves real GitHub issues," not "agent is good." Multidimensional
targets are normal (correctness AND no regression AND under budget) — make each
its own measurable criterion (Anthropic: "less than 0.1% of 10,000 trials
flagged," not "safe"). One capability per eval; three dimensions means three
graders, not one fuzzy score.

### 2. Corpus
- **Draw from real failures.** 20–50 tasks from the bug tracker, support queue,
  and the failures you hit in development is a strong start (Anthropic 2026-01).
  Synthetic tasks fill gaps; real failures anchor the distribution.
- **Every task must be expert-agreement-solvable** — two domain experts reach the
  same pass/fail verdict — and everything the grader checks is stated in the
  task, so no agent fails on an ambiguous spec.
- **Attach a reference solution.** A known passing output proves the task is
  solvable *and* that the grader is configured right; a 0% pass rate is almost
  always a broken task or grader, not an incapable model — read the transcripts.
- **Class-balance it.** Include cases where the behavior should occur AND where it
  shouldn't; an only-positive corpus measures recall with no precision, and the
  model that always says "yes" scores 100%.
- **Cover edge cases:** empty/irrelevant, over-long, adversarial, and genuinely
  ambiguous input (label the ambiguous ones).
- **Size to the effect.** Detecting a 3% difference at 80% power needs ~1,000
  tasks (Miller 2024); most bespoke evals resolve only larger effects — declare
  the resolvable effect rather than over-read a small delta, and let `crucible
  validate` warn you.

### 3. Grader — climb the ladder, stop at the first rung that holds
- **Code / deterministic first.** Exact/regex match, "does the suite pass," "is
  the JSON valid," did the file reach the target state. Fast, reproducible,
  brittle to valid variation — push every check you can here.
- **Model-judge** for open-ended quality code can't capture (prose correctness,
  rubric adherence, tone). Calibrate it before you trust it —
  `references/judge-alignment.md`.
- **Human** as the calibration anchor and for the irreducibly subjective call —
  reserve it for anchoring the judge, not for volume.

**For agents specifically:** grade the **outcome and the transcript, not the
trajectory.** Verify the final environment state (did the reservation land in the
DB, does the patch fix the bug) plus the transcript (tool calls, reasoning). Do
NOT assert a specific step sequence — agents find valid paths you didn't
anticipate, and step-checking makes brittle tests. Cap behavior (`max_turns`),
never prescribe *how*, and use partial credit for multi-part tasks. For
stochastic agents the rate is a design choice: **`pass@k`** (one of k succeeds —
coding) vs **`pass^k`** (all k succeed — customer-facing consistency); they
diverge fast (at k=10, 100% vs 0% tell opposite stories). Isolate each trial in a
clean environment so infra flakiness doesn't correlate failures.

### 4. Judge alignment
Mandatory before trusting any model-judge — a biased sub-eval until proven. The
critique-align loop and the best-practices bundle (decorrelated family,
reason-before-verdict, observable rubric, low-precision scale, position/format
probes) live in `references/judge-alignment.md`.

### 5. Comparison — refuse a delta you can't defend
- **Interval on every rate.** `62% (±6%)`, never a bare `62%`. Binary: `SE =
  sqrt(p(1-p)/n)`.
- **Pair the comparison.** Run both arms on the *same* tasks; per-task differences
  buy variance reduction for free (Miller 2024). `crucible runs compare` does this.
- **Check the noise floor.** A delta inside it is not a result — say "underpowered"
  or "no effect," don't report a number (Crucible's resolution ratio + MDE).
- **Cluster your SEs when tasks are grouped** (multiple prompts per repo, one task
  across many models); clustered SEs can be >3× naive ones. Crucible does not yet
  compute them — flag it when your corpus is grouped.
- **Attribute to one axis.** A delta spanning model *and* harness is
  unattributable — change one axis per comparison, or label it `config_delta`.

## Anti-patterns (the ways a "good eval" is fake)

- **Instrumentation in an eval costume.** A linter, CI gate, or KPI presented as a
  capability eval — no fresh output, no task, no defensible grader. The operator's
  canonical failure; the demarcation test catches it, especially on a
  familiar-looking "add an eval for X" request.
- **Recall-only corpus.** Only-positive cases; the model that always fires scores
  perfectly. Class-balance or the rate is meaningless.
- **Uncalibrated / self-graded judge.** Quoting a model-judge's rate before
  aligning it to human labels on the fail class, or grading with the worker's own
  family — both inflate the margin. Anchor and decorrelate, or it's a smoke test.
  Re-anchor on any judge/worker model change.
- **Trajectory policing.** Asserting a tool sequence for an agent — brittle, and it
  fails competent agents who found a better path. Grade the end state.
- **Bare delta.** A rate or two-model gap with no interval and no noise-floor
  check; inside the noise floor, `62% vs 60%` is nothing. Most bespoke evals
  resolve only large effects — state the MDE.
- **Goodhart / saturation.** An eval the target trains against, or one stuck at
  100% and yielding no signal. Keep a held-out slice; retire saturated evals.
- **Eval theater.** Building corpus and grader but never *looking at the data*.
  "You are doing it wrong if you aren't looking at lots of data" (Hamel) — grader
  bugs and broken tasks only surface in the transcripts.
- **Grader before corpus.** You can't write a defensible grader until you've read
  real failures; corpus and grader co-evolve, and the reference solution is how
  you know the grader works.

## Completion Gate

See `primitives/shared/AGENTS.md` (Prove) for the shared core. An
eval design is done when: the demarcation test passes (decision + fresh output +
defensible grader); the corpus is class-balanced, real-failure-sourced, and
carries a reference solution per task; the grader climbs no higher than it must;
any model-judge is calibrated against human labels with fail-class
precision/recall recorded; and the comparison plan names the interval, the paired
noise-floor check, and the single axis under test. The runnable proof is the
Crucible loop (`references/crucible-map.md`).

## Sources

The annotated primary-source canon lives in
[`references/sources.md`](references/sources.md) — load it to justify a
methodology choice, go deeper than this distillation, or hand a lane the
literature (Anthropic agentic-evals 2026-01, Hamel Husain, Miller's error-bars
paper, the MT-Bench/G-Eval judge-bias catalog, Inspect as reference
architecture).
