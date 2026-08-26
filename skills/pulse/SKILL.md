---
name: pulse
description: Produce a dated, evidence-backed HTML account of software health, production, verification, structure, and risk.
disable-model-invocation: true
argument-hint: "[target-path] [--window=30d]"
---

# Pulse

Pulse answers three questions: Does the product work now? Can the team change it
safely? Is the system becoming easier or harder to own? A score without source,
time, and identity is not an answer.

## Bind the report

Resolve the target, revision, dirty state, comparison window, product surfaces,
deployed environments, and exclusions. Default the window to 30 days. Embed one
versioned machine-readable payload as the report's data owner.

Every datum carries value, unit, source, capture time, scope, revision or runtime
identity, method, confidence, and status: observed, source-proven, inferred,
unavailable, or drifted.

Done when every section reads from one bounded payload.

## Measure

Use current primary sources and safe read probes. Cover:

- current repository state and recent change;
- public and operator product behavior;
- deployed identity, health, dependencies, and recovery;
- repository checks, test defense, CI latency, and failures;
- complexity distribution, median, p95, and maximum when a numeric analyzer is configured, or structural proxy findings/hotspots; module token budgets, ownership, coupling, and trend;
- validated defects, incidents, regressions, and release stability;
- system design, data paths, states, and trust boundaries;
- independent persona judgments grounded in the same immutable packet.

Keep missing, not-applicable, and failing distinct. Do not infer production from
source or health from an open port. Do not send alerts, mutate production, or
invent benchmark values.

Done when each material claim has evidence or an explicit gap.

## Judge

Separate facts from assessments. A finding states the mechanism, evidence,
impact, owner, and smallest credible action. Deduplicate shared root causes.
Prioritize broken product behavior, unsafe release or recovery, data risk, and
structural ownership failures over style or activity counts.

Done when every recommendation follows from a measured failure or trend.

## Render and inspect

Write one self-contained HTML report with: controlling verdict; identities and
scope; indexed domains; current and baseline evidence; production; verification;
stability; design; independent assessments; findings; source index; gaps; and
machine-readable payload.

Open it in a headless browser. Check navigation, charts, tables, labels, links,
responsive layout, and consistency with the payload. Return the inspected path
or requested published URL.

Done when every visible claim traces to the payload and source.
