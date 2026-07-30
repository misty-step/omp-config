# Default Fanout

Multi-source triangulation for substantive research.

## Use

Load this reference when the user asks for broad research, comparison, architecture prior art, or model/provider investigation.
Also load it for "what are people saying" or any question where a single lookup would overfit one source.

Use single-source research only when the user names the source or requests a narrow fact/version lookup.

## Context Packet

Capture the packet before launching lanes:

- Objective: fact lookup, prior-art scan, architecture comparison, discourse
  scan, or decision support.
- Scope: repos, files, domains, products, dates, jurisdictions, or excluded
  areas.
- Freshness tolerance: latest/current, date-bounded, or stable background.
- Acceptance oracle: decision to support, risk to refute, artifact to produce,
  or explicit absence.
- Tool constraints: unavailable credentials, provider limits, offline mode, or
  user-named sources.

## Source Invariant

Account for these capability lanes in default research.
Run a lane when relevant; otherwise keep it in the matrix as `skipped` with the reason.

| Lane | Capability | Primary refs |
|---|---|---|
| Codebase | live repo patterns, existing contracts, local prior art | `rg`, `git`, local files |
| Docs | library/API docs and official references | Context7, official docs, `web-search.md` |
| Retrieval | web, papers, reference implementations | `web-search.md`, `exa-tools.md` |
| Agentic acquisition | optional async broad research, list building, entity enrichment | `web-search.md`, `exa-tools.md` |
| Extraction | known URL fetch, page extraction, site maps, crawls | `exa-tools.md`, `extraction-tools.md`, `/browser` |
| Recency / discourse | current web, X/social discourse, contradiction checks | `xai-search.md` |
| Synthesis | concise answer over gathered evidence | Perplexity/Exa deep/lead synthesis |
| Repo-aware critique | local fit, architecture tradeoffs, second opinion | `delegate.md` |

If a lane fails, times out, lacks credentials, or is intentionally skipped by scope, keep its section and label its status.
Do not silently collapse failed lanes into synthesis.

Capability lanes do not replace the roster floor.
For substantive research, follow the chief contract in `../../../AGENTS.md` unless a documented waiver applies.

## Capability Routing

For each capability, prefer the most agent-native verified surface.
Use MCP tool first, local CLI wrapper second, direct REST/API call third, and
built-in WebSearch last.
Report substitutions explicitly.
Keep the local wrapper surface intentionally thin and JSON-emitting when installed:
`exa-search`, `exa-fetch`, `brave-search`, `firecrawl-fetch`, and
`xai-search web|x`. MCP-only surfaces such as `parallel-search` still belong
at the first step in the chain.

| Intent | Prefer | Fallback |
|---|---|---|
| Local repo truth | `rg`, git, local files | user-provided context |
| Code examples or reference implementations | Exa code context | GitHub/source search, web search |
| Library docs or API usage | docs capability such as Context7 | official docs via web search |
| Known URL or generated docs extraction | Exa fetch / Firecrawl scrape | browser agent |
| Site discovery, sitemap, or crawl | Tavily/Firecrawl map/crawl | browser/manual link walk |
| Broad multi-hop research, entity enrichment, or list building | Optional Exa Agent lane for `web-deep` | Exa deep / lead synthesis |
| Model releases, pricing, CVEs, deprecations | recency-filtered web/xAI | Exa recency, official sources |
| Social sentiment or public discourse | xAI X Search | web results that cite public posts |
| Grounded answer synthesis | Perplexity/Exa deep after retrieval | lead synthesis over cited sources |
| Repo architecture or local tradeoffs | roster lanes | scoped grep plus lead analysis |
| Saved user reading/highlights | Readwise | local notes or explicit web search |

Route by capability.
Treat vendor names as implementation details.
If a named provider is unavailable, use the closest source and report the substitution.
Do not add a vendor to the prose unless a script, command recipe, or explicit manual fallback can invoke it.

## Report Shape

Use this shape for default fanout reports:

```markdown
## Synthesis
[Lead conclusion, confidence, decision impact, and residual uncertainty.]

## Source Matrix
| Source lane | Status | What it contributed | Key refs |
|---|---|---|---|
| Codebase | complete/partial/failed/skipped | ... | file:line/commands |
| Docs | complete/partial/failed/skipped | ... | URLs/artifacts |
| Retrieval | complete/partial/failed/skipped | ... | URLs/artifacts |
| Agentic acquisition | complete/partial/failed/skipped | ... | `response.agentic`, run id, URLs/artifacts |
| Extraction | complete/partial/failed/skipped | ... | URLs/artifacts |
| Recency / discourse | complete/partial/failed/skipped | ... | URLs/citations |
| Synthesis | complete/partial/failed/skipped | ... | citation refs |
| Repo-aware critique | complete/partial/failed/skipped | ... | receipt ids/output dir |

## Conflicts
[Disagreements across sources and the lead's resolution.]

## Evidence
[Grouped citations, commands, receipts, local files, or artifacts.]

## Residual Risk
[Stale facts, missing providers, unqueried sources, or none with reason.]
```

For source-heavy reports, keep per-source detail below the matrix.
Readers must identify each lane's independent contribution.

## Failure Labels

- `complete`: lane produced usable evidence inside scope.
- `partial`: lane started but only some artifacts or results exist.
- `failed`: lane was attempted and produced no usable evidence.
- `skipped`: lane was out of scope, user-forbidden, or impossible due missing
  credentials/tooling.
- `stale`: evidence may be outdated for the requested freshness tolerance.

Test every recommendation without the weakest source.
If it fails, label the recommendation low confidence.
