# Disabled MCP mapping

`global/mcp.json` defines only live servers. The `disabledServers` list keeps
server names blocked by policy. Disabled names are not runtime routes.
Do not re-enable them from a skill or workflow.
Prefer these canonical replacements:

| Disabled server | Canonical replacement | Rationale |
|---|---|---|
| `canary` | `misty-canary`, `canary` CLI, or Canary API | The product-owned CLI/API carries operational health and incident queries without an always-on server. |
| `powder` | `powder` CLI or Powder API through the `powder` skill | Powder MCP stays disabled; the CLI/API owns durable work state. |
| `chrome-devtools` | builtin `browser`, `agent-browser` CLI, or `chrome-devtools` CLI | Browser and scored-audit paths are selected per job and do not require standing MCP schemas. |
| `crucible` | Crucible CLI and persisted run records | Evaluation commands own validation, execution, comparison, and evidence. |
| `monologue` | repository search and the owning product CLI/API | No OMP skill has a live Monologue MCP contract; do not invent one. |
| `node_repl` | the repository's declared runtime or `bun`/`node` entrypoint | Runtime execution belongs to the project command, not a global REPL server. |
| `openaiDeveloperDocs` | `web_search` and `read` against official documentation URLs | Current documentation lookup uses the web tools and keeps provider schemas out of every turn. |
| `openrouter` | Mint-brokered OpenRouter catalog/API plus `omp models` | The disabled MCP is not a route; Mint owns credentialed egress and the local catalog command exposes the selected metadata. |
| `qmd` | `grep`, `glob`, `read`, and the local search CLI | Bounded repository search is available without an always-on index server. |

