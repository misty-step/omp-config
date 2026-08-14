---
name: model-research
description: Research current OMP model selectors, access, effort, roles, and fallback routes.
---

# Model Research

1. Run `omp models refresh`, then `omp models --json`.
2. Run `omp usage --json --redact`.
3. Enable the OpenRouter MCP server through `/mcp` before querying it, then
   disable the server when the research is complete.
4. Treat OMP as the authority for selectors, effort support, and local access.
5. Use OpenRouter MCP data for OpenRouter routes, prices, endpoints, rankings,
   and benchmarks.
6. Use a provider source for provider capability claims.
7. Record conflicts and follow the source that controls the target interface.

For a role, judge:

- `default`, `task`: coding and tool use;
- `slow`, `reviewer`, `plan`, `advisor`: long-task judgment and defects;
- `designer`, `vision`: design or image input;
- `smol`, `tiny`, `commit`: speed after the quality floor.

For a fallback, preserve required input and effort, use locally accessible
models, change provider near the start, and place an OpenRouter route last.

Return a dated recommendation with selectors, effort, access, evidence, and
limits. Finish only when every selector and effort is valid and every fallback
is usable or explicitly conditional.