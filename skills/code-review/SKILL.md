---
name: code-review
description: Review a completed change through a lens council, filter findings through a taste gate, and stop for the operator before repairing.
disable-model-invocation: true
---

# Code Review

Operator-invoked deep review of a completed change. Report findings and stop;
repair only after the operator rules on each Take.

## 1. Intent

Reconstruct from the request, accepted decisions, repository authority, and
runtime evidence: intended outcome, invariants, intentional removals and
non-goals, affected callers and real interfaces, and the proof that separates
success from a plausible regression. Review the complete relevant system, not
only the diff. A concern that requires changing accepted intent is a design
conflict — route it through `grilling`; do not disguise it as a repair.

## 2. Lenses

Trivial change (local, no public interface, no new state, no error or
concurrency path): default to `thermo` and `torvalds`. Otherwise run the full
council; the operator may name a subset.

| Lens | Job |
|---|---|
| thermo | Ambitious code-judo, file size, spaghetti growth |
| ousterhout | Deep modules, leaked complexity |
| torvalds | Data, invalid states, ownership |
| carmack | Practicality, inspectability, hot-path cost |
| uncle-bob | Robustness and error boundaries |
| kcd | Behavioral tests and readable contracts |
| taelin | Erasure; a smaller program |
| hickey | Simple vs easy; decomplecting; necessary complexity |
| ponytail | YAGNI; the laziest solution that works |

Each lens's reference lives in `references/<lens>.md`. Launch one read-only
scout per lens with the intent, the diff, and only its reference file. Each
returns at most five findings: exact target, failing mechanism, evidence,
smallest coherent repair, severity (`block`, `should`, or `note`). Zero
findings is valid.

## 3. Taste gate

Dedupe overlapping findings, then judge each repair against the running
system, not diff polish. A finding is a **Take** only when its repair is
simpler, more robust, more elegant, and removes an invalid representable
state or a dual owner — otherwise drop it.

- **Take** — the only class the operator is asked about. At most one
  follow-up Take outside the ticket.
- **Hygiene** — no runtime state change; record under Deferred, do not ask.
- **Refuse** — style, speculative extensibility, or scope that fights the
  ticket.

## 4. Report

Write one report to an OS temp path: Taste verdict first, then Take findings
with evidence and repair, then Deferred and Conflicts with accepted intent.
Write a Hunk sidecar beside it and open the walkthrough per `skill://hunk`:
one note per load-bearing decision plus every Take with a changed-line
target, numbered `1/N`, `liveCommentCount` > 0, viewport on note 1.

Present the report and stop.

Completion criterion: report shown with a Taste verdict, Hunk annotated and
focused on note 1, no production edits made.

## 5. Repair

After the operator rules, repair only the accepted set. Delete first; fix the
source; migrate every caller. Prove each repair with the narrowest real
scenario, then contract tests; a failed check is a new finding. If repairs
were non-trivial, re-run the same lenses over the repaired boundary and stop
at a new report.

Completion criterion: every accepted Take repaired and proved, or an external
blocker named. Rejected, deferred, and Hygiene items untouched.
