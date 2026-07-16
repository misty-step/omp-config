# eval-design: judge alignment and best-practices

Load when the grader is a model-judge. A model-judge is a sub-eval, biased until
proven; do not quote its rate until it is aligned to human labels on the fail
class.

## The critique-align loop (Hamel)

1. Hand-label a calibration set (positive and negative cases).
2. Run the judge blind and compare to the human labels.
3. Measure **precision/recall on the fail class**, not raw agreement and not a
   bare Cohen's κ — the minority (failing) class is what a judge must catch, and
   aggregate agreement hides it on imbalanced data.
4. Iterate the judge prompt until alignment stabilizes; re-anchor whenever the
   judge model or the worker model changes.

## Best-practices bundle

Consensus across MT-Bench, G-Eval, Anthropic, Braintrust, promptfoo:

- **Decorrelated family.** Grade with a different model family than the one under
  test — a judge favors its own family (self-preference/self-enhancement bias).
- **Reason before the verdict.** Instruct chain-of-thought, then read only the
  final tagged verdict. Improves agreement on hard judgments.
- **Observable rubric.** "Must mention X in the first sentence, else incorrect" —
  clear, checkable standards, not "is it good."
- **Low-precision scale.** Binary or ≤5-point; 1-10 scales are noisier and less
  consistent (Databricks via promptfoo).
- **Give it an exit.** Let the judge return "Unknown" when it lacks information,
  so it doesn't hallucinate a grade.
- **Probe position/format sensitivity.** Swap answer order (or cosmetically
  reorder the prompt) and require agreement; a high flip rate means the judge is
  reading form, not substance.
- **Average multiple runs** to tame non-determinism; watch **verbosity bias**
  (longer ≠ better) and **G-Eval's bias toward fluent LLM-generated text**.

The `agentic_judge` runner enforces the mechanical half — `CalibrationRecord`
(fail-class precision/recall, per-family scope, κ), reasoning-first tail-anchored
verdict, `format_sensitivity_flip_rate`, and the judge-gaming canary. See
[`crucible-map.md`](crucible-map.md).
