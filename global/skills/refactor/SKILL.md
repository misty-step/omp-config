---
disable-model-invocation: true
name: refactor
description: |
  Architecture refactor mode. Set a concrete goal, refactor until the architecture
  is simpler and coherent, live-test after each significant step, autoreview,
  commit green milestones, and track progress in /tmp/refactor-{project}.md.
  Trigger: /refactor.

argument-hint: "[scope|subsystem]"
---

# /refactor

Refactor architecture deliberately.
Keep behavior stable unless the operator explicitly asks for product change.

## Goal Articulation

Set an explicit active goal with:

- **Outcome:** the architectural property that will be true.
- **Scope:** subsystem, files, routes, or public surface in bounds.
- **Fitness tests:** live command, route, consumer build, or browser path that
  must keep passing after each significant step.
  When the fitness test is not already a credible proof loop, define claim,
  falsifier, driver, grader, evidence packet, and cadence per
  `global/references/verification-system-first.md`.
- **Stop rule:** state what evidence means the architecture is good enough.


Good shape:

```text
Refactor <subsystem> so <responsibility> has one owning module, public callers
use <named interface>, and <live tests/routes> still pass after each milestone.
Stop when the diff removes the duplicated seam, reviewers find no blocking
architecture concern, and no broader behavior change is needed.
```

## Progress File

Create `/tmp/refactor-{project}.md` immediately and keep it current.
Use it as the handoff if the session ends.
Track the goal/scope/fitness/stop rule, the current architecture read
(modules, smells, constraints), the quality system
(`global/references/verification-system-first.md`), milestones (planned/active/done),
live-test receipts, review findings, commits, and residual risk.
Keep secrets and private customer data out of `/tmp`.

## Working Loop
1. **Read shape before edits.** Map module ownership, public interfaces,
   invariants, and the live verification path.
   If no live path exists, build or name the smallest credible one first.
   Keep this rule: a refactor without a behavior-preservation loop is a rewrite in disguise.

2. **Choose one architectural pressure.** Split ownership, shallow wrapper,
   dependency direction, duplicated data shape, or feature logic hiding in UI glue.
   See `global/references/delete-first.md` (Ponytail:
   `global/external/dietrich-ponytail/SKILL.md`).
   Do not tidy everything.
3. **Make one significant step** — a moved boundary, deleted abstraction,
   renamed public concept, data-flow simplification, or large-file split.
   Mechanical formatting is not a milestone.
   A step that you cannot test and commit independently is too large.
4. **Live-test immediately.** Use the repo's verification path, dispatch
   `verifier` with `verify-live`, or use the surface-specific route.
   Refactors can break integration seams.
   Unit tests alone do not close a milestone.
5. **Autoreview the milestone** with fresh-context critique when substantive.
   Give critics the artifact and oracle only.
   Never give them the author's reasoning trail (Shared Operating Spine: Prove).
   Here, give them the diff, architecture goal, and fitness tests.
   Scale critic topology with `global/references/verification-system-first.md`.
   A risky boundary change earns more than one lens.
   Fix blockers before continuing.
6. **Commit green milestones.** One concern per commit.
7. **Reassess the stop rule.** Continue only while another high-leverage
   architecture pressure remains in scope and the live loop stays cheap.

## Delegation Judgment

Delegate according to the Shared Operating Spine (Act).
Useful lanes include a `researcher` to map ownership and coupling before edits,
a `verifier` with `thermo-nuclear-code-quality-review` to challenge the goal or
a milestone diff, and a fresh `verifier` with `verify-live` to exercise the live
surface when the lead cannot drive it cheaply.

Default harsh critique uses a `verifier` with
`thermo-nuclear-code-quality-review`.
Read the projected skill at
`global/skills/thermo-nuclear-code-quality-review/SKILL.md`.
It is standalone and does not require a special vendor harness.
Use it for milestone diffs that add abstractions, split modules, cross file-size
thresholds, or claim cleaner architecture.

Use `julius-caveman` only for interim synthesis.
Keep findings, code, commits, and final artifacts in normal English.


## Stop Conditions

Stop and report instead of improvising when:

- The refactor requires product behavior changes.
- The live verification loop is absent and cannot be built cheaply.
- Three edits hit the same file without simplifying the architecture.
- A milestone breaks a public contract and no migration path is obvious.
- Review says the goal is vague, unmeasurable, or already satisfied.

## Gotchas

- **Unmeasured oracle.** Treat "Happy" as non-evidence.
  The stop rule needs a diff, live proof, and review signal.
- **Architecture appearance.** Renames, folders, and wrappers do not count unless
  they reduce coupling, clarify ownership, or delete a real failure mode.
- **Unprotected change.** A god-file split or corrected dependency direction
  needs a gate that prevents regression.
Ratchet the structural win into a standing gate — a fitness function, a god-file baseline — per
`global/references/quality-gates.md`.


## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract.
`/refactor` adds:
the goal stop rule satisfied or explicitly blocked;
a live-test receipt for every significant step;
blocking review findings fixed or rejected with a reason;
meaningful milestones committed; and
`/tmp/refactor-{project}.md` naming final architecture, commits, verification,
residual risk, and follow-up pressure outside scope.
