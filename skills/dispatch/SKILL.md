---
name: dispatch
description: Choose or audit OMP model routes from current access, task evidence, cost, and fallback needs.
---

# Dispatch

Choose a route for a named workload. Current access and task-shaped evidence
beat reputation.

## Frame

Record the workload, quality bar, tools, modalities, context, latency, cost,
privacy, provider, and fallback constraints. State what success and failure
look like.

## Establish current truth

Run `omp models refresh`, `omp models --json`, and
`omp usage --json --redact`. Read live `config.yml` and specialist frontmatter.
Remove inaccessible or quota-blocked selectors. Every candidate and effort
level must resolve now.

## Compare

Use evidence in this order: local task-shaped runs, matching independent
benchmarks, provider technical reports, then current route data. Compare exact
model versions on the actual role. Prefer the least expensive route that clears
the quality bar.

Build fallbacks that preserve required tools, modality, context, and quality.
Change provider early enough to survive an outage. Mark downgrades and any
operator-owned activation.

## Apply

When authorized, change one owner: `modelRoles`,
`retry.fallbackChains`, or specialist frontmatter. Install in isolation and run
one representative workload. Record the resolved model, result, cost limits,
rejected routes, evidence gaps, and fallback activation rules.
