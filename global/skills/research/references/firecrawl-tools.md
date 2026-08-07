# Firecrawl tools

Firecrawl turns known URLs and site trees into clean agent-readable text.

## Access

OMP server: `firecrawl-mint` in `global/mcp.json`.

Local MCP: `global/skills/research/scripts/firecrawl_mcp_stdio.py`  
REST via Mint: `http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev`  
Marker: `Authorization: Bearer __mint.firecrawl.default__`

Never set a raw `FIRECRAWL_API_KEY` in an agent environment.

Remote hosted Firecrawl MCP is not used here. Mint auth does not attach cleanly to that host. This local server calls the REST API through Mint.

## MCP tools

| Tool | Use |
|---|---|
| `firecrawl_scrape` | one known URL → markdown or structured fields |
| `firecrawl_map` | discover URLs under a docs root |
| `firecrawl_crawl` | bounded multi-page crawl with required `limit` |
| `firecrawl_search` | page-backed web search when Exa is weak or unavailable |

## CLI fallbacks

Script: `global/skills/research/scripts/firecrawl_tools.py`

```bash
SCRIPT="${HOME}/.omp/agent/skills/research/scripts/firecrawl_tools.py"
python3 "$SCRIPT" firecrawl-scrape https://example.com
python3 "$SCRIPT" firecrawl-map --limit 20 https://docs.example.com
python3 "$SCRIPT" firecrawl-search --limit 5 "site:docs.example.com auth"
python3 "$SCRIPT" firecrawl-crawl --limit 10 --depth 2 https://docs.example.com/docs
```

REST examples:

```bash
# scrape
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev/v1/scrape \
  -H "Authorization: Bearer __mint.firecrawl.default__" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","formats":["markdown"],"onlyMainContent":true}'

# map
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev/v1/map \
  -H "Authorization: Bearer __mint.firecrawl.default__" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.example.com","limit":20}'

# search
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev/v1/search \
  -H "Authorization: Bearer __mint.firecrawl.default__" \
  -H "Content-Type: application/json" \
  -d '{"query":"firecrawl scrape formats","limit":5}'
```

## Routing

| Need | Tool | Bound |
|---|---|---|
| Read this URL | `firecrawl_scrape` | one URL |
| List docs pages | `firecrawl_map` | `limit` |
| Ingest a small docs tree | `firecrawl_crawl` | `limit` and depth |
| Search then read | Exa or Firecrawl search, then scrape | top N only |

## Rules

1. Prefer Exa to discover. Prefer Firecrawl to extract.
2. Always bound map and crawl with `limit`. Default crawl wait is on; do not start unbounded crawls.
3. Keep source URLs with every extract. A summary without a URL is not evidence.
4. Prefer official docs and repo-local files before paid extraction.
5. If scrape returns empty or broken content on a JS app, escalate to `browser` or `agent-browser`.
6. Do not use Firecrawl for interactive QA, form flows, or visual proof.
