---
disable-model-invocation: true
name: eval-design
description: >
  Design LLM/agentic evals that change decisions. Separate capability evals from
  instrumentation, and calibrate judges before comparing models or harnesses.
  Trigger: /eval-design.
argument-hint: "[capability|decision] [--corpus|--judge|--compare]"
---

# /eval-design

Build an eval that can change a decision, or do not build it.
An eval is a **task plus a model or agent under test that produces fresh output, plus a grader that scores that output**.
Run it over a corpus. Add an interval to every rate.
Calibrate every model-judge and check the noise floor for every comparison.
Anything that scores a *fixed artifact* (a lint pass or a snapshot diff) or a
*past metric* (a dashboard KPI or a CI trend) is **instrumentation, not an eval**.
Instrumentation cannot show whether a model or agent is *capable* because it
produces no fresh output against a task.
Do not call instrumentation an eval. This skill prevents that common failure.

To prove that a harness skill beats no skill, use `/skill-eval`.
It provides the skill-specific A/B specialization of this design method.

Crucible supplies the statistics, enforcement, and evidence engine beneath this skill.
The `references/crucible-map.md` file maps each design step to its Crucible surface.
Never re-implement the statistics in prose. Point into Crucible.

## The demarcation test (run this first)

Before you design anything, answer three questions.
A "no" means you have instrumentation, a KPI, or a unit test, not an eval.
State that result and stop, or reshape it into a real eval.

1. **Is there a decision?** Name the decision that the number will change:
   ship this prompt, pick model A over B, or accept this harness change.
   Without a downstream decision, the result is a metric, not an eval.
2. **Is fresh output produced against a task?** The model or agent must *generate*
   something in response to a task. A checked-in file, git-history trend, or
   static rule is instrumentation.
3. **Does a grader score that output against a defensible standard?** "The build
   is green" is a gate. "The agent's patch resolves the issue, judged against a
   reference, at 62% ± 6%" is an eval.

## The design sequence

Size the effort to the stakes. A prompt tweak needs a light pass.
A model-selection decision under budget needs the full treatment.
Keep the order fixed.

### 1. Decision → capability
State the decision, then state the **one capability under test** as a falsifiable
claim: "agent resolves real GitHub issues," not "agent is good."
Multidimensional targets are normal, such as correctness AND no regression AND
under budget. Make each dimension its own measurable criterion.
Anthropic gives this example: "less than 0.1% of 10,000 trials flagged," not "safe."
Use one capability per eval. Three dimensions need three graders, not one fuzzy score.

### 2. Corpus
- **Draw from real failures.** Start with 20–50 tasks from the bug tracker,
  support queue, and development failures (Anthropic 2026-01).
  Use synthetic tasks to fill gaps. Let real failures anchor the distribution.
- **Make every task expert-agreement-solvable.** Two domain experts must reach
  the same pass/fail verdict. State every grader check in the task.
  Do not make an agent fail because the specification is ambiguous.
- **Attach a reference solution.** A known passing output proves that the task
  is solvable and that the grader works. A 0% pass rate usually indicates a
  broken task or grader, not an incapable model. Read the transcripts.
- **Class-balance the corpus.** Include cases where the behavior should occur
  and cases where it should not. An only-positive corpus measures recall without
  precision. A model that always says "yes" then scores 100%.
- **Cover edge cases.** Include empty or irrelevant, over-long, adversarial, and
  genuinely ambiguous input. Label the ambiguous cases.
- **Size the corpus to the effect.** Detecting a 3% difference at 80% power needs
  about 1,000 tasks (Miller 2024). Most bespoke evals resolve only larger effects.
  Declare the resolvable effect and let `crucible validate` warn you.

### 3. Grader — climb the ladder, stop at the first rung that holds
- **Use code / deterministic checks first.** Use exact or regex matches, suite
  status, JSON validity, and target-state checks. These checks are fast and
  reproducible, but valid variations can fail them. Use every available check here.
- **Use a model-judge** for open-ended quality that code cannot capture, such as
  prose correctness, rubric adherence, or tone. Calibrate it before you trust it.
  Read `references/judge-alignment.md`.
- **Use a human** as the calibration anchor and for irreducibly subjective calls.
  Reserve human grading for judge anchoring, not volume.

**For agents:** Grade the **outcome and the transcript, not the trajectory**.
Verify the final environment state, such as the reservation in the DB or the
patch that fixes the bug. Also verify the transcript, including tool calls and reasoning.
Do not assert a specific step sequence. Agents can find valid paths you did not
anticipate, and step checks make tests brittle.
Cap behavior with `max_turns`. Never prescribe *how*. Use partial credit for
multi-part tasks.
For stochastic agents, choose the rate: **`pass@k`** means one of k succeeds,
and **`pass^k`** means all k succeed. The first fits coding; the second fits
customer-facing consistency. At k=10, 100% and 0% tell opposite stories.
Isolate each trial in a clean environment so infrastructure flakiness cannot
correlate failures.

### 4. Judge alignment
Align every model-judge before you trust it. Treat it as a biased sub-eval until
you prove alignment.
Read the critique-align loop and best-practices bundle in
`references/judge-alignment.md`. They cover decorrelated family,
reason-before-verdict, observable rubric, low-precision scale, and
position/format probes.

### 5. Comparison — refuse a delta you can't defend
- **Report an interval for every rate.** Use `62% (±6%)`, never a bare `62%`.
  For binary results, use `SE = sqrt(p(1-p)/n)`.
- **Pair the comparison.** Run both arms on the *same* tasks.
  Per-task differences reduce variance for free (Miller 2024).
  `crucible runs compare` performs this pairing.
- **Check the noise floor.** A delta inside it is not a result.
  Say "underpowered" or "no effect," and do not report a number.
  Use Crucible's resolution ratio and MDE.
- **Cluster SEs when tasks are grouped.** Grouping includes multiple prompts per
  repo or one task across many models. Clustered SEs can exceed naive SEs by >3×.
  Crucible does not compute them yet, so flag grouped corpora.
- **Attribute the result to one axis.** A delta spanning model *and* harness is
  unattributable. Change one axis per comparison, or label it `config_delta`.

## Anti-patterns (the ways a "good eval" is fake)

- **Instrumentation in an eval costume.** People present a linter, CI gate, or
  KPI as a capability eval. It has no fresh output, task, or defensible grader.
  The demarcation test catches this canonical failure, especially for a
  familiar-looking "add an eval for X" request.
- **Recall-only corpus.** Only-positive cases let a model that always fires score
  perfectly. Class-balance the corpus, or the rate is meaningless.
- **Uncalibrated / self-graded judge.** Do not quote a model-judge rate before
  aligning it to human labels on the fail class. Do not grade with the worker's
  own family. Both choices inflate the margin.
  Anchor and decorrelate the judge. Re-anchor after any judge or worker model change.
- **Trajectory policing.** Do not assert a tool sequence for an agent.
  The check is brittle and can fail a competent agent that found a better path.
  Grade the end state.
- **Bare delta.** A rate or two-model gap without an interval or noise-floor check
  is not useful. Inside the noise floor, `62% vs 60%` is nothing.
  Most bespoke evals resolve only larger effects. State the MDE.
- **Goodhart / saturation.** A target can train against its eval.
  An eval can also stay at 100% and yield no signal.
  Keep a held-out slice and retire saturated evals.
- **Eval without data review.** Do not build a corpus and grader without *looking at the data*.
  "You are doing it wrong if you aren't looking at lots of data" (Hamel).
  Grader bugs and broken tasks surface in the transcripts.
- **Grader before corpus.** Read real failures before you write a defensible
  grader. Let the corpus and grader co-evolve.
  Use the reference solution to confirm that the grader works.

## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract.
An eval design is done only when it meets every condition:
- The demarcation test passes: decision, fresh output, and defensible grader.
- The corpus is class-balanced, sourced from real failures, and has a reference
  solution for every task.
- The grader climbs no higher than necessary.
- Every model-judge is calibrated against human labels and records fail-class precision/recall.
- The comparison plan names the interval, paired noise-floor check, and single axis.
- The runnable proof uses the Crucible loop in `references/crucible-map.md`.

## Sources

Load the annotated primary-source canon in
[`references/sources.md`](references/sources.md) to justify a methodology choice,
go deeper than this distillation, or give a lane the literature.
The canon includes Anthropic agentic-evals 2026-01, Hamel Husain, Miller's
error-bars paper, the MT-Bench/G-Eval judge-bias catalog, and Inspect as a
reference architecture.
