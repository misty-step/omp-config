# eval-design: judge alignment and best-practices

Load this file when the grader is a model-judge.
Treat a model-judge as a biased sub-eval until you prove alignment.
Do not quote its rate until it aligns with human labels on the fail class.

## The critique-align loop (Hamel)

1. Hand-label a calibration set (positive and negative cases).
2. Run the judge blind and compare to the human labels.
3. Measure **precision/recall on the fail class**, not raw agreement or a bare
   Cohen's κ. The failing minority class is what a judge must catch.
   Aggregate agreement hides this class in imbalanced data.
4. Iterate the judge prompt until alignment stabilizes.
   Re-anchor after the judge model or worker model changes.

## Best-practices bundle

Consensus across MT-Bench, G-Eval, Anthropic, Braintrust, promptfoo:

- **Decorrelated family.** Grade with a different model family than the one under
  test. A judge favors its own family (self-preference/self-enhancement bias).
- **Reason before the verdict.** Instruct chain-of-thought, then read only the
  final tagged verdict. This improves agreement on hard judgments.
- **Observable rubric.** Use "Must mention X in the first sentence, else
  incorrect." Set clear, checkable standards, not "is it good."
- **Low-precision scale.** Use binary or ≤5-point scales.
  1-10 scales are noisier and less consistent (Databricks via promptfoo).
- **Give it an exit.** Let the judge return "Unknown" when it lacks information.
  This prevents a hallucinated grade.
- **Probe position/format sensitivity.** Swap answer order or cosmetically
  reorder the prompt. Require agreement. A high flip rate means the judge reads
  form, not substance.
- **Average multiple runs** to reduce non-determinism.
  Watch **verbosity bias**: longer ≠ better.
  Watch **G-Eval's bias toward fluent LLM-generated text**.

The `agentic_judge` runner enforces the mechanical half:
`CalibrationRecord` records fail-class precision/recall, per-family scope, and κ.
The runner also records the reasoning-first tail-anchored verdict,
`format_sensitivity_flip_rate`, and the judge-gaming canary.
See [`crucible-map.md`](crucible-map.md).
