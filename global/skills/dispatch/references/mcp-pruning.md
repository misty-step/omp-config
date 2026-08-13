# Disabled MCP mapping

`global/mcp.json` defines only live servers. The `disabledServers` list keeps
server names blocked by policy. Disabled names are not runtime routes.
Do not re-enable them from a skill or workflow.

## Live research servers

| Server | Role |
|---|---|
| `firecrawl-mint` | Firecrawl scrape, map, crawl, search through Mint REST |
| `parallel-search` | Parallel web search MCP |

Prefer these canonical replacements for disabled names:

| Disabled server | Canonical replacement | Rationale |
|---|---|---|
| `canary` | `misty-canary`, `canary` CLI, or Canary API | The product-owned CLI/API carries operational health and incident queries without an always-on server. |
| `chrome-devtools` | builtin `browser` or `agent-browser` CLI | Browser paths are selected per job; no standing DevTools MCP. |
| `crucible` | Crucible CLI and persisted run records | Evaluation commands own validation, execution, comparison, and evidence. |
| `monologue` | repository search and the owning product CLI/API | No OMP skill has a live Monologue MCP contract; do not invent one. |
| `node_repl` | the repository's declared runtime or `bun`/`node` entrypoint | Runtime execution belongs to the project command, not a global REPL server. |
| `openaiDeveloperDocs` | Exa, Firecrawl, and `read` against official documentation URLs | Current documentation lookup uses research tools and keeps provider schemas out of every turn. |
| `openrouter` | Mint-brokered OpenRouter catalog/API plus `omp models` | The disabled MCP is not a route; Mint owns credentialed egress and the local catalog command exposes the selected metadata. |
| `qmd` | `grep`, `glob`, `read`, and the local search CLI | Bounded repository search is available without an always-on index server. |

