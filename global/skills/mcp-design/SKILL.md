---
disable-model-invocation: true
name: mcp-design
description: >
  Design or review MCP server tool surfaces for agent usability: catalogs,
  schemas, response payloads, instructions, token budgets, and eval gates.
  Use for MCP construction, audits, context reduction, scan/read/write design,
  CRUD consolidation, persona toolsets, or tool-choice debugging.
  Trigger: /mcp-design, /mcp-tools, /mcp-review.
argument-hint: "[server|catalog|diff] [--design|--audit|--shrink|--eval]"
---

# /mcp-design

An MCP server is a model interface, not an API wrapper.
Design the default path as a **scan** surface.
Let the agent find the right object with little context, then read detail
intentionally.

The dated source canon and public-skill comparison live in
[`references/sources.md`](references/sources.md).
Load it to defend a contested rule, refresh the research base, or compare this
skill with public MCP builder skills.

## Start

1. Name the agent persona and job.
   Make each server serve one coherent job.
   Split admin, end-user, coding-agent, and debugging personas when their
   default tools or risk differ.
2. Inventory the live surface.
   Capture `tools/list`, initialize `instructions`, representative `tools/call`
   outputs, and current token/byte counts.
   If the server does not exist, sketch the intended tool catalog and response
   shapes.
3. Classify each user task as **scan**, **read**, or **write**.
   Make scan return enough to choose.
   Make read return bounded detail.
   Make write return the result plus the next safe read, not a full object dump.
4. Pick the smallest default toolset for the persona's frequent jobs.
   Start with 5-15 tools. Exceed that range only with eval or production-call
   evidence.

Done means the proposed catalog names its persona and default tools.
It also defines scan/read/write contracts, growth bounds, and a proof loop.

## Tool Surface

Design for outcomes, not operations.

- Prefer intent-shaped tools that collapse a common multi-step workflow:
  `schedule_event`, `get_customer_context`, `search_logs`.
- Keep low-level operations only when the agent must compose them and their
  outputs stay small.
- Use service/resource namespacing that survives neighboring servers:
  `github_issue_search`, `sentry_event_read`, `powder_card_update`.
  If the client prefixes by server, keep the tool name resource/action-specific.
- Consolidate sibling CRUD operations with a typed `method` or `action` parameter
  when the operation family shares arguments and a mental model.
  Split the family when write risk, required arguments, or return shape diverge.
- Split by persona before adding server-side dynamic discovery.
  Dynamic toolset enablement usually breaks prompt-cache stability and depends
  on user configuration.
  Put discovery in the harness/client. Make the server expose stable curated
  toolsets.
- Do not mirror REST.
  A REST endpoint map serves human developers who read docs once.
  MCP schema sits in the model context every session.

## Schemas And Descriptions

Every schema token is context tax.

- Flatten inputs into primitive fields, arrays of primitives, and
  `enum`/`Literal` choices.
  Avoid nested filter bags unless the nested shape is the product object the
  agent naturally manipulates.
- Give defaults for safe common cases: `limit: 20`, `detail: "summary"`,
  `include_archived: false`.
- Describe when to use the tool, how to format arguments, and what the response
  contains.
  Tool descriptions steer the agent; they are not API docs.
- Prefer stable semantic identifiers in scan results.
  Include opaque ids only when the next tool requires them.
- Use `outputSchema` / `structuredContent` when deterministic clients or evals
  need validation.
  Add a compact text or Markdown rendering when the target model performs
  better with it. Treat format as an eval question, not a principle.
- Keep examples tiny and discriminating.
  One example that prevents a likely wrong call beats a long usage section.

## Response Design

The list contract is strict: **list output is a subset of get output**.
Lists help the agent choose. Gets explain.

| Surface | Return | Exclude |
|---|---|---|
| `*_search` / `*_list` | id, title/name, state, timestamps/source, 1-line summary, matching highlights, pagination | body text, duplicated criteria, full nested objects, URLs not needed for next calls |
| `*_read` / `*_get` | bounded detail plus links/ids needed for follow-up | unbounded histories, always-null fields, pretty-print bloat |
| `*_write` | success/failure, changed id, important side effects, suggested read call | the full updated object unless it is tiny |

Response rules:

- Bound every growing surface: histories, comments, logs, work notes,
  attachments, timelines, and Markdown bodies.
- Paginate with default 20-50 items and metadata: `has_more`, `next_cursor` or
  `next_offset`, and `total_count` when cheap.
  If you truncate output, say exactly what you omitted and which next call
  continues.
- Filter before bytes reach the model.
  Add server-side search/filter parameters for common scans.
  Use code execution or harness offload for large intermediate datasets when
  available.
- Remove zero values, nulls, empty arrays, default booleans, repeated criteria,
  pretty-print whitespace, and decorative URLs.
  Compact serialization is a product feature.
- Add `detail`/`response_format` only when agents need both shapes.
  Default to summary. Make `detailed` opt-in.
- Return errors with a correction path.
  Name the failed argument, valid enum values, a smaller limit/filter suggestion,
  or a specific read/search alternative.
  Opaque stack traces teach nothing.

### Powder Case Study

A 2026-07 audit of the Powder work-board MCP found this canonical failure pattern:

- 31 tools cost about 2.6k schema tokens per session before any work.
- `list(20)` returned about 14k tokens and `list(50)` about 31.5k.
  Lists returned full card objects.
- 56% of list bytes repeated the same criteria text; about 8% were always-null
  fields; pretty JSON added 16%.
- Detail reads were unbounded while product doctrine encouraged frequent
  work-log appends.
- Fields needed for scan decisions were only about 10% of the payload.

Apply these lessons: drive the server over stdio, count bytes by field, separate
scan/read intents, delete duplication/nulls first, and bound every append-only
surface.

## Server Instructions

Use initialize `instructions` as a short operating contract, not documentation.
Aim near 300 tokens.

Include:

- What this server is for and which persona it serves.
- The default scan -> read -> write flow.
- Safety and approval boundaries, plus destructive-tool handling.
- Pagination and truncation rules, including how to continue.
- Naming conventions or IDs that the agent must preserve.
- One line that tells the agent to prefer filters or smaller reads over broad
  dumps.

Do not put the whole tool catalog in instructions.
Tools already carry descriptions.

## Measure And Eval

A design change is not better until you drive it through a loop.

- **Schema budget:** Serialize `tools/list`.
  Count total tokens and per-tool schema tokens.
- **Output budget:** Call representative scan/read/write tools over stdio.
  Record bytes/tokens by top-level field and repeated text.
- **Task eval:** Run realistic prompts against the old and new surfaces.
  Grade task success, wrong-tool rate, calls per task, total tokens,
  truncation recovery, and error self-correction.
- **Format eval:** Compare JSON, XML, Markdown, CSV, and `structuredContent`
  where relevant. Different models prefer different shapes.
- **Regression rule:** Pair an eval or production transcript for any tool rename,
  consolidation, list shape change, or default-detail change.
  Keep aliases only when compatibility requires them.
  Measure alias confusion.

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
