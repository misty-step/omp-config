---
name: research
description: |
  Research current facts through primary sources, independent angles, and
  auditable evidence. Use for bounded lookup, comparison, model selection,
  discourse analysis, or delegated external research. Trigger: /research.
argument-hint: "[query|web|extract|map|crawl|delegate] [args]"
---

# /research

Research one question through evidence another reviewer can audit.

## Evidence contract

1. Frame two to four independent angles. Each angle needs a distinct claim, source path, or falsifier.
2. Prefer primary sources: official docs, specs, repos, release notes, direct measurements, first-party records.
3. Read the source behind each consequential claim. Capture the supporting passage, stable URL or path, publication date when available, and retrieval date.
4. Triangulate consequential and fast-changing claims across independent publishers or source types. Preserve conflicts.
5. Separate observed facts, source claims, inferences, and recommendations.
6. Date facts that can change: availability, prices, versions, benchmarks, policies.
7. Record rejected evidence and the reason.
8. State unresolved conflicts, missing primary evidence, and the cheapest next probe.

Complete acquisition when every consequential claim has direct support or an explicit coverage gap.

## Tool stack

| Need | Prefer | Fallback |
|---|---|---|
| Discover technical pages, papers, code | `exa-search` CLI / REST | Parallel Search |
| Fetch known URLs into clean text | Firecrawl scrape (`firecrawl-mint`) | `exa-fetch` CLI |
| Map or crawl a docs site | Firecrawl map / crawl | selective Exa fetch |
| Broad web search | Exa or Parallel Search | Firecrawl search |
| Local office/PDF/CSV to markdown | `anydoc` CLI | hosted Firecrawl Parse (OCR only, operator OK) |
| Dynamic or logged-in UI | builtin `browser` or `agent-browser` | operator artifact |
| Local repo truth | `rg`, `git`, `read` | operator-provided context |

Route by capability, not vendor.

- **Exa:** find and rank sources; code and technical discovery.
- **Firecrawl:** turn known URLs and site trees into agent-readable text.
- **anydoc:** convert local Word, Excel, PowerPoint, PDF, EPUB, CSV, and related files to markdown.
- **Browser / agent-browser:** interact with pages. Do not use them as the default static fetcher.
- **Mint:** every paid vendor call uses a value-free `__mint.<alias>__` marker. Never put raw API keys in the environment or transcript.

## OMP route

The chief uses native `researcher` lanes for independent angles. Each lane runs only its assigned angle.

| Need | Load |
|---|---|
| multi-angle research | `references/default-fanout.md` |
| Exa search, fetch, code context | `references/exa-tools.md` |
| Firecrawl scrape, map, crawl, search | `references/firecrawl-tools.md` |
| local documents to markdown | `references/anydoc.md` |
| browser fallback for dynamic pages | `references/browser-fallback.md` |
| delegated multi-lane work | `references/delegate.md` |
| examples and curl recipes | `references/exemplars.md` |

Load the default fanout for substantive multi-angle research. Use one source only for a named-source request or simple fact lookup.

## Acquisition order

1. Read local repo truth when the question touches this codebase.
2. Discover candidate sources with Exa or Parallel Search.
3. Extract page text with Firecrawl scrape. Map or crawl only with an explicit bound.
4. Use browser or `agent-browser` only when extraction fails on dynamic or authenticated UI.
5. Synthesize over cited sources. Do not treat search snippets as final evidence.

## Completion gate

Return a bounded conclusion with inline citations and exact supporting passages for consequential claims. Include publication and retrieval dates for volatile claims.

Record queried tools, accepted and rejected evidence, failures, coverage gaps, residual uncertainty, and the next probe.
