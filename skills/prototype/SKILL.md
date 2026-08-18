---
name: prototype
description: Fan Emil and Leon taste scouts, then build a visual catalog of at least six options for a design task.
disable-model-invocation: true
license: MIT; modified from Matt Pocock's prototype skill. Emil and Leon texts keep their own MIT licenses under references/.
---

# Prototype

For a visual or interaction task: synthesize Emil and Leon, then ship a
catalog of at least six structurally different options. For a logic, state,
or data-shape question: read `LOGIC.md` and stop there.

## 1. Choose

- Visual hierarchy, interaction, motion, or existing-UI overhaul: continue.
- Logic, state, data shape, or business rules: read `LOGIC.md`.

Completion criterion: The question type is named and the matching path is
selected.

## 2. Fan out

Default scout set (one read-only scout per file):

- `references/emil/emil-design-eng.md`
- `references/emil/animate.md`
- `references/emil/review-animations.md`
- `references/emil/find-animation-opportunities.md`
- `references/emil/apple-design.md`
- `references/emil/prototype.md`
- `references/leon/taste-skill.md`
- `references/leon/redesign-skill.md`
- `references/leon/output-skill.md`

Add or drop files from `references/emil/` and `references/leon/` when the
operator names a subset or the surface is not web UI. Skip
`animate-expo`, imagegen, `stitch-skill`, `ask-sonner`, and
`pick-ui-library` unless the task needs them.

Each scout reads only its assigned file plus the brief and the real surface.
It returns at most five concrete directives for this task. It does not write
code.

Completion criterion: Every selected reference has a harvested scout result.

## 3. Synthesize

Merge the scout output into one direction:

- thesis (one sentence);
- audience and job;
- VARIANCE / MOTION / DENSITY dials, or why they do not apply;
- keep / drop / never lists;
- constraints from the existing system.

Read `frontend-design` only for product thesis and browser critique rules.
Do not let it replace the synthesized direction.

Completion criterion: One written direction a catalog can implement.

## 4. Catalog

Read `UI.md`. Build at least six options. Each option must differ in
structure, hierarchy, or primary interaction. Theme-only swaps do not count.

Mark the surface `PROTOTYPE`. Isolate it from production mutations.

Completion criterion: Six or more switchable options are on a real surface.

## 5. Decide

Exercise every option at desktop and mobile sizes. Use keyboard and pointer
on the primary interaction. Capture comparison screenshots.

Record the operator's pick, or stop and wait if none is chosen. After a pick,
remove the other options, the switcher, and prototype-only routes. Implement
the winner to production standards only when the operator asks.

Completion criterion: A pick is recorded, or the catalog is waiting. Losers
are gone after a pick.
