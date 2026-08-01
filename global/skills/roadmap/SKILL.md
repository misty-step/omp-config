---
name: roadmap
description: Interrogate the operator, then create or update and open a concise project ROADMAP.html.
disable-model-invocation: true
argument-hint: "[project|path]"
---

# /roadmap

Create or update root `ROADMAP.html` as the human planning surface. Keep vision,
roadmap, and work authority separate.

## Boundaries

- Keep durable direction in `VISION.md` when it exists.
- Keep outcomes, sequence, questions, research, and proof in `ROADMAP.html`.
- Keep tasks, claims, attempts, relations, and proof records in the work ledger.
- Keep 5–12 strategic items, exactly one current item, and no ticket detail.
- Open the local artifact after each successful update. Publish only when asked.

## Procedure

### 1. Ground

Find the repository root and active workspace. Read existing `ROADMAP.html` and root `VISION.md` when they exist. Read only sources that settle facts or authority. Resolve
factual questions with tools before asking the operator. Finish when you can
state the vision, roadmap, work authority, and relevant source files.

### 2. Interrogate

Read `global/references/interrogate-first.md` before questioning the operator.
Batch decisions about purpose, target state, human role, measures, current item,
sequence, proof, research, exclusions, and work authority. Give one recommended
answer and one short reason per question. Absorb dictation, remove settled
questions, and batch again. State the full shared understanding. Get explicit
confirmation before changing the artifact; finish only after confirmation.

### 3. Shape

Read `references/artifact-contract.md`. Convert confirmed understanding to its
data shape. Preserve identifiers when outcomes remain. Map each concern to one
item or explicit exclusion. Write outcomes, one observable proof condition, one
next decision, and one bounded research need per item. Finish when the artifact
contract passes.

### 4. Update

Write confirmed data to a temporary JSON file outside the repository and set its
final update date. From this skill directory, run:

```bash
scripts/render_roadmap.py <data-file> <repository-root>/ROADMAP.html
```

The renderer creates a missing artifact or updates its data block. Preserve the
layout unless the operator confirmed a layout change. Remove the temporary JSON
after success. Finish when the root artifact contains all confirmed data and no
template marker.

### 5. Prove and open

Read `skill://simplified-technical-english` and apply it to visible artifact prose.
From this skill directory, run:

```bash
scripts/validate_roadmap.py <repository-root>/ROADMAP.html
```

Resolve each validator error before running the repository gate. Run the gate.
Open the absolute `file://` URL in the browser. Check desktop and mobile views,
filter and expansion controls, JavaScript errors, and horizontal overflow. Keep
the browser open. Finish when the gate passes and the browser shows the artifact.

## Completion Gate

Report artifact path, vision changes, roadmap item changes, deferred decisions,
exclusions, gate result, and browser evidence. End with the current item and next question.

## Gotchas

- Keep backlog detail in the work ledger; a dump hides strategy.
- Summarize and link `VISION.md`; a second vision source creates drift.
- Preserve identifiers while outcomes remain; fresh identifiers break history.
- Keep detail behind expansion; a large artifact defeats the human surface.
- Require confirmed shared understanding before every write.
