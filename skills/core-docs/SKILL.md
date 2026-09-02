---
name: core-docs
description: Audit, research, brainstorm, and author core documentation across fleet repositories.
disable-model-invocation: true
argument-hint: "[audit | overhaul] [path]"
---

# Core docs

This skill audits and authors core documentation for a repository.

Core documents capture only what code cannot explain. They record philosophy, non-obvious invariants, domain language, and architectural decisions.
They never describe code mechanics or repeat discoverable implementation facts.

Every repository maintains a base floor:
1. `README.md` states entrypoint identity, non-obvious prerequisites, and the canonical gate.
2. `AGENTS.md` provides an index router and repository invariants.

Repositories add conditional documents when they own those boundaries:
3. `VISION.md` defines product purpose, operating bets, and deliberate non-goals.
4. `DOMAIN.md` defines ubiquitous language, domain models, and retired terms.
5. `docs/adr/` records durable architectural choices and rejected alternatives.

`CLAUDE.md` must always exist as a symlink pointing to `AGENTS.md`.

All core documents use ASD-STE 100. Every sentence must contain at most twenty words.

## Target and Explore

Identify the repository. Inspect source code, directory layout, commit history, and existing documentation.

Investigate what the code already proves. Identify gaps that code cannot explain:
- Why does this system exist?
- Who uses the system?
- Which invariants are non-negotiable?
- What deliberate non-goals bind the architecture?
- Which domain terms require unambiguous definitions?
- Which past architectural choices shaped the current design?

Done when the codebase is understood and documentation gaps are identified.

## Research

Investigate each non-obvious claim against primary sources. Use `skill://research` for unfamiliar APIs, protocols, and domain terms.

Read fleet exemplars, accepted ADRs, and authoritative domain sources. Record evidence for vision, domain language, and architectural refusals.

Name every inference. Leave an explicit gap when a primary source is missing.

Done when each material claim has a primary source or a named gap.

## Consult and Brainstorm

Engage the operator in a focused conversation. Ask targeted questions to acquire missing context.

Discuss and settle:
- Product vision and operating premises.
- Deliberate architectural refusals ("What we refuse").
- Domain vocabulary and retired terms.
- Non-obvious decisions, trade-offs, and rejected alternatives.
- The applicable document set for this repository.

Done when the operator confirms the core concepts, boundaries, and decisions.

## Audit

Audit existing documents against their contracts:

1. **`README.md`**
   - Confirm entrypoint identity, non-obvious prerequisites, and canonical gate exist.
   - Verify the file omits discoverable package scripts and code walkthroughs.

2. **`AGENTS.md`**
   - Confirm the file acts as a tight router under one hundred lines.
   - Confirm the file lists pointers to authoritative documents.
   - Confirm non-negotiable repository invariants are explicit.
   - Verify the file omits generic engineering advice and secrets.

3. **`VISION.md`** (when applicable)
   - Confirm product purpose and operational premises are explicit.
   - Confirm a "What we refuse" section names deliberate non-goals.

4. **`DOMAIN.md`** (when applicable)
   - Confirm domain entities and relationships have single, explicit definitions.
   - Confirm a table lists retired terms and replacements.

5. **`docs/adr/`** (when applicable)
   - Confirm records follow sequential numbering (`NNNN-slug.md`).
   - Confirm records state context, decision in active voice, and consequences.

6. **`CLAUDE.md`**
   - Confirm `CLAUDE.md` exists and is a symlink pointing to `AGENTS.md`.

Done when the audit report lists every gap, stale rule, and contract violation.

## Author and Overhaul

Draft missing core documents or overhaul existing ones based on operator alignment.

Prune misplaced content:
- Remove discoverable package scripts and command restatements from documentation.
- Delete code-discoverable text outright when shrinking bloated files. Do not create archive directories.
- Move non-obvious operational gates to `README.md`.
- Move domain vocabulary to `DOMAIN.md`.
- Move product goals and refusals to `VISION.md`.
- Keep `AGENTS.md` focused on routing and repository invariants.
- Ensure `CLAUDE.md` is a symlink pointing to `AGENTS.md`.

Apply ASD-STE 100 rules:
- Write in active voice.
- Limit every sentence to twenty words.
- Focus on why and what. Do not describe implementation mechanics.
- State instructions positively. Reserve prohibitions for hard guardrails.

Leave all changes uncommitted in the working tree for operator review. Never commit or push changes.

Done when all applicable documents satisfy their contracts and changes remain uncommitted.

## Verify

Inspect the working tree diff:
```sh
git diff --stat
```

Verify relative markdown links resolve to existing files.

Confirm `CLAUDE.md` links to `AGENTS.md` as a symlink.

Verify no sentence in the revised core documents exceeds twenty words.

Present the overhauled documents, decisions, and uncommitted diffs to the operator.

Done when verified uncommitted diffs await human review.
