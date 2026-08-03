---
name: research
description: |
  Research current facts through primary sources, independent angles, and
  auditable evidence. Use for bounded lookup, comparison, model selection,
  discourse analysis, or delegated external research. Trigger: /research.
argument-hint: "[query|web-search|web-deep|web-news|web-docs|delegate|introspect|readwise|xai|exemplars] [args]"
---

# /research

Research one question through evidence that another reviewer can audit.

## Evidence contract

1. Frame two to four independent angles. Each angle needs a distinct claim, source path, or falsifier; wording changes are not independent.
2. Prefer primary sources: official documentation, specifications, repositories, release notes, direct measurements, and first-party records. Search summaries only locate evidence.
3. Read the source behind each consequential claim. Capture the supporting passage, stable URL or path, publication date when available, and retrieval date. Never fabricate a citation.
4. Triangulate consequential, comparative, and fast-changing claims across independent publishers or source types. Preserve conflicts.
5. Separate observed facts, source claims, inferences, and recommendations. Label a layer when readers can confuse it with another.
6. Date facts that can change, including availability, prices, versions, benchmarks, and policies.
7. Record rejected evidence. Name stale, secondary, partial, inaccessible, conflicting, or weak sources and state the limitation.
8. State unresolved conflicts, unverified assumptions, missing primary evidence, and the cheapest next probe. Absence of search results is not evidence of absence.

Complete acquisition when every consequential claim has direct support or an explicit coverage gap.

## OMP route

Route by capability, not vendor. The chief uses native `researcher` lanes for independent angles. Each lane executes only its assigned angle.

| Need | Load |
|---|---|
| broad comparison, prior art, or discourse scan | `references/default-fanout.md` |
| `web-search`, `web-deep`, `web-news`, or `web-docs` | `references/web-search.md` |
| Exa search, fetch, or code context | `references/exa-tools.md` |
| extraction, site maps, or crawls | `references/extraction-tools.md` |
| delegated research | `references/delegate.md` |
| introspection | `references/introspect.md` |
| Readwise | `references/readwise.md` |
| xAI search | `references/xai-search.md` |
| exemplars | `references/exemplars.md` |

Load the default fanout for substantive multi-angle research. Use one source only for a named-source request or simple fact lookup.

## OMP acquisition

Keep Exa, xAI, Brave, Perplexity, Context7, Tavily, Firecrawl, browser agents, and provider lanes behind the evidence contract.

For model selection, start with `global/skills/peer-harnesses/references/model-provider-harness-index.md`. Then verify availability, price, context, and tool support through current provider lanes.

## Completion Gate

Return a bounded conclusion with inline citations and exact supporting passages for consequential claims. Include publication and retrieval dates for volatile claims.

Record queried tools and reasons, provider lanes, receipt identifiers, accepted and rejected evidence, failures, coverage gaps, residual uncertainty, and the next probe.
