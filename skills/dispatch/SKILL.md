---
name: dispatch
description: Choose or audit OMP model routes from current access, task fit, measured performance, benchmarks, cost, and fallback requirements. Use when selecting a model, effort, role, specialist agent, or fallback chain; comparing models for a workload; or updating model routing.
---

# Dispatch

Route one workload to the strongest justified model chain. Current evidence
wins over reputation.

## 1. Frame the dispatch

Name:

- workload and observable quality bar;
- coding, tools, reasoning, vision, research, or review needs;
- context size and input types;
- latency, throughput, cost, privacy, and provider constraints;
- ambient, operator-visible on-demand, or release-critical use;
- required fallback behavior.

If no workload is named, build a capability map for the models currently
accessible through OMP.

Completion criterion: The dispatch question and hard constraints are explicit.

## 2. Establish local truth

Search exocortex for prior routing decisions. Then run:

```text
omp models refresh
omp models --json
omp usage --json --redact
```

Treat OMP as the authority for selectors, effort support, modalities, context,
local credentials, and current quota. Treat `config.yml` and specialist-agent
frontmatter as the authority for live roles and fallback order.

Discard inaccessible selectors before comparison. Mark quota-limited routes.

Completion criterion: Every candidate selector, effort, modality, and access
claim is valid now.

## 3. Pull capability evidence

Use current, exact model versions. Record publication date and source for each
claim.

Evidence order:

1. a local task-shaped benchmark or recent repository transcript;
2. an independent benchmark that matches the workload;
3. a provider model card, system card, or technical report;
4. an OpenRouter route record for price, endpoint, and provider availability.

Enable the OpenRouter MCP server through `/mcp` only while querying its route
data. Disable it when complete. If MCP is unavailable, use current primary
sources and mark the gap.

Choose benchmarks by workload:

- repository coding: SWE-bench Verified or a stricter current successor;
- terminal agents: Terminal-Bench;
- code generation: LiveCodeBench or an equivalent contamination-aware set;
- long context: MRCR, RULER, or a task-shaped retrieval probe;
- factual research: source-grounded task evals, not style preference;
- vision: the benchmark matching document, chart, screenshot, or image work;
- latency and throughput: `omp bench` on this machine and provider route data;
- cost: current provider pricing and observed token use.

Do not average unrelated leaderboards. Do not compare different model dates as
one selector. A benchmark score is evidence for its task, not a general
intelligence rank.

Completion criterion: Every material capability claim has exact-version,
task-relevant, dated evidence or an explicit evidence gap.

## 4. Match the role

Judge candidates against the actual job:

- `default`, `task`: implementation and tool reliability;
- `slow`, `plan`, `reviewer`, `advisor`: long-horizon judgment and defect
  detection;
- `designer`, `vision`: product design and image input;
- `smol`, `tiny`, `commit`: latency after the quality floor;
- specialist agent: narrow policy, tools, output schema, and model route.

Prefer the least expensive route that clears the quality bar. Use a more
capable model when failure cost dominates token or latency cost.

For ambient automation, stay on flat-rate providers. Use per-token routes for
explicit operator-visible work. Place OpenRouter last unless the workload
requires an OpenRouter-only model.

Completion criterion: The chosen role has one primary route and a rejected
alternative with evidence.

## 5. Build the fallback chain

Each fallback must preserve required tools, input modalities, context, and
minimum reasoning effort. Change provider early enough to survive one provider
outage. Preserve the quality floor before optimizing cost.

For each fallback, state:

- selector and effort;
- what failure activates it;
- capabilities preserved and lost;
- current access and quota;
- provider correlation with earlier routes;
- whether use is automatic or requires operator authorization.

Completion criterion: Every fallback is usable now or explicitly conditional.
The chain has no silent modality, context, tool, or quality downgrade.

## 6. Apply and prove

When the request authorizes a routing change, update the single owning surface:
`modelRoles`, `retry.fallbackChains`, or specialist-agent frontmatter. Do not
duplicate one chain across owners.

Run the installer. Dispatch a representative subagent or workload. Capture its
`resolvedModel` and result. Test fallback activation only through a safe
provider-disable or isolated profile; never damage live credentials.

Return:

```markdown
# Dispatch
- Workload:
- Evidence date:
- Constraints:

## Capability map
## Primary route
## Fallback chain
## Rejected routes
## Benchmark and source table
## Cost, quota, and correlation limits
## Applied change and proof
## Evidence gaps
```

Completion criterion: The recommendation is dated and source-grounded. Applied
selectors resolve in OMP. Every fallback and limitation is visible.