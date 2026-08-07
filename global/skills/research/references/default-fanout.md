# Default fanout

Multi-source triangulation for substantive research.

## Use

Load this reference for broad research, comparison, prior art, model or provider investigation, discourse scans, or any question where one lookup would overfit one source.

Use single-source research only when the user names the source or asks for a narrow fact.

## Context packet

Capture before launching lanes:

- Objective: fact lookup, prior-art scan, architecture comparison, discourse scan, or decision support.
- Scope: repos, files, domains, products, dates, jurisdictions, exclusions.
- Freshness: latest, date-bounded, or stable background.
- Acceptance oracle: decision to support, risk to refute, artifact to produce, or explicit absence.
- Tool constraints: missing credentials, offline mode, or user-named sources.

## Source matrix

Run a lane when relevant. Otherwise keep it as `skipped` with the reason.

| Lane | Capability | Primary tools |
|---|---|---|
| Codebase | live repo patterns and contracts | `rg`, `git`, `read` |
| Discovery | find candidate sources | Exa MCP, Parallel Search |
| Extraction | page and site text | Firecrawl scrape / map / crawl |
| Documents | local office/PDF/CSV text | `anydoc` |
| Interaction | dynamic or authenticated UI | builtin `browser`, `agent-browser` |
| Synthesis | answer over gathered evidence | lead synthesis with citations |
| Critique | local fit and contradictions | `delegate.md` contradiction lane |

If a lane fails, times out, or lacks credentials, keep its section and label the status. Do not silently drop it into synthesis.

## Capability routing

Prefer MCP first, local CLI wrapper second, direct Mint REST third.

| Intent | Prefer | Fallback |
|---|---|---|
| Local repo truth | `rg`, git, local files | operator context |
| Code or reference implementations | Exa code / neural search | GitHub search |
| Known URL text | Firecrawl scrape | Exa fetch |
| Site map or docs corpus | Firecrawl map | manual link list |
| Bounded docs crawl | Firecrawl crawl with `limit` | map + selective scrape |
| Local `.docx`/`.pdf`/`.xlsx`/CSV | `anydoc` | Firecrawl Parse only for scanned OCR with operator OK |
| Broad web discovery | Exa or Parallel Search | Firecrawl search |
| Dynamic or logged-in page | `browser` / `agent-browser` | operator artifact |
| Model pricing or availability | dated web sources via Exa + official pages | /home/phaedrus/.omp/agent/skills/harness-engineering/references/model-provider-harness-index.md, then verify live |

## Report shape

```markdown
## Synthesis
[Conclusion, confidence, decision impact, residual uncertainty.]

## Source matrix
| Lane | Status | Contribution | Key refs |
|---|---|---|---|
| Codebase | complete/partial/failed/skipped | ... | path or command |
| Discovery | ... | ... | URLs |
| Extraction | ... | ... | URLs |
| Interaction | ... | ... | evidence refs |
| Synthesis | ... | ... | citation refs |
| Critique | ... | ... | notes |

## Conflicts
[Disagreements and the lead resolution.]

## Evidence
[Grouped citations, commands, artifacts.]

## Residual risk
[Stale facts, missing providers, unqueried sources, or none.]
```

## Failure labels

- `complete`: usable evidence inside scope
- `partial`: some artifacts only
- `failed`: attempted, no usable evidence
- `skipped`: out of scope, forbidden, or impossible
- `stale`: may be outdated for the freshness requirement

Test every recommendation without the weakest source. If it fails, label confidence low.
