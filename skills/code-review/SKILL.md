---
name: code-review
description: Review and repair a completed change for whole-system simplicity, correctness, and behavioral fidelity.
disable-model-invocation: true
---

# Code Review

Review the completed change, repair every supported defect, prove the repairs,
and repeat until the boundary is clean.

## Establish intent

Reconstruct from the request, accepted decisions, repository authority, and
runtime evidence:

- intended outcome and user value;
- accepted design and tradeoffs;
- data model, ownership, lifetimes, states, transitions, and invariants;
- intentional removals, behavior changes, non-goals, and unchanged behavior;
- affected callers, operators, and real interfaces;
- proof that would distinguish success from a plausible regression.

Review the complete relevant system, not only the diff. A concern that requires
changing accepted intent is a design conflict, not an implementation defect.
Route that choice through `grill-me`; do not disguise it as a repair.

## Start with data

Use the Torvalds maxim as a hypothesis lens:

> Bad programmers worry about the code. Good programmers worry about data
> structures and their relationships.

Inspect the data structures and relationships before local control flow. Find
the owner of each datum, invariant, mutation, and transition. Look for duplicate
authority, invalid representable states, leaked lifecycle knowledge, conversions
that erase meaning, and names that misstate the domain.

Prefer designs that define errors out of existence. Make invalid states
unrepresentable when the existing language and interface can do so directly.
Do not add validation, retries, branches, or recovery for states a better model
can eliminate.

## Seek strategic simplicity

Judge the whole codebase after the change, not whether the new code is locally
small. The shipped system should be simpler, more elegant, and more robust than
before.

Use Ousterhout's strategic-design lens:

- make modules deep: small stable interfaces hiding necessary complexity;
- pull special cases and policy behind the owner instead of leaking them to
  callers;
- remove shallow wrappers, pass-through methods, temporal coupling, and
  configuration that transfers complexity elsewhere;
- spend complexity only where it removes more complexity from the system over
  its expected life.

Challenge every new requirement, layer, branch, state value, fallback,
compatibility path, abstraction, option, and test fixture. Delete obsolete code,
aliases, comments, tests, configuration, scaffolding, and dependencies. Look
beyond the touched lines for nearby machinery the change makes unnecessary.
Do not preserve residue because deletion was not named in the request.

## Prove behavior

Review correctness, errors, concurrency, security, compatibility, data
integrity, performance, and operator failure paths against concrete behavior.
Trace representative inputs from the real interface through effects and back to
observable output or state.

Tests must defend intent and behavior:

- assert outcomes, boundaries, invariants, transitions, precedence, and real
  errors;
- avoid source-text assertions, call-count choreography, private helpers, mocks
  of the implementation under test, and incidental defaults;
- prefer the real boundary; use a test only when the changed contract cannot be
  proved more directly;
- require each test to fail on a plausible defect.

## Findings and repair

A finding requires:

- exact file, symbol, interface, or behavior;
- a concrete failing path or maintenance mechanism;
- evidence;
- the smallest coherent source repair;
- observable proof.

Exclude taste, generic best practices, speculative hardening, and style nits.
Zero findings is valid.

Track every finding. Delete first, then simplify the necessary system. Fix the
source rather than suppressing a symptom or special-casing the observed input.
Migrate every caller and remove obsolete paths; do not leave compatibility
shims unless accepted intent requires them.

Run the narrowest real scenario for each repair, then applicable behavioral
contract tests. A failed check is a new finding. Restart the review over the
same boundary, including the repairs.

Finish only when no supported finding remains, the real behavior is proved,
unchanged invariants hold, and the codebase contains no obsolete path exposed
by the change. Report repaired findings, deleted complexity, exact proof, and
any external blocker.

## Interactive walkthrough
When a review identifies structural choices, accepted trade-offs, or complex
repairs worth operator discussion, use `skill://hunk` to open an annotated diff
in Herdr and walk the operator through the changes.