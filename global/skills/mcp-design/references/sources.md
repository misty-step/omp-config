# MCP Design Sources

Accessed: 2026-07-08.

## Primary Sources

- Anthropic, "Writing effective tools for agents - with agents", published
  2025-09-11, https://www.anthropic.com/engineering/writing-tools-for-agents.
  Took: intent-shaped tools over API mirrors, namespacing, `response_format`
  detail enums, pagination/filtering/truncation defaults, approximate 25k-token
  response caps, steering errors/truncation, and eval-before-shipping discipline.
- Anthropic, "Code execution with MCP: Building more efficient agents",
  published 2025-11-04,
  https://www.anthropic.com/engineering/code-execution-with-mcp. Took: tool
  schema load and intermediate results are the two bloat sources; progressive
  disclosure and filtering before data reaches the model are first-class design
  moves; code/harness offload is useful for large intermediate data.
- Model Context Protocol specification, version 2025-06-18,
  https://modelcontextprotocol.io/specification/2025-06-18. Took: initialize
  `instructions`, `tools/list` pagination, `outputSchema`, `structuredContent`,
  and `isError` tool execution errors.
- Philipp Schmid, "MCP is Not the Problem, It's your Server: Best Practices for
  Building MCP Servers", published 2026-01-21,
  https://www.philschmid.de/mcp-best-practices. Took: MCP as UI for agents,
  outcomes over operations, flat args, instructions/errors as context, 5-15 tool
  curation, persona split, discovery naming, and `limit` default 20-50 with
  pagination metadata.
- Sam Morrow, "MCP Doesn't Have a Context Problem", published 2026-05,
  https://sam-morrow.com/blog/progressive-discovery-in-mcp-part-1. Took:
  default tool count reduction, prompt-cache cost of dynamic toolset changes,
  progressive discovery as harness concern, and large-output disk offloading as
  harness/client concern.
- GitHub MCP Server PR #2016, opened 2026-02-16 and closed 2026-02-25,
  https://github.com/github/github-mcp-server/pull/2016. Took: measured list
  optimization tactics: flatten nested objects, remove URLs, remove zero values,
  normalize whitespace, summarize collections, filter low-fill fields, and
  validate with cross-model evals. Note: public API reports this PR closed
  without merge; use it as design evidence, not release state.
- GitHub MCP Server release v0.32.0, published 2026-03-06,
  https://github.com/github/github-mcp-server/releases/tag/v0.32.0. Took:
  released context reductions across list/read outputs.
- GitHub MCP Server PR #2512, merged 2026-05-20,
  https://github.com/github/github-mcp-server/pull/2512. Took: server-side
  dynamic toolsets were deleted after adding complexity and depending on local
  configuration; discovery belongs in the harness/client.
- GitHub MCP Server release v1.1.0, published 2026-05-28,
  https://github.com/github/github-mcp-server/releases/tag/v1.1.0. Took: compact
  CSV/list output, context-reduced project item responses, GHAS alert
  pagination, and `isError` validation failures that help agents self-correct.
- getsentry/sentry-mcp README, fetched from main on 2026-07-08,
  https://github.com/getsentry/sentry-mcp. Took: persona-scoped server design
  for human-in-the-loop coding agents and query-param tool narrowing via
  `skills=` / `disable-skills=`.

## Public Skill Comparison

- `anthropics/skills` search, 2026-07-08: found skills that teach agents to use
  specific MCP servers (FlowStudio, TensorFeed, BotSpot) and proposals for
  skills-over-MCP. Took: specific-server skills should document response shapes
  and prerequisites. Rejected: none provided general MCP server design judgment.
- `ComposioHQ/awesome-claude-skills/mcp-builder`, fetched 2026-07-08. Took:
  eval-driven development, workflow-not-endpoint advice, and response-format
  planning. Rejected: phase-heavy SDK build procedure, broad documentation
  imports, and generic implementation checklists that dilute design judgment.
- `eduardoremedios/mcp-builder-skill`, fetched 2026-07-08. Took: public demand
  for a production MCP builder skill. Rejected: very large monolithic guide and
  SDK-specific examples; this roster skill stays design-first and stack-neutral.
- `mcp-use/skills` `mcp-builder`, fetched 2026-07-08. Took: framework-specific
  quick-start and inspector-test emphasis as useful when already using mcp-use.
  Rejected: framework coupling and widget/app details outside this skill's job.
- `rahmanef63/mcp-skill` / `chatgpt-mcp`, fetched 2026-07-08. Took:
  battle-tested gotchas, tool descriptions as prompt context, schema/dispatcher
  drift warning, and "always allow" as host UX rather than server flag. Rejected:
  OAuth/Convex/Next.js implementation phases as too product-specific.
- `mcp2skill`, `mcp-to-skill`, `skills-mcp`, and related repos, fetched
  2026-07-08. Took: progressive disclosure and inspection tooling are useful.
  Rejected: automatic conversion tends to preserve an existing tool surface; it
  does not replace design review.

## Unverified Prompt Item

The requested "GitHub MCP Server changelog 2025-10-29" was not found in public
GitHub releases, GitHub code search, or web search on 2026-07-08. The closest
verified public release evidence for the same design direction is v0.32.0
(2026-03-06) and v1.1.0 (2026-05-28). Do not cite the 2025-10-29 changelog
until a stable URL is available.
