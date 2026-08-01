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

Create committed reference docs in `docs/` from one source. Render that source
to Markdown, HTML, and diagrams. Verify every claim against live source.

## Route

| Need | Load |
|---|---|
| Verification system: turn accuracy and coverage into falsifiers | `references/oracles.md` |
| Information architecture: Diátaxis, page taxonomy, useful diagrams | `references/information-architecture.md` |
| Provenance, freshness, incremental scope, Mode B handoff | `references/provenance-and-freshness.md` |
| Agent loop, lane cards, build order | `references/orchestration.md` |
| Markdown, HTML, Mermaid, sync, and publish contract | `references/render-contract.md` |
| Page provenance and skeleton | `templates/page.md` |
| Freshness oracle driver | `scripts/freshness.py` |

`--check` runs freshness and render oracles against existing `docs/` only.
`--full` forces full-repo regeneration instead of incremental scope.

## Workflow judgment

The lead decomposes these outcome-shaped lanes. See
`references/orchestration.md` for lane cards and detail.

| Lane | Required judgment | Oracle |
|---|---|---|
| Recon swarm | Use blind agents for entry points, data flow, dependencies, config, tests, and git history. | — |
| IA plan | Adapt page types and diagrams to the repo, not to a fixed tree. | coverage |
| Generation | Use one agent per facet with just-enough context; generate in dependency order. | — |
| Verify | Use fresh skeptics from a decorrelated model family and a cold reader. | accuracy, navigability |
| Iterate | Regenerate flagged pages until K consecutive rounds have no blocking oracle failure. | all |
| Render + stamp | Generate Markdown, HTML, and diagrams; stamp provenance; commit. | render, freshness |

Use model-driven ad-hoc fan-out first. Build a deterministic orchestration
workflow only after telemetry shows a recurring pattern.

## Contract

- Ground every architectural claim in source lines that a fresh skeptic verifies; cut or flag unsupported prose.
- Stamp each committed page with `generated-at-sha` and `covers:` globs from `templates/page.md`.
- Run full verification on every rerun. Regenerate only stale pages, changed-source neighbors, and required links.
- Let the system shape choose the page tree. Borrow page types, not a fixed tree.
- Compose with `/design` and `anthropic-frontend-design` for HTML, `/showcase` for publish machinery, and `/groom` for recon.
- Use `scripts/freshness.py`; a page past its stamped SHA is stale.
- Let the operator choose page tree, depth, diagrams, and HTML publish location when unclear.

## Boundaries

- These docs serve humans. They do not replace live source or the agent context substrate; use `/dispatch` for independent grounding.
- `/showcase` owns external proof and launch copy. This skill owns technical reference docs.
- The vendored `deepwiki` skill queries third-party wikis. This skill documents the current repo.
- Mode B auto-refresh is unavailable. Use on-demand Mode A and `global/references/loop-readiness.md`; do not invent a workflow service.

## Delegation

Delegate through the Shared Operating Spine (`Act`). Route heavy or long runs to
`/sprites`. Use these lanes:

- Recon scouts: one per blind lens, using `/groom`'s bench.
- Page generators: one per facet, with dependency order.
- Accuracy skeptics: fresh context, a different model family, artifact plus oracle only; never the author's reasoning trail.
- Cold-reader navigator: generated docs plus a real task; wrong landing means bad IA.

## Failure controls

- Fix weak proof instead of polishing unsupported claims.
- Run coverage and accuracy oracles; they catch different failures.
- Make render reject broken Mermaid and dead internal links.
- Let recon choose IA; copied IA becomes generic.
- Capture intent, flow, and why; restating code adds drift.
- Log skipped scope when you bound recon, such as top-N modules or sampled history.

## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract.
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
