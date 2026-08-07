# /research eval

Claim: given a drift-prone or comparison-shaped question, `/research` returns a synthesized answer with dated sources, residual uncertainty, and no silent single-source overfitting.

Arms:

- A = `/research` installed and invoked
- B = raw same-model prompt with same tools, no skill
- C = single search call only

Grade blind. Run objective checks first. Use a different model family for the judge.

## Fixtures

| # | Prompt | Stress |
|---|---|---|
| 1 | Compare 2–3 cheap high-volume OpenRouter models on price, context, and tool calling right now. Rank one pick. | drift-prone facts, dated sources, ranked recommendation |
| 2 | Extract the current Firecrawl scrape request shape from official docs and quote the required fields. | Exa discover + Firecrawl extract, primary docs |
| 3 | Does this repo's research skill still mention Context7, Brave, or Perplexity as live routes? Check the repo first. | repo-truth-first |

Two of three must show A>B for a pass.

## Objective checks

- Every load-bearing claim has a citation (URL, path, or command output).
- At least one cited source has an explicit date; report states research date or recency window.
- Fixture 1 ranks ≥2 candidates and picks one.
- Fixture 2 uses a primary docs URL, not only a search snippet.
- Fixture 3 reads local `global/skills/research/**` before or with any web claim.
- Skipped, failed, or stale sources are named.
- Residual uncertainty line is present.

## Rubric (1–5)

| Dimension | 5 | 1 |
|---|---|---|
| Source grounding | every claim traceable | no citations |
| Tool fit | Exa for find, Firecrawl for extract when needed | browser used for static docs |
| Repo-truth (fixture 3) | reads local skill files | answers from memory only |
| Honesty about gaps | names unverified or stale items | smooths over gaps |

## Pass condition

Arm A beats arm B on grounding and uncertainty on ≥2 of 3 fixtures, and passes every objective check.

## Cadence

- Edit-time: fixture 1 smoke on any `global/skills/research/**` change.
- Contract change to source order or tool stack: full A/B.
- Major model release: re-audit.

**No full run yet.** Record verdicts here when executed.
