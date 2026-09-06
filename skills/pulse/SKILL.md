---
name: pulse
description: Answer a software system's material health question from current signals.
disable-model-invocation: true
argument-hint: "[target-path] [--window=30d]"
---

# Pulse

Answer one health question with the smallest set of current signals that can
change the verdict.

## Bind

Resolve the target, revision, comparison window, relevant surfaces, deployed
environments, and evidence limits. Default to a 30-day window when trend
matters.

## Measure

Use current primary sources and safe read probes. Check product behavior,
delivery safety, production health, and structural ownership only when the
question needs them. For a failure or recovery question, trace the signal path
to identify what failed, who was affected, which release caused it, and how to
recover. Give each claim source, time, scope, and runtime identity. Keep
missing, not-applicable, and failing distinct.

## Judge and render

Lead with the controlling verdict. A finding needs a mechanism, evidence,
impact, and smallest credible repair. Recommend a provider only when the
required signal is clear and the current system cannot supply it. Render the
requested format; use self-contained HTML for a dashboard or useful comparison,
then inspect the rendered output. Omit sections with no material evidence.
