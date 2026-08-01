---
disable-model-invocation: true
name: quality-tests
description: Dispatch an audit-assess-remediate program that takes a repository's automated test system to an explicit target state of meaningful, rigorous test classes.
argument-hint: "[repo-path] [--audit-only]"
---

# /quality-tests

Take one repository's automated test system to an explicit target state:
only meaningful test classes, each rigorous, reproducible, budgeted, and
evidenced.
This skill is a dispatch program. The owning lane composes, supervises, and
integrates subagent lanes. It does not audit or remediate inline.

## Scope

Own: test-class selection and depth — unit, integration, end-to-end,
property, mutation, jitter, performance, torture — plus suite rigor, flake
control, timing budgets, and failure artifacts. This is the quality-tooling
slice: the repo-owned automated test system only.

Route away:

- diff-scoped test judgment → `global/skills/review-tests/SKILL.md`; this
  program applies the same checks suite-wide and inherits its fix-vs-weaken
  rule
- lint, build, typecheck, and hook gates → `skill://quality-toolchain`
- gate tiers and placement → `global/skills/ci/SKILL.md`
- live persona or exploratory QA against running products → the QA lanes,
  never this program

## Program

Compose lanes per `global/skills/dispatch/SKILL.md` and return its manifest
fields before spawning each substantive lane. Dispatch independent lanes together.

| Phase | Lane | Output | Completion criterion |
|---|---|---|---|
| 1. Inventory | `scout` per suite or framework; `sonic` for mechanical enumeration | `inventory.surfaces[]` in the assessment | every framework, suite, present test class, runtime and duration, CI wiring, coverage/mutation tool, seed source, fixture root, and CI flake history is listed; every absence is recorded as a fact |
| 2. Target state | owning lane, no subagent | selected and refused classes in `targets[]` | every class in `references/test-classes.md` is selected with trigger evidence or refused with the failing selection rule |
| 3. Audit | ad-hoc read-and-run lanes, one per selected class | `findings[]` with evidence | suites run with transcripts; `review-tests` checks 1–8 applied to the highest-risk contracts; durations measured against budgets; rerun-on-red flake sweep done |
| 4. Assess | owning lane; operator for contested decisions | durable assessment per `global/references/quality-assessment.md` | every finding carries remediate, waive (reason + approver + expiry), or defer (ticket) |
| 5. Remediate | `builder` or `fixer`, one per independent gap cluster | new or strengthened tests, fixed flakes | every accepted gap is closed or returned with a named blocker; no test weakened to pass |
| 6. Verify | fresh `qa` lane, never a remediating lane | one `gates[]` entry per suite run — transcript in `report`, disclosed seed in `seed`, seeded-bug result in `falsifier_verified` | the suite runs green twice from a clean state with seeds disclosed, and each new test fails on its seeded bug — a mutation or the reverted fix — before passing |

`--audit-only` stops after phase 4.

## Selection rules

A test class enters the target state only when all three hold:

1. The repo demonstrably has the failure mode the class detects — name the
   code, seam, or incident.
2. A falsifier is named: the concrete bug this class would catch that no
   cheaper selected class catches.
3. The class runs deterministically, or with seeded replayable randomness, in
   a named tier.

A class failing any rule is refused in the assessment with the failing rule.
Refusal with reason is a valid, expected outcome. Ceremony — a class added
for coverage optics or template compliance — is a finding, and its removal is
remediation.

Load `references/test-classes.md` before phase 2 and `references/rigor.md`
before phases 3 and 5.

## Completion Gate

See `global/references/verification-system-first.md` for the shared proof
contract. Add:

- assessment paths (`.evidence/quality/quality-tests/assessment.json` +
  `.md`) and the revision audited
- classes selected and refused, each with the rule and evidence cited
- suite commands, durations against budgets, exit codes, and seeds
- flakes found: fixed, or quarantined with ticket and deadline
- each new test's seeded-bug falsifier evidence
- residual gaps, or none with reason
