# Readwise Reader

Query the user's Readwise Reader library for saved articles, highlights, and documents.

## Authentication

Run these commands only from an OMP process launched inside the operator's
Agent Vault wrapper. Configure a service rule for `readwise.io/api/*`; the
rule owns and replaces `Authorization` at the upstream boundary.

```bash
READWISE_BASE_URL="https://readwise.io"
```

Do not set, print, or pass a Readwise credential from agent context. The
commands below use the upstream URL and rely on the approved service rule.

## Core Operations

### Search by Topic

No full-text search endpoint exists. Fetch documents, then filter them client-side.

```bash
curl -s "$READWISE_BASE_URL/api/v3/list/?limit=100" \
  | jq '[.results[] | select(((.title // "") + " " + (.summary // "")) | test("TOPIC"; "i"))]
        | .[] | {title: (.title // "(untitled)"), source_url, summary: (.summary // ""), reading_progress, word_count, saved_at}'
```

Search all locations by default. Add `&location=later` or `&category=article` to narrow.

### List Recent Saves

```bash
curl -s "$READWISE_BASE_URL/api/v3/list/?location=new&limit=20" \
  | jq '.results[] | {title: (.title // "(untitled)"), category, source_url, summary: (.summary // ""), saved_at, word_count}'
```

### List by Category

Categories: `article`, `email`, `rss`, `highlight`, `note`, `pdf`, `epub`, `tweet`, `video`

### List by Location

Locations: `new`, `later`, `shortlist`, `archive`, `feed`

### List Tags

```bash
curl -s "$READWISE_BASE_URL/api/v3/tags/" \
  | jq '.results[] | .name'
```

### Filter by Tag

```bash
curl -s "$READWISE_BASE_URL/api/v3/list/?tag=TAG_NAME&limit=20" \
  | jq '.results[] | {title: (.title // "(untitled)"), source_url, summary: (.summary // "")}'
```

Up to 5 `tag` params allowed. Empty `tag=` finds untagged documents.

### Get Full Content

```bash
curl -s "$READWISE_BASE_URL/api/v3/list/?id=DOCUMENT_ID&withHtmlContent=1" \
  | jq '.results[0].html_content'
```

### Get Highlights

Highlights are documents with `parent_id` pointing to the source document.

```bash
curl -s "$READWISE_BASE_URL/api/v3/list/?category=highlight&limit=100" \
  | jq '[.results[] | select(.parent_id == "DOCUMENT_ID")]
        | .[] | {title: (.title // "(untitled)"), summary: (.summary // ""), notes: (.notes // "")}'
```

## Pagination

The response includes `nextPageCursor`. Loop until null:

```bash
CURSOR=""
while true; do
  PARAMS="limit=100"
  [ -n "$CURSOR" ] && PARAMS="$PARAMS&pageCursor=$CURSOR"
  RESPONSE=$(curl -s "$READWISE_BASE_URL/api/v3/list/?$PARAMS")
  echo "$RESPONSE" | jq '.results[]'
  CURSOR=$(echo "$RESPONSE" | jq -r '.nextPageCursor // empty')
  [ -z "$CURSOR" ] && break
done
```

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| LIST | 20/min |
| CREATE/UPDATE | 50/min |
| BULK UPDATE | 10/min |
| DELETE | 20/min |

On `429`, check `Retry-After` header.

## Workflow Patterns

### Research a Topic
1. Search across all locations for topic keywords
2. Prioritize `shortlist` and `later` (user-curated intent)
3. For promising hits, fetch full content with `withHtmlContent=1`
4. Synthesize findings for the user

### Save Something for Later
```bash
curl -s -X POST "$READWISE_BASE_URL/api/v3/save/" \
  -H "Content-Type: application/json" \
  -d '{"url": "URL", "location": "later", "tags": ["tag1"]}'
```

### Triage Reading List
1. List `new` items
2. Present summaries to user
3. Bulk update locations based on user decisions
