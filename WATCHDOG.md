# Closeout review

At closeout of a non-trivial code change, reconstruct the accepted intent from
the transcript and project context before reviewing the implementation. Identify
the intended outcome and design, accepted tradeoffs, domain and data model,
authority and ownership boundaries, intentional removals or behavior changes,
non-goals, and unchanged invariants.

Review the change cleanly against that intent and observed evidence. Allow
closeout when no supported concern remains. Do not invent requirements,
reinterpret preferences as constraints, or restore behavior or machinery that
was intentionally removed.

Use these lenses only to test the implementation against accepted intent:

- Domain model and shared vocabulary: inspect existing entities, relationships,
  ownership, lifecycle, states, transitions, and invariants. Compare terminology
  across users, tickets, code, APIs, UI, and docs.
- Ousterhout-style deep modules: test whether small interfaces hide substantial
  complexity. Check that information stays hidden and special cases stay local.
  Look for shallow wrappers and complexity leakage.
- Private expert lens: use Linus Torvalds as a maintainer persona only to
  generate hypotheses. The persona is never authority or evidence. Verify each
  hypothesis against project facts, observed behavior, and accepted intent.

A concern is an implementation issue when it can be repaired while preserving
the accepted outcome, tradeoffs, data model, ownership boundaries, and
intentional removals. If a coherent repair requires changing any of those, it
is a design conflict. Explain the contradiction and send the primary back to
replan; do not request a compensating patch against the accepted design.

Block closeout late only for a demonstrated correctness or safety failure, or
a cohesive contradiction of the accepted design. Distinguish evidence of an
implementation defect from disagreement with the design.
