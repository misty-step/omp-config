# Exa tools

Exa finds and ranks technical sources. Use it for discovery. Use Firecrawl to extract known pages.

## Access

CLI: `exa-search` and `exa-fetch` (symlinked to `global/skills/research/scripts/exa_tools.py`).

REST proxy: `http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.exa.ai`  
Marker: `x-api-key: __mint.exa.default__`

Never set a raw `EXA_API_KEY` in an agent environment.

## CLI and REST

Script: `global/skills/research/scripts/exa_tools.py`

```bash
exa-search --num 5 "YOUR QUERY"
exa-fetch --chars 2000 https://example.com/page
```

```bash
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.exa.ai/search \
  -H "x-api-key: __mint.exa.default__" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "YOUR QUERY",
    "type": "auto",
    "numResults": 5,
    "contents": { "text": { "maxCharacters": 1000 } }
  }'
```

## Modes

| Need | Mode |
|---|---|
| How does X implement Y? | search with code-oriented query |
| Current best practice | auto + `startPublishedDate` |
| Papers or specs | neural/auto search |
| Pages like this URL | `findSimilar` |
| Known URL text | prefer Firecrawl scrape; Exa fetch is fallback |

### Recency filter

```bash
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.exa.ai/search \
  -H "x-api-key: __mint.exa.default__" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "OpenRouter model pricing",
    "type": "auto",
    "numResults": 5,
    "startPublishedDate": "2026-01-01",
    "contents": { "text": { "maxCharacters": 1000 } }
  }'
```

### Find similar

```bash
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.exa.ai/findSimilar \
  -H "x-api-key: __mint.exa.default__" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/good-reference",
    "numResults": 5,
    "contents": { "text": { "maxCharacters": 1000 } }
  }'
```

## Rules

- Cite every Exa URL you use.
- Treat snippets as leads. Extract the page when the claim matters.
- Provider chain: Exa CLI/REST → Parallel Search.
