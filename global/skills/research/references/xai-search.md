# xAI Search

Grounded web search and X (Twitter) search via the xAI Grok API.

## Two Tools

### Web Search (`web_search`)
Grounded web search with optional image understanding.

### X Search (`x_search`)
Keyword, semantic, user, and thread search on X. Real-time social data.

## When to Use

| Need | Tool |
|------|------|
| Grounded live web retrieval | Web Search |
| Recency verification or contradiction check | Web Search |
| Social sentiment, public discourse | X Search |
| What people are saying about X | X Search |
| Trending topics, viral content | X Search |
| Specific user's posts/opinions | X Search with `allowed_x_handles` |
| Web search with image analysis | Web Search with `enable_image_understanding` |
| Video content analysis from X | X Search with `enable_video_understanding` |
| General web with domain filtering | Web Search with `allowed_domains` |

Use xAI alongside Exa in the default `/research` fanout, not instead of it.
Use xAI/Grok for grounded web retrieval, recency verification, contradiction
checks, X-native discourse, and multimodal web/social evidence.
Do not limit Grok to social sentiment.

## API Access

Set `XAI_BASE_URL` to `${MINT_BASE_URL}/proxy/https/api.x.ai/v1`.
The runtime rejects direct-vendor, alternate-origin, query-bearing, and
sibling-path values.
Auth: `Authorization: Bearer __mint.xai.default__`
Use the OpenAI Responses API-compatible interface.
The default model is `grok-4.3` unless the environment overrides it.

## Web Search

```bash
curl "${XAI_BASE_URL:?set XAI_BASE_URL to Mint's xAI proxy route}/responses" \
  -H "Content-Type: application/json" \
  -H "$(printf '%s: Bearer %s' Authorization __mint.xai.default__)" \
  -d '{
  "model": "grok-4.3",
  "input": [{"role": "user", "content": "What is the latest on AI regulation?"}],
  "tools": [{"type": "web_search"}]
}'
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `allowed_domains` | Only search within specific domains (max 5) |
| `excluded_domains` | Exclude specific domains from search (max 5) |
| `enable_image_understanding` | Analyze images found during browsing |

### Domain filtering
```json
{"type": "web_search", "filters": {"allowed_domains": ["arxiv.org", "github.com"]}}
```

### Image understanding
```json
{"type": "web_search", "enable_image_understanding": true}
```

## X Search

```bash
curl "${XAI_BASE_URL:?set XAI_BASE_URL to Mint's xAI proxy route}/responses" \
  -H "Content-Type: application/json" \
  -H "$(printf '%s: Bearer %s' Authorization __mint.xai.default__)" \
  -d '{
  "model": "grok-4.3",
  "input": [{"role": "user", "content": "What are people saying about Claude 4?"}],
  "tools": [{"type": "x_search"}]
}'
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `allowed_x_handles` | Only posts from specific handles (max 10) |
| `excluded_x_handles` | Exclude posts from handles (max 10) |
| `from_date` | Start date, ISO8601 `YYYY-MM-DD` |
| `to_date` | End date, ISO8601 `YYYY-MM-DD` |
| `enable_image_understanding` | Analyze images in posts |
| `enable_video_understanding` | Analyze videos in posts (X Search only) |

### Handle filtering
```json
{"type": "x_search", "allowed_x_handles": ["kaborek", "AnthropicAI"]}
```

### Date range
```json
{"type": "x_search", "from_date": "2025-03-01", "to_date": "2025-03-15"}
```

### Multimodal
```json
{"type": "x_search", "enable_image_understanding": true, "enable_video_understanding": true}
```

## SDK Usage

### OpenAI-compatible Python
```python
from openai import OpenAI

client = OpenAI(api_key="__mint.xai.default__", base_url=os.environ["XAI_BASE_URL"])

response = client.responses.create(
    model="grok-4.3",
    input=[{"role": "user", "content": query}],
    tools=[{"type": "x_search"}],  # or "web_search"
)
```

Omit the Vercel xAI provider and xAI native SDK examples.
The versions evaluated for this integration do not expose the base-URL seam required to force every request through Mint.
Use the OpenAI-compatible client or the built-in provider above.

## Citations

Responses include `response.citations` with source URLs. Always cite them.

## Integration Notes

- Both tools can be used in the same request.
- `enable_image_understanding` on Web Search also enables it for X Search.
- Use `enable_video_understanding` only with X Search.
- Do not combine `allowed_domains` and `excluded_domains` in one request.
- Do not combine `allowed_x_handles` and `excluded_x_handles` in one request.
- In this harness runtime, use xAI as a retrieval/discourse provider when
  `XAI_BASE_URL` is set.
- Route it before Exa for social/discourse queries and after Exa for recency corroboration.
