---
name: pulse
description: Produce a dated, evidence-backed account of a software system's material health.
disable-model-invocation: true
argument-hint: "[target-path] [--window=30d]"
---

# Pulse

Answer the operator's health question with the smallest set of current signals
that can change the verdict.

## Bind

Resolve the target, revision, comparison window, relevant product surfaces,
deployed environments, and evidence limits. Default the window to 30 days when
trend matters.

## Measure

Use current primary sources and safe read probes. Check product behavior,
delivery safety, production health, or structural ownership only when relevant
to the question. Keep missing, not-applicable, and failing distinct. Give each
material claim enough source, time, scope, and runtime identity to be checked.

## Judge and render

State the controlling verdict first. A finding needs a mechanism, evidence,
impact, and smallest credible action. Do not add generic best practices or
persona judgments.

Produce a concise report in the requested format. Use self-contained HTML when
the operator asks for a dashboard or when comparison benefits from charts.
Inspect the rendered output when HTML is used.

Done when every recommendation follows from a measured failure or trend and the
report contains no unused sections.
