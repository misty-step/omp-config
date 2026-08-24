# Stage 2 — Deletion Gate (Shrink Before You Split)

A split preserves what exists. Delete what should not survive the move before
designing the boundary.

## Procedure

1. **Apply the deletion test to every module in the candidate.** For each file
   or submodule inside the candidate, ask: if this were deleted today, would
   complexity concentrate in one clear owner, or scatter? Record **keep**,
   **delete**, **merge into owner**, or **defer with reason**.
2. **Speculative abstractions.** Hunt and mark for deletion:
   - interfaces with a single implementation and no external consumer;
   - abstract base classes that add no invariant over a concrete type;
   - generic wrappers that only forward to one backend;
   - "future flexibility" parameters never read;
   - adapter layers that translate between identical shapes.
3. **Single-impl interfaces.** For each interface in the candidate:
   - list implementations and external consumers;
   - if one impl and no out-of-candidate consumer, mark **inline or delete**;
   - if one impl but external consumers, mark **keep surface, delete interface**
     or **narrow to the concrete type** with caller migration noted.
4. **Dead flags and config.** Grep for feature flags, env keys, and config
   fields touched only inside the candidate. Mark flags that are always true or
   always false, keys with no reader, and config branches that never fire.
   Propose deletion or consolidation before extraction.
5. **Pass-through adapters.** Identify modules that only re-export, rename, or
   forward calls without adding invariant, telemetry, or error translation.
   Mark **delete and migrate callers to the underlying owner**.
6. **Test-only production seams.** Find exports, hooks, or `#[cfg(test)]`
   gates that exist only to support tests. Mark **move seam to test package** or
   **delete and rewrite tests against the public boundary**.
7. **Update the coupling map.** Remove deleted modules from Stage 1's map.
   Re-run fan-in on symbols marked for deletion — callers must migrate or
   disappear. Record net deletion: files, lines, flags, and interfaces removed.
8. **Deletion ledger.** Use the
   [Deletion ledger template](artifacts.md#deletion-ledger) in `artifacts.md`.

## Completion criterion

Every file and submodule inside the candidate has a deletion-test verdict.
Every speculative abstraction, single-impl interface, dead flag, pass-through
adapter, and test-only seam is listed with evidence and a **delete**, **merge**,
or **defer** decision. Deferred items have an explicit reason and owner. The
deletion ledger is complete. The coupling map reflects post-deletion scope —
no symbol marked for deletion remains on the map without a migration note.
