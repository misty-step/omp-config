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
| Model pricing or availability | dated web sources via Exa + official pages | `skill://harness-engineering/references/model-provider-harness-index.md`, then verify live |

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

## OpenRouter account audit

- Mistake the Mint-routed key for the complete account key inventory.
- Expose credential bytes, secret-derived identifiers, or request content in evidence.
- Mix R90 and Misty Step ownership, keys, budgets, usage, or enforcement.
- Treat current key metadata as historical account usage without a matching time range.
- Omit revoked, disabled, unused, or provisioning-only keys because one endpoint excludes them.
- Claim tracing, guardrails, or enforcement that the documented request path cannot prove.
- Recommend another proxy, store, or dashboard before testing Mint and OpenRouter controls.
- Report spend without its retrieval time, currency, filters, and provider limitations.
- Add concepts and process when fewer named keys, tags, limits, and deletion preserve control.
- Erasure question: what can be deleted while preserving account governance and audit evidence?

## OpenRouter premium-model attribution

- Attribute Luna spend to a caller from model totals alone.
- Treat an OpenRouter app label, API key, or user field as an agent identity without proving the mapping.
- Mix workstation OMP usage with deployed R90 product usage because the active repository belongs to R90.
- Recommend R90 account changes without authenticated R90 evidence or current operator scope.
- Infer a spike from a rolling total without daily or finer time buckets and a baseline.
- Treat one expensive model as waste without separating request count, tokens, cache, reasoning, and task outcome.
- Add a new telemetry store or proxy before testing native Analytics, Activity, Generation, metadata, and Broadcast.
- Design one key per ephemeral agent when request metadata provides sufficient traceability.
- Let a cheaper default silently weaken deep-reasoning routes that require Luna.
- Erasure question: which credentials, dimensions, sinks, jobs, and controls can be removed while preserving attribution?
