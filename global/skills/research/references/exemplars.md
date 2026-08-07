# Research exemplars

## Discover then extract

1. Exa search for candidates.
2. Firecrawl scrape the top primary sources.
3. Cite passages with URLs and dates.

```bash
# 1. discover
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.exa.ai/search \
  -H "x-api-key: __mint.exa.default__" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "OpenRouter tool calling pricing 2026",
    "type": "auto",
    "numResults": 5,
    "startPublishedDate": "2026-01-01",
    "contents": { "text": { "maxCharacters": 800 } }
  }'

# 2. extract one official page
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev/v1/scrape \
  -H "Authorization: Bearer __mint.firecrawl.default__" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://openrouter.ai/docs","formats":["markdown"],"onlyMainContent":true}'
```

## Docs corpus

```bash
# map first
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev/v1/map \
  -H "Authorization: Bearer __mint.firecrawl.default__" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.firecrawl.dev","limit":15}'

# crawl only when map is too large to scrape selectively
# firecrawl-crawl --limit 10 --depth 2 https://docs.example.com
```

## Code reference search

```bash
curl -s http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.exa.ai/search \
  -H "x-api-key: __mint.exa.default__" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "open source agent browser visual regression playwright",
    "type": "auto",
    "numResults": 5,
    "contents": { "text": { "maxCharacters": 1500 } }
  }'
```

## Dynamic page fallback

When scrape returns empty shell HTML:

```bash
agent-browser skills get core
agent-browser open https://example.com/app
agent-browser snapshot
agent-browser close --all
```

## Report minimum

Every exemplar-style answer must include:

- ranked conclusion or decision
- citations with URLs
- retrieval date for volatile facts
- residual uncertainty line
