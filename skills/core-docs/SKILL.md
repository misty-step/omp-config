---
name: core-docs
description: Audit and author the durable documentation a repository's code cannot explain.
disable-model-invocation: true
argument-hint: "[audit | overhaul] [path]"
---

# Core docs

Write only what code cannot explain: product purpose, non-obvious invariants,
domain language, deliberate refusals, and durable architectural choices.

## Document contracts

- `README.md`: entrypoint identity, non-obvious prerequisites, canonical gate,
  and pointers to durable records.
- `AGENTS.md`: a short router, repository invariants, stop signals, and owners.
- `VISION.md`: product purpose, operating bets, and deliberate refusals when
  the repository owns a product identity.
- `DOMAIN.md`: owned entities, external systems, lifecycles, and retired terms
  when the repository owns domain language.
- `docs/adr/`: numbered records for non-obvious, high-consequence choices.
- `CLAUDE.md`: a symlink to `AGENTS.md` when the repository's agent contract
  requires it.

Keep discoverable commands, dependency inventories, code walkthroughs, generic
engineering advice, secrets, ephemeral status, and unsettled debates out.

## Explore

Identify the repository and inspect source, layout, history, and current
documents. Mark each non-obvious claim as source-backed, inferred, or missing.
Research disputed claims through primary sources; use `/research` for unfamiliar
APIs, protocols, and domain terms. Ask focused questions only for missing human
intent, then record settled answers in the owning document.

## Audit

Check applicable documents against their contracts. Find stale rules, duplicate
ownership, broken links, missing decisions, and claims code cannot support.
Check that `CLAUDE.md` points to `AGENTS.md` when required.

## Author

Draft or overhaul only the documents the repository needs. Delete
code-discoverable text instead of archiving it. Keep one authoritative home for
each fact, move domain language to `DOMAIN.md`, product goals to `VISION.md`,
and routing to `AGENTS.md`. Leave changes uncommitted.

Return the document set, evidence and gaps, decisions captured, links checked,
and remaining human choices.
