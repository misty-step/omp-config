---
disable-model-invocation: true
name: quality-toolchain
description: Dispatch an audit-assess-remediate program that takes a repository's lint, build, typecheck, and hook gates to an explicit target state.
argument-hint: "[repo-path] [--audit-only]"
---

# /quality-toolchain

Take one repository's engineering toolchain from its current state to an
explicit, evidenced target state.
This skill is a dispatch program. The owning lane composes, supervises, and
integrates subagent lanes. It does not audit or remediate inline.

## Scope

Own: strict and project-specific linting, builds, type checks, formatting,
pre-commit and pre-push hooks, and the observability and tamper resistance of
those gates. This is the quality-tooling slice: build-time gates only.

Route away:

- automated test system depth → `skill://quality-tests`
- CI architecture, gate tiers, and gate running → `global/skills/ci/SKILL.md`
- whole-repo fitness profile → `global/skills/project-engineering/SKILL.md`
- standing gate floor and tiering → `global/references/quality-gates.md`
- live-behavior QA and runtime operations → the `qa`/`verify-live` and
  operations lanes; never this program

## Program

Compose lanes per `global/skills/dispatch/SKILL.md` and return its manifest
fields before spawning each substantive lane. Dispatch independent lanes together.

| Phase | Lane | Output | Completion criterion |
|---|---|---|---|
| 1. Inventory | `scout` per language or tool family; `sonic` for mechanical enumeration | `inventory.surfaces[]` in the assessment | every language, manifest, lint/format/typecheck config, build entrypoint, hook config, CI workflow, baseline, and repo-owned gate command is listed; every absence is recorded as a fact |
| 2. Target state | owning lane, no subagent | `targets[]` in the assessment | every surface in `references/target-state.md` has a target with a named failure mode, or a not-applicable reason |
| 3. Audit | ad-hoc read-and-run lanes, one per surface; no edits | `findings[]` with evidence | every target has a pass or a gap; every gap carries a command transcript or file path; no finding rests on declaration |
| 4. Assess | owning lane; operator for contested decisions | durable assessment per `global/references/quality-assessment.md` | every finding carries remediate, waive (reason + approver + expiry), or defer (ticket) |
| 5. Remediate | `builder` or `fixer`, one per independent gap cluster | diffs plus updated findings | every accepted gap is closed or returned with a named blocker; no gate weakened to pass |
| 6. Verify | fresh `qa` lane, never a remediating lane | gate transcripts in the assessment | every gate runs green from a clean tree, and one seeded violation per new or changed gate proves it can fail |

`--audit-only` stops after phase 4.

## Target state

Load `references/target-state.md` before phase 2.
Derive targets from the quality-gates floor plus repo evidence. Every target
names the real failure it catches; delete targets that name none. Gate the
diff, ratchet the baseline; never demand a big-bang legacy cleanup.

## Hard to weaken

- Gate configs, thresholds, and baselines are committed and versioned. Hooks
  are convenience; CI re-runs the same repo-owned contract as enforcement.
- Baselines only shrink. A rule disable, severity downgrade, exclusion
  widening, or threshold lowering is a finding, not a fix; each needs a waiver
  with reason and expiry in the assessment.
- Every gate is one repo-owned command with a durable report path. A gate
  nobody can run by name is a gap.
- Falsifiability is part of verification: prove each new or changed gate fails
  on a seeded violation — bad format, lint violation, type error, blocked
  commit — then passes clean.

## Completion Gate

See `global/references/verification-system-first.md` for the shared proof
contract. Add:

- assessment paths (`.evidence/quality/quality-toolchain/assessment.json` +
  `.md`) and the revision audited
- gates run with exact commands and exit codes, including falsifier runs
- remediation diffs and the gate that verified each
- waivers granted with approver and expiry; deferred findings with ticket
- residual gaps, or none with reason
