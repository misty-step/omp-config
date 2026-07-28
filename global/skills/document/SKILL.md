---
disable-model-invocation: true
name: document
description: |
  Generate world-class, source-verified reference documentation for a codebase.
  Survey the repo, plan information architecture, write facet-scoped pages, and
  verify every claim against live source. Commit markdown + HTML + diagrams to
  docs/ from one source. Always run the full verify loop; scope incrementally by
  provenance. Use when: "document this codebase", "generate the docs",
  "build a codebase wiki", "write architecture docs", "onboarding docs",
  "documentation site", "keep the docs in sync", "world-class docs". Trigger:
  /document, /docs, /wiki.
argument-hint: "[scope-path|--full|--check]"
---

# /document

Documentation earns trust when **every claim is verified against live source**. It is not a plausible summary that drifts.

This skill owns the gap between existing code and safe system changes.
It helps new contributors and maintainers navigate, understand, and safely
change the system from the docs.
It produces committed, human-facing reference docs in `docs/`.
One source renders to markdown, HTML, and diagrams.
The main difference from auto-wiki products is adversarial verification of each claim against source.
That verification prevents confident false claims in the repository.

These named phases (survey → plan → write → critique → iterate) follow SDLC practice. Do not narrate them.
The skill's value is the **oracles, the IA taste, the provenance contract, and the orchestration discipline** below.

## Route

| Need | Load |
|---|---|
| The verification system — how "comprehensive / accurate / well-organized" become falsifiers | `references/oracles.md` |
| Information architecture — Diátaxis mapping, page taxonomy, which diagrams are useful | `references/information-architecture.md` |
| Committed-docs provenance, freshness falsifier, incremental scope, Mode B handoff | `references/provenance-and-freshness.md` |
| The multi-agent loop topology, lane cards, build-order discipline | `references/orchestration.md` |
| Output surfaces: md source → HTML + mermaid, "synced across surfaces", publish target | `references/render-contract.md` |
| Per-page provenance front-matter + world-class page skeleton | `templates/page.md` |
| Freshness oracle driver (stale-page detector) | `scripts/freshness.py` |

`--check` runs only the freshness + render oracles against existing `docs/` (no
generation). `--full` forces full-repo regeneration instead of incremental scope.

## The loop, where the judgment lives

A table of lanes, not a procedure. Each lane is outcome-shaped; the lead owns
decomposition. Detail and lane cards in `references/orchestration.md`.

| Lane | Non-obvious judgment | Oracle it feeds |
|---|---|---|
| Recon swarm | lens-blind agents (entry-points / data-flow / dep-graph / config+infra / tests-as-spec / git-*why*); each agent works without the other lenses, so one search angle cannot show full coverage | — |
| IA plan | structure **adapts to the system** — a CLI ≠ a service ≠ a library; pick pages and diagrams from what recon found, not a fixed template | coverage |
| Generation | one agent per page/facet, just-enough context, dependency order (overview before deep-dives); pipeline, not barrier | — |
| Verify | adversarial skeptics from a **decorrelated model family** refute each claim against source; a cold reader proves navigability | accuracy, navigability |
| Iterate | loop-until-dry: regenerate flagged pages until K consecutive rounds raise no blocking oracle failure | all |
| Render + stamp | one generation → md + HTML + diagrams; stamp provenance; commit | render, freshness |

**Build-order discipline:** Use model-driven, ad-hoc fan-out first. Do not write a deterministic orchestration-workflow template before telemetry shows a recurring pattern. The harness-engineering contract requires this order. Build the asset only after the pattern recurs. Avoid the deterministic-scaffold failure mode.

## Contract

- **Source-grounded or it does not ship.** Every architectural claim maps to
  specific source lines a skeptic verified, or it is cut/flagged. Unverifiable
  prose is the failure this skill exists to prevent.
- **Committed pages carry provenance.** Each page stamps `generated-at-sha` and
  `covers:` globs (`templates/page.md`). This makes drift *detectable* instead
  of hidden — the load-bearing mitigation for committing docs into the repo.
- **Always use the world-class quality bar with incremental scope.** Run full verification every time. On each rerun, regenerate only pages whose covered source changed (freshness-stale pages) and their cross-link neighbors. Keep quality constant and work proportional to the diff.
- **IA adapts to the repo.** Borrow page *types*, never a fixed tree. Let the
  system's shape choose the structure.
- **Compose, don't reinvent.** Use `/design` + `anthropic-frontend-design` for Aesthetic/HTML. Use `/showcase` for publish machinery. Use `/groom`'s investigation bench for recon work. This skill owns the oracles and IA taste.
- **Freshness is checkable.** `scripts/freshness.py` is the driver; a page
  covering changed files past its stamped SHA is stale, full stop.
- **Operator owns IA and publish choices.** Page tree, depth, diagram set, and
  where HTML publishes are the operator's call when ambiguous.

## Boundaries (what this is not)

- **Not the agent's context substrate.** The owning lane reads live source and uses `/dispatch` for independent grounding. Humans use these docs. They are not a possibly stale substitute for source.
- **Not marketing/demo.** `/showcase` owns external proof and launch copy. This is technical reference.
- **Not external-repo lookup.** The vendored `deepwiki` skill queries third-party OSS wikis. This skill documents *your* repo.
- **Auto-refresh-on-push is currently unavailable in Mode B.** This skill is
  on-demand (Mode A). The freshness script remains the local trigger contract;
  see `global/references/loop-readiness.md`. Do not invent a replacement
  workflow service.

## Delegation Judgment

Delegate per the Shared Operating Spine (Act).
This skill is parallel-by-default and uses many tokens. Route heavy or long runs to `/sprites`.
Lanes:

- **Recon scouts** — one per lens, blind to the others (compose `/groom`'s bench).
- **Page generators** — one per facet, just-enough context, dependency order.
- **Accuracy skeptics** — fresh-context, **different model family**, prompted to *refute* each claim against source. Critics get the artifact and the oracle only — never the author's reasoning trail (Shared Operating Spine: Prove).
- **Cold-reader navigator** — sees only the generated docs and a real task. It must land in the right files. Wrong landing = bad IA.

## Gotchas

- **Polished false claims are worse than plain true weakness.** If proof is weak, fix the proof.
- **Committed docs can drift without an error.** Provenance stamps and the freshness oracle make this drift visible.
- **Coverage is not accuracy.** A wrong flow description fails even when every symbol appears. Run both oracles; they catch different errors.
- **Restating code is not documentation.** A page that paraphrases functions adds drift risk without understanding. Capture intent, flow, and *why*.
- **A diagram that does not parse fails the build.** The render oracle must reject broken mermaid or dead internal links.
- **Copied IA is generic IA.** A fixed page tree makes every repo look autogenerated. Let recon choose the structure.
- **Unreported truncation can look complete.** If scope is bounded (top-N modules, sampled history), `log` what it skipped.

## Completion Gate

See `global/AGENTS.md` (Prove) for the shared core.
`/document` adds:

```markdown
## Document Gate
- Coverage: real export/route/entry surface vs documented surface; named gaps or waiver.
- Accuracy: each architectural claim source-grounded by a fresh-context skeptic; refuted/flagged claims listed.
- Navigability: cold-reader landed on the right files for the test task(s), or where it failed.
- Render: HTML built, mermaid parsed, zero broken internal links — command + result.
- Provenance: every committed page stamped with generated-at-sha + covers globs.
- Freshness: scripts/freshness.py result against HEAD; stale pages or clean.
- Scope: full vs incremental, and what was intentionally not regenerated.
- Publish: where HTML renders, or that it stayed local pending operator choice.
```
