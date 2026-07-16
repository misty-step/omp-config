---
name: refactor
description: |
  Architecture refactor mode: set a concrete improvement goal, refactor until
  the architecture is simpler and coherent, live-test after each significant
  step, autoreview, commit green milestones, and track progress in
  /tmp/refactor-{project}.md. Use when: "refactor this", "clean up the
  architecture", "make the design better", "refactor until you're happy",
  "pay down design debt", "simplify this subsystem". Trigger: /refactor.
argument-hint: "[scope|subsystem]"
---

# /refactor

Refactor architecture deliberately. Keep behavior stable unless the operator
explicitly asks for product change.

## Goal Articulation

Set an explicit active goal — not "refactor until happy," a goal with:

- **Outcome:** the architectural property that will be true.
- **Scope:** subsystem, files, routes, or public surface in bounds.
- **Fitness tests:** live command, route, consumer build, or browser path that
  must keep passing after each significant step. When the fitness test is not
  already a credible proof loop, define claim, falsifier, driver, grader,
  evidence packet, and cadence per
  `primitives/shared/references/verification-system-first.md`.
- **Stop rule:** what evidence means the architecture is good enough.

Good shape:

```text
Refactor <subsystem> so <responsibility> has one owning module, public callers
use <named interface>, and <live tests/routes> still pass after each milestone.
Stop when the diff removes the duplicated seam, reviewers find no blocking
architecture concern, and no broader behavior change is needed.
```

## Progress File

Create `/tmp/refactor-{project}.md` immediately and keep it current — it is the
handoff if the session dies. Track the goal/scope/fitness/stop rule, the current
architecture read (modules, smells, constraints), the quality system
(`primitives/shared/references/quality-system.md`), milestones (planned/active/
done), live-test receipts, and review findings, commits, and residual risk. No
secrets or private customer data in `/tmp`.

## Working Loop

1. **Read shape before edits.** Map module ownership, public interfaces,
   invariants, and the live verification path. If no live path exists, build or
   name the smallest credible one first — a refactor without a
   behavior-preservation loop is a rewrite in disguise.
2. **Choose one architectural pressure.** Split ownership, shallow wrapper,
   dependency direction, duplicated data shape, feature logic hiding in UI glue.
   See `primitives/shared/references/delete-first.md` (Ponytail:
   `primitives/skills/.external/dietrich-ponytail/SKILL.md`). Do not tidy
   everything.
3. **Make one significant step** — a moved boundary, deleted abstraction,
   renamed public concept, data-flow simplification, or large-file split.
   Mechanical formatting is not a milestone, and a step you cannot test and
   commit independently is too large.
4. **Live-test immediately.** Use the repo's verification path, `/qa`, or the
   surface-specific route. Refactors break integration seams; unit tests alone
   do not close a milestone.
5. **Autoreview the milestone** with fresh-context critique when substantive.
   Critics get the artifact and the oracle only — never the author's reasoning
   trail (Shared Operating Spine: Prove); here that's the
   diff + architecture goal + fitness tests. Scale critic topology with
   `primitives/shared/references/quality-system.md`; a risky boundary change
   earns more than one lens. Fix blockers before continuing.
6. **Commit green milestones.** One concern per commit.
7. **Reassess the stop rule.** Continue only while another high-leverage
   architecture pressure remains in scope and the live loop stays cheap.

## Delegation Judgment

Delegate per the Shared Operating Spine (Act). Useful
lanes: an Explore lane to map ownership and coupling before edits, a critic lane
to attack the goal or a milestone diff, a QA lane to exercise the live surface
when the lead cannot drive it cheaply.

Default harsh critic: the synced `thermo-nuclear-code-quality-review` skill
(`primitives/skills/.external/cursor-thermo-nuclear-code-quality-review/SKILL.md`)
for milestone diffs that add abstractions, split modules, cross file-size
thresholds, or claim "cleaner architecture." julius-caveman for interim
synthesis only; findings, code, commits, and final artifacts stay normal
English.

## Stop Conditions

Stop and report instead of improvising when:

- The refactor requires product behavior changes.
- The live verification loop is absent and cannot be built cheaply.
- Three edits hit the same file without simplifying the architecture.
- A milestone breaks a public contract and no migration path is obvious.
- Review says the goal is vague, unmeasurable, or already satisfied.

## Gotchas

- **Vibes as oracle.** "Happy" is not evidence. The stop rule needs a diff,
  live proof, and review signal.
- **Architecture theater.** Renames, folders, and wrappers do not count unless
  they reduce coupling, clarify ownership, or delete a real failure mode.
- **Unfenced win.** A god-file split or corrected dependency direction with no
  gate to stop it regrowing comes back. Ratchet the structural win into a
  standing gate — a fitness function, a god-file baseline — per
  `primitives/shared/references/quality-gates.md`.

## Completion Gate

See `primitives/shared/AGENTS.md` (Prove; Durable State and Closeout) for the
shared core. `/refactor` adds: the goal stop rule satisfied or explicitly
blocked; a live-test receipt for every significant step; blocking review
findings fixed or rejected with a reason; meaningful milestones committed; and
`/tmp/refactor-{project}.md` naming final architecture, commits, verification,
residual risk, and follow-up pressure outside scope.
