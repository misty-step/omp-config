---
name: mcp-design
description: |
  Design or review MCP server tool surfaces for agent usability: tool catalog shape, schemas/descriptions, response payloads, server instructions, token budget, and eval gates. Use when building an MCP server, auditing MCP tools, reducing tool schema/output context, deciding list/read/write split, consolidating CRUD tools, persona-splitting toolsets, or debugging agents choosing MCP tools poorly. Trigger: /mcp-design, /mcp-tools, /mcp-review.
argument-hint: "[server|catalog|diff] [--design|--audit|--shrink|--eval]"
---

# /mcp-design

An MCP server is a model interface, not an API wrapper. Design the default path
as a **scan** surface: the agent finds the right object with little context, then
reads detail intentionally.

The dated source canon and public-skill comparison live in
[`references/sources.md`](references/sources.md). Load it when defending a
contested rule, refreshing the research base, or comparing this skill to public
MCP builder skills.

## Start

1. Name the agent persona and job. One server should serve one coherent job;
   split admin, end-user, coding-agent, and debugging personas when their
   default tools or risk differ.
2. Inventory the live surface. Capture `tools/list`, initialize
   `instructions`, representative `tools/call` outputs, and current
   token/byte counts. If the server does not exist yet, sketch the intended
   tool catalog and response shapes.
3. Classify each user task as **scan**, **read**, or **write**. Scan returns
   enough to choose. Read returns bounded detail. Write returns result plus the
   next safe read, not a full object dump.
4. Pick the smallest default toolset that covers the persona's frequent jobs.
   Treat 5-15 tools as the starting range; exceed it only with eval or
   production-call evidence.

Done means the proposed catalog names its persona, default tools,
scan/read/write contracts, growth bounds, and proof loop.

## Tool Surface

Design for outcomes, not operations.

- Prefer intent-shaped tools that collapse a common multi-step workflow:
  `schedule_event`, `get_customer_context`, `search_logs`.
- Keep low-level operations only when the agent must compose them and their
  outputs stay small.
- Use service/resource namespacing that survives neighboring servers:
  `github_issue_search`, `sentry_event_read`, `powder_card_update`. If the
  client already prefixes by server, keep the tool name resource/action-specific.
- Consolidate sibling CRUD operations with a typed `method` or `action`
  parameter when the operation family shares arguments and mental model. Split
  when write risk, required args, or return shape diverges.
- Split by persona before adding server-side dynamic discovery. Server-side
  dynamic toolset enablement usually breaks prompt-cache stability and depends
  on users configuring the server. Put discovery in the harness/client; make the
  server expose stable curated toolsets.
- Do not mirror REST. A REST endpoint map optimizes human developers who read
  docs once; MCP schema sits in the model context every session.

## Schemas And Descriptions

Every schema token is context tax.

- Flatten inputs into primitive fields, arrays of primitives, and
  `enum`/`Literal` choices. Avoid nested filter bags unless the nested shape is
  the product object the agent naturally manipulates.
- Give defaults for safe common cases: `limit: 20`, `detail: "summary"`,
  `include_archived: false`.
- Describe when to use the tool, how to format arguments, and what the response
  contains. Tool descriptions are steering text, not API docs.
- Prefer stable semantic identifiers in scan results. Include opaque ids only
  when the next tool requires them.
- Use `outputSchema` / `structuredContent` when deterministic clients or evals
  need validation. Still consider a compact text or Markdown rendering if the
  target model performs better with it; format is an eval question, not a
  principle.
- Keep examples tiny and discriminating. One example that prevents a likely
  wrong call beats a long usage section.

## Response Design

The list contract is strict: **list output is a subset of get output**. Lists
help choose; gets explain.

| Surface | Return | Exclude |
|---|---|---|
| `*_search` / `*_list` | id, title/name, state, timestamps/source, 1-line summary, matching highlights, pagination | body text, duplicated criteria, full nested objects, URLs not needed for next calls |
| `*_read` / `*_get` | bounded detail plus links/ids needed for follow-up | unbounded histories, always-null fields, pretty-print bloat |
| `*_write` | success/failure, changed id, important side effects, suggested read call | the full updated object unless it is tiny |

Response rules:

- Bound everything that grows: histories, comments, logs, work notes,
  attachments, timelines, Markdown bodies.
- Paginate with default 20-50 items and metadata: `has_more`, `next_cursor` or
  `next_offset`, and `total_count` when cheap. If truncated, say exactly what
  was omitted and which next call continues.
- Filter before bytes reach the model. Add server-side search/filter parameters
  for common scans; use code execution or harness offload for large intermediate
  datasets when available.
- Remove zero values, nulls, empty arrays, default booleans, repeated criteria,
  pretty-print whitespace, and decorative URLs. Compact serialization is a
  product feature.
- Add `detail`/`response_format` only when agents actually need both shapes.
  Default to summary. Make `detailed` opt-in.
- Return errors with the correction path: which argument failed, valid enum
  values, smaller limit/filter suggestion, or a specific read/search
  alternative. Opaque stack traces teach nothing.

### Powder Case Study

A 2026-07 audit of the Powder work-board MCP found the canonical failure
pattern:

- 31 tools cost about 2.6k schema tokens per session before any work.
- `list(20)` returned about 14k tokens and `list(50)` about 31.5k because lists
  returned full card objects.
- 56% of list bytes were the same criteria text serialized twice; about 8% were
  always-null fields; pretty JSON added 16%.
- Detail reads were unbounded while product doctrine encouraged frequent
  work-log appends.
- Fields needed for scan decisions were only about 10% of the payload.

Lessons: drive the server over stdio, count bytes by field, separate scan/read
intents, delete duplication/nulls first, and bound every append-only surface.

## Server Instructions

Use initialize `instructions` as a short operating contract, not documentation.
Aim near 300 tokens.

Include:

- What this server is for and the persona it serves.
- The default scan -> read -> write flow.
- Safety/approval boundaries and destructive-tool handling.
- Pagination/truncation rules and how to continue.
- Naming conventions or IDs the agent must preserve.
- One line telling the agent to prefer filters/smaller reads over broad dumps.

Do not put the whole tool catalog in instructions; tools already carry
descriptions.

## Measure And Eval

A design change is not better until driven through a loop.

- Schema budget: serialize `tools/list`; count total tokens and per-tool schema
  tokens.
- Output budget: call representative scan/read/write tools over stdio; record
  bytes/tokens by top-level field and by repeated text.
- Task eval: run realistic prompts against old vs new surface. Grade task
  success, wrong-tool rate, calls per task, total tokens, truncation recovery,
  and error self-correction.
- Format eval: compare JSON, XML, Markdown, CSV, and `structuredContent` where
  relevant. Different models prefer different shapes.
- Regression rule: any tool rename, consolidation, list shape change, or
  default-detail change needs a paired eval or production transcript
  comparison. Keep aliases only where compatibility requires them, and measure
  alias confusion.

Minimal stdio audit shape:

```text
tools/list -> schema_tokens_by_tool
tools/call(search/list fixtures) -> bytes_by_field, tokens_total, truncation flags
tools/call(read fixtures) -> max growth path, append-only fields, duplicate text
```

## Anti-Patterns

| Anti-pattern | Better design |
|---|---|
| REST mirror: one tool per endpoint | Outcome tools plus scan/read/write contracts |
| All tools on by default | Persona-scoped default set; harness/client discovery for the rest |
| Server-side dynamic discovery toggles | Stable toolsets; discovery outside the server |
| List returns full objects | List subset of get; summary shapes |
| Nested filter bags | Flat args, enums, defaults |
| Unbounded detail read | `detail`, pagination, limits, or resource/file offload |
| Pretty JSON as default | Compact structured output; pretty only for human display |
| Duplicate query criteria in every row | Top-level criteria once, row-specific data per item |
| Null/default field flood | Omit zero-value fields unless semantically meaningful |
| Errors as stack traces | Errors that steer the next valid call |
| Format chosen by taste | Paired task eval by model/client |
| Tool count justified by API breadth | Tool count justified by persona tasks and evals |
