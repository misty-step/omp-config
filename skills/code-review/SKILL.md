---
name: code-review
description: Run a gated lens council, filter findings through a taste gate, and wait for the operator before repairing.
disable-model-invocation: true
---

# Code Review

Review the completed change. Do not edit production code until the operator
has accepted or rejected each Take finding.

## 1. Establish intent

Reconstruct from the request, accepted decisions, repository authority, and
runtime evidence:

- intended outcome and user value;
- accepted design and tradeoffs;
- data model, ownership, lifetimes, states, transitions, and invariants;
- intentional removals, behavior changes, non-goals, and unchanged behavior;
- affected callers, operators, and real interfaces;
- proof that would distinguish success from a plausible regression.

Review the complete relevant system, not only the diff. A concern that
requires changing accepted intent is a design conflict. Stop and hand it to
the operator to route through `/explore-unknowns`; do not disguise it as a
repair.

Completion criterion: Intent, invariants, and proof are written.

## 2. Select lenses

A change is **trivial** when it is local, touches no public interface, adds
no state, and does not change an error or concurrency path. Trivial default:
`thermo` and `torvalds`.

Otherwise, or when the operator invoked this skill by name on a non-trivial
change, run the full council:

| Lens | File | Job |
|---|---|---|
| thermo | `references/thermo.md` | Ambitious code-judo, file size, spaghetti growth |
| ousterhout | `references/ousterhout.md` | Deep modules, leaked complexity |
| torvalds | `references/torvalds.md` | Data, invalid states, ownership |
| carmack | `references/carmack.md` | Practicality, inspectability, hot-path cost |
| uncle-bob | `references/uncle-bob.md` | Robustness and error boundaries |
| kcd | `references/kcd.md` | Behavioral tests and readable contracts |
| taelin | `references/taelin.md` | Erasure, reduction, a smaller program |
| ponytail | `references/ponytail.md` | YAGNI; the laziest solution that works |

The operator may name a subset or force the full council.

Completion criterion: The lens set is listed with the trivial/full reason.

## 3. Council

Launch one read-only scout per selected lens. Give each scout the intent,
the diff, the target files, and only its reference file.

Each scout returns at most five findings. A finding has:

- exact file, symbol, or behavior;
- the failing mechanism;
- evidence;
- the smallest coherent repair;
- severity: `block`, `should`, or `note`.

Zero findings from a lens is valid.

Completion criterion: Every selected lens has a harvested result.

## 4. Synthesize

Dedupe overlapping findings. Assign one primary lens. Drop nits that do not
change behavior, ownership, or future change cost.

**Taste gate.** For each remaining finding, judge the repair against the
running system, not the diff polish. All four must hold, or the finding
must remove an invalid representable state:

- simpler (less machinery, one owner, no relocated complexity);
- more robust (failure is visible; bad input cannot become valid state);
- more elegant (the model matches the domain);
- Torvalds-tasteful (invalid states unrepresentable; one owner per datum).

Classify:

- **Take** — passes the gate. This is the only class the operator is asked
  about. At most one follow-up Take that sits outside the ticket. If several
  pass, pick the one that most improves the running model and defer the rest.
- **Hygiene** — colocation, test shape, naming, DRY, comment, or a move that
  does not change runtime state. Do not ask. Record under Deferred.
- **Refuse** — style, speculative extensibility, or extra scope that fights
  the ticket. Drop, or put under Conflicts with accepted intent.

Do not present a flat accept/reject list that mixes Take and Hygiene. The
operator must not have to ask whether the findings improve the design.

Write one report to an OS temp path (not the repository):

```markdown
# Code review
- Scope:
- Intent:
- Lenses:

## Taste
- Take: `<id>` — <one sentence: what invalid state or dual owner it removes>
- Hygiene (not asking): <ids or none>
- Follow-up: <one Take outside this ticket, or none>

## Findings
1. [block|should|note] lens=`<name>` `<file>:<symbol>`
   Evidence:
   Repair:

## Deferred
## Conflicts with accepted intent
```

`## Findings` lists Take items only. Hygiene lives in Deferred.

Write a Hunk sidecar at a sibling `.json`. This is a walkthrough, not a
findings dump. Include:

- one note per load-bearing changed decision (owner, interface, callers, proof);
- every Take finding that has a changed-line target.

Schema: `comments[].filePath`, `newLine` or `oldLine`, `summary`, `rationale`.
Number tour notes `1/N`. Apply them to the live Hunk session (`skill://hunk`
Walkthrough). Do not present a review as complete while the viewer sits on
an unannotated first file with `liveCommentCount` 0.

Present the report. Lead with Taste. Stop.

Completion criterion: The report is on disk, shown to the operator with a
Taste verdict, the Hunk session has the walkthrough notes and is focused on
note `1/N`, and no production edit has been made.

## 5. Repair

After the operator accepts, rejects, or defers each Take finding, repair
only the accepted set. Do not promote Hygiene unless the operator names it.
Delete first. Fix the source. Migrate every caller. Remove obsolete paths.

Run the narrowest real scenario for each repair, then applicable contract
tests. A failed check is a new finding. If repairs were non-trivial, re-run
the same lens set over the repaired boundary and stop again at a new report.

Use `skill://hunk` when the operator wants an annotated walkthrough.

Completion criterion: Every accepted Take finding is repaired and proved, or
an external blocker is named. Rejected, deferred, and Hygiene items are
untouched.
