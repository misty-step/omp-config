---
name: dispatch
description: Choose or audit OMP model routes from current access, task evidence, cost, and fallback needs.
---

# Dispatch

A route is good only for a named workload. Current access and task-shaped
evidence beat reputation.

## Frame

State the workload, quality bar, tools, modalities, context, latency, cost,
privacy, provider, and fallback constraints.

Done when failure and success are observable.

## Establish current truth

Run `omp models refresh`, `omp models
--json`, and `omp usage --json --redact`. Read live `config.yml` and specialist
agent frontmatter. Remove inaccessible or quota-blocked selectors.

Done when every candidate and effort level resolves now.

## Compare

Use evidence in this order: local task-shaped runs, matching independent
benchmarks, provider technical reports, then current route data. Compare exact
model versions on the actual role. Do not average unrelated benchmarks.
Prefer the least expensive route that clears the quality bar.

Build a fallback chain that preserves required tools, modality, context, and
quality. Change provider early enough to survive an outage. Mark any downgrade
or operator authorization.

Done when one primary and each fallback have evidence and activation rules.

## Apply

When authorized, change the single owner: `modelRoles`,
`retry.fallbackChains`, or specialist frontmatter. Install in isolation and run
one representative workload. Record the resolved model, result, cost limits,
rejected routes, and evidence gaps.

Done when the configured route resolves and clears the named quality bar.
