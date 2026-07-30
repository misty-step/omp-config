# Target-state rubric

Write the target state as verifiable clauses. Each clause below becomes a
concrete statement about the audited system, with the modules and interfaces
named. Auditors cite the clause a finding violates.

## Strategic design

Working code is not enough. Judge every structure by the change it makes to
future modification cost, not by whether it runs today. Name the places where
tactical shortcuts accreted structure nobody chose. The target state says what
the system's load-bearing abstractions are and why each earns its keep.

## Deep modules

Each module offers a lot of behavior behind a small interface. State, per
named module, the interface a caller must learn and the complexity it hides.
Flag the inverse shapes:

- Shallow module: interface cost near implementation cost.
- Pass-through: a layer that forwards calls and adds no abstraction.
- Generic-name smell: `Manager`, `Util`, `Helper` naming a module with no
  contract of its own.

Apply the deletion test: if deleting the module makes complexity vanish, it
was a pass-through; if complexity reappears across N callers, it was earning
its keep.

## Complexity ownership

Pull complexity downward. A module owns its own difficulty instead of
exporting it as configuration, caveats, ordering rules, or error handling that
every caller must repeat. The target state names, for each hard problem, the
single module that owns it. Change amplification — one conceptual change
forcing edits in many places — marks unowned complexity.

## Information hiding

Each design decision lives inside exactly one module. Data structures,
algorithms, storage formats, and dependency choices do not leak through the
interface. Temporal decomposition — modules shaped by execution order rather
than by knowledge — is the leak to name explicitly.

## Contracts and tests

Every public interface has a stated contract: inputs, outputs, invariants,
error behavior. Tests defend the observable contract and its rigorous
constraints — boundaries, transitions, precedence, and real error paths — and
fail on a plausible mutation of the changed logic. Tests that assert internal
structure, mock owned seams, or execute lines without defending a contract do
not count toward the target. The `review-tests` skill holds the normative
checks; do not restate them, apply them.
