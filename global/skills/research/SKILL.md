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

Read `../research-core/SKILL.md` before routing. That linked skill is the
canonical research-evidence contract; this adapter only supplies OMP's route,
acquisition, and closeout surfaces.

## OMP route

`/research` routes by capability, not vendor. `/research [query]` handles a
bounded lookup or synthesis; `/research delegate [task]` selects a delegated
research lane. The adapter keeps these OMP slash-command triggers stable.
Broad multi-angle delegation remains with the OMP `magellan` role through
`/dispatch`; this adapter does not rename or relocate OMP roles.

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

If the user names a sub-capability, load its reference. Otherwise load the
default fanout for substantive research; narrow to one source for an explicit
single-source request or simple fact/version lookup.

## OMP acquisition and local surfaces

Exa, xAI, Brave, Perplexity, Context7, Tavily, Firecrawl, browser agents, and
provider lanes remain OMP acquisition surfaces behind the evidence jobs. Use
the provider reference that the route table selects; do not move provider
semantics into the canonical core.

For model selection or comparison, start with
`global/skills/peer-harnesses/references/model-provider-harness-index.md`, then
verify current availability, pricing, context, and tool-calling support through
the selected OMP provider lanes. Keep dates and citations required by the
canonical core.

## OMP closeout

Record OMP provider lanes, tools queried and why, receipt ids, accepted and
rejected outputs, failures, and source-coverage gaps in the research result.
The OMP `/dispatch` skill owns full composition and role routing; this adapter
does not move that runtime into the core. Apply the canonical core's evidence
labels and uncertainty statement before returning the result.

See `global/AGENTS.md` for OMP's shared operating spine and
`global/skills/peer-harnesses/references/model-provider-harness-index.md` for
the OMP model/provider reference.
