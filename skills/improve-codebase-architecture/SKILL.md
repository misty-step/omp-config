---
name: improve-codebase-architecture
description: Find evidence-backed module-deepening opportunities, report them visually, then grill one selected change.
disable-model-invocation: true
license: MIT; modified from Matt Pocock's improve-codebase-architecture skill
---

# Improve Codebase Architecture

A deep module hides substantial necessary behavior behind a small interface.
Find changes that reduce caller knowledge and whole-system complexity. Judge
every candidate by its data structures and relationships (Torvalds), module
depth with errors defined out of existence (Ousterhout), and
necessary-versus-incidental complexity (Hickey).

## Scope

Use the named subsystem or one active hot spot from recent changes. Read its
governing decisions and trace representative caller-to-effect paths.

Look for:

- one concept scattered across shallow modules;
- interfaces as complex as their implementations;
- leaked state or repeated caller-side translation;
- test-only seams and pass-through wrappers;
- changes that repeatedly touch the same unrelated files.

Apply the deletion test. Removing a module helps only when complexity
concentrates in one clear owner instead of moving elsewhere. Counts support a
finding; they do not justify it.

## Candidates

Return zero to three candidates. Each must state:

- affected files and callers;
- observed friction and evidence;
- deletion or direct-use design considered first;
- proposed owner and smaller interface;
- state and behavior that move behind it;
- code, seams, tests, and configuration removed;
- preserved invariants, migration risk, and proof;
- strength: `Strong`, `Worth exploring`, or `Speculative`.

Do not create an adapter for one hypothetical alternative.

## Report

Read `HTML-REPORT.md`. Write one self-contained HTML report to the OS temporary
directory and open it in a browser. Recommend one candidate, or state that none
survived.

Do not edit production code yet. After the user selects a candidate, use
`grilling` to settle ownership, interface, state, migration, failure behavior,
and proof. Implement only when the request authorizes it and the lock does not
expand scope.
