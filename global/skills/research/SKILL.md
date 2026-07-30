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

Read `../research-core/SKILL.md` before routing.
That linked skill defines the canonical research-evidence contract.
This adapter adds OMP routing, acquisition, and closeout surfaces.

## OMP route

Route `/research` by capability, not vendor.
Use `/research [query]` for a bounded lookup or synthesis.
Use `/research delegate [task]` to select a delegated research lane.
Keep the OMP slash-command triggers stable.
Keep broad multi-angle delegation with OMP `magellan` through `/dispatch`.
Do not rename or relocate OMP roles in this adapter.

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

If the user names a sub-capability, load its reference.
Otherwise, load the default fanout for substantive research.
For an explicit single-source request or simple fact/version lookup, use one source.

## OMP acquisition and local surfaces

Keep Exa, xAI, Brave, Perplexity, Context7, Tavily, Firecrawl, browser agents, and provider lanes as OMP acquisition surfaces behind evidence jobs.
Use the provider reference selected by the route table.
Do not move provider semantics into the canonical core.

For model selection or comparison, start with
`global/skills/peer-harnesses/references/model-provider-harness-index.md`, then verify current availability, pricing, context, and tool-calling support through the selected OMP provider lanes.
Keep dates and citations required by the canonical core.

## OMP closeout

Record the OMP provider lanes, queried tools and reasons, receipt ids,
accepted and rejected outputs, failures, and source-coverage gaps in the research result.
Let OMP `/dispatch` own full composition and role routing.
Do not move that runtime into the core.
Apply the canonical core's evidence labels and uncertainty statement before returning the result.

See `global/AGENTS.md` for the OMP shared operating spine.
See `global/skills/peer-harnesses/references/model-provider-harness-index.md` for the OMP model/provider reference.
