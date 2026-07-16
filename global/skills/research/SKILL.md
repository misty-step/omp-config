---
name: research
description: |
  Web research, multi-AI delegation, and multi-perspective validation.
  /research [query], /research delegate [task].
  Use when: "search for", "look up", "research", "delegate",
  "get perspectives", "web search", "find out", "investigate",
  "introspect", "check readwise", "saved articles", "reading list",
  "what are people saying", "X search", "trending", "which model",
  "compare models", "best model for", "model selection".
  Trigger: /research.
argument-hint: "[query|web-search|web-deep|web-news|web-docs|delegate|introspect|readwise|xai|exemplars] [args]"
---

# /research

Evidence-backed research. The lead owns framing, source weighting, synthesis,
and residual uncertainty.

`/research` routes by capability, not vendor. Exa, xAI, Brave, Perplexity,
Context7, Tavily, Firecrawl, browser agents, and provider lanes are acquisition
tools behind a small set of evidence jobs: repo truth, docs lookup, web
retrieval, code/context examples, extraction, social/discourse, recency
verification, and synthesis.

## Route

| Need | Load |
|---|---|
| broad research, comparison, architecture prior art, or discourse scan | `references/default-fanout.md` |
| `web-search`, `web-deep`, `web-news`, `web-docs` | `references/web-search.md` |
| Exa search/fetch/deep/MCP/code context | `references/exa-tools.md` |
| extraction, site maps, crawls | `references/extraction-tools.md` |
| `delegate` | `references/delegate.md` |
| `introspect` | `references/introspect.md` |
| `readwise` | `references/readwise.md` |
| `xai` | `references/xai-search.md` |
| `exemplars` | `references/exemplars.md` |

If the user names a sub-capability, load that reference. Otherwise use the
default fanout for substantive research; narrow to one source only for explicit
single-source requests or simple fact/version lookups.

Model selection/comparison is research, not memory: model facts rot in
weeks. Start from
`primitives/skills/peer-harnesses/references/model-provider-harness-index.md` for
current local facts, then verify against live sources — availability on the
target platform, pricing, context, tool-calling support — and return a ranked
recommendation with dates on every claim.

## Contract

- Read the live repo first for repo facts; use current external sources for
  drift-prone facts.
- Prefer acquisition surfaces in this order when available: MCP tool, local CLI
  wrapper, direct REST/API, built-in WebSearch last.
- Retrieval and synthesis are distinct jobs: source URLs/files/receipts are the
  proof, your synthesis is the conclusion. Cite the source for every claim; a
  summary never stands in for it.
- Label skipped, failed, stale, in-flight, and partial sources; report residual
  uncertainty rather than smoothing over gaps.

## Delegation Judgment

Delegate per the Shared Operating Spine (Act). A lane earns
its spend only by carrying distinct sources, methods, or model families.

## Completion Gate

See `primitives/shared/AGENTS.md` (Prove) for the shared core.
`/research` adds:

- Sources/tools queried and why.
- Provider lanes, receipt ids, accepted/rejected outputs, and failures.
- Source coverage gaps, stale facts, and skipped tools.

## Gotchas

- A single WebSearch is a lookup, not substantive research.
- Mandatory source structure belongs in `references/default-fanout.md`; keep
  vendor command recipes in tool references.
