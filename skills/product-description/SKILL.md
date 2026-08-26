---
name: product-description
description: Build an outside-in description of a software product, verify it on the running product, and triage defects.
disable-model-invocation: true
---

# Product description

A product description records the state chart the user experiences. Source and
tests suggest that behavior; the running product verifies it.

## Scope

Set the product, users, source revision, runnable environments, included
features, output repository, and evidence limits. Infer from source before
asking. Use `references/product-kinds.md` only to adapt names and surfaces.

Done when inclusions, exclusions, and verification access are explicit.

## Establish the pattern

Create the output from `README-template.md`, `goal-template.md`,
`glossary-guide.md`, and `document-template.md`. Write the goal, glossary,
foundations, and one difficult pilot yourself. Describe what the user sees,
does, and causes. Keep code mechanics in a technical note only when they change
expected behavior.

Each feature covers entry, visible states, actions, persistence, errors,
interruptions, recovery, accessibility, and exit. Cite the source revision.

Done when the pilot fixes vocabulary, skeleton, and depth for the set.

## Complete and reconcile

Draft remaining independent features from current code and tests. Then run one
whole-set pass for terminology, links, state ownership, numbers, contradictions,
and missing transitions. Use `check-links.py`.

Done when every in-scope feature has one owner and one consistent account.

## Verify and triage

Build checklists from `verification-template.md`. Exercise the running product
by hand and record observed differences. Recapture documents whose behavior
changed. Collect suspected defects through `bug-triage-template.md`; deduplicate
by root cause and separate confirmed defects from product decisions.

Return coverage, verified revision and runtime identity, gaps, and triage.

Done when the description matches observed behavior or marks the exact evidence
gap.
