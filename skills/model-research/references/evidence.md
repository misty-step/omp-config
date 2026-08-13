# Evidence

Use these sources in this order:

1. Use `omp models --json` for OMP selector and effort support.
2. Use `omp usage --json --redact` for local access and limits.
3. Use OpenRouter MCP model and endpoint tools for live route data.
4. Use OpenRouter MCP benchmark and ranking tools for current comparisons.
5. Use [Artificial Analysis](https://artificialanalysis.ai/agents/coding-agents) for coding-agent results.
6. Use [Snorkel](https://snorkel.ai/leaderboard/agentic-coding) for agentic coding and terminal results.
7. Use a provider model card for a capability claim.

Read the schema for each tool before first use. Use only
`mcp__openrouter_get_model`, `mcp__openrouter_list_model_endpoints`,
`mcp__openrouter_list_benchmarks`, `mcp__openrouter_list_daily_model_rankings`,
`mcp__openrouter_list_app_rankings`, `mcp__openrouter_list_task_classifications`,
and `mcp__openrouter_search_docs`. Get operator approval before you use any
other OpenRouter MCP tool.

Record the source URL, model ID, test harness, test date, and retrieval date.
Keep conflicting results separate.