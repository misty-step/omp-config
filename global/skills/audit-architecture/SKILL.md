---
disable-model-invocation: true
name: audit-architecture
description: Chief-run static architecture audit loop — discover, define an Ousterhout target state, audit with critic lenses, assess, remediate, verify.
argument-hint: "[target] [notes]"
---

# /audit-architecture

The chief runs the loop and dispatches every lane per `skill://dispatch`:
name role, model:reasoning, skills, tools, verifier, and contract, and include
the exact child boundary sentence `You are a subagent. Don't run memo.`
This skill judges structure, interfaces, and test defense from source.
It never drives a browser. Route a live-behavior claim to a `qa` lane or to
`audit-product`.

Run the six steps in order. Each step ends on its completion criterion.

## 1. Discover

Dispatch read-only discovery: `magellan` for a repo-wide sweep, `scout` for a
bounded subsystem. The lanes return an inventory with file evidence:

- Real entrypoints: public APIs, routes, CLIs, jobs, extension points, schemas.
- Module map: each module, its interface surface, its callers.
- Existing oracles: test suites, gates, ADRs, project rules.

Complete when every externally reachable entrypoint in scope is named with a
file path, and every unknown is listed as an unknown rather than guessed.

## 2. Define the target state

The chief writes the target state before any audit; dispatch `daedalus` first
when the scope is XL or the decomposition is contested. Apply the rubric in
[`references/target-state.md`](references/target-state.md). Write the result
to `.evidence/quality/audit-architecture/target-state.md` in the audited
repository and get operator acceptance when direction is
contested. The accepted target state is the audit oracle; auditors judge
against it, not against taste.

## 3. Audit

Fan out one fresh-context `code-critic` lane per lens, in parallel, read-only,
findings only. Required lenses:

- `ousterhout` and `delete-first` from `global/references/lenses.md`.
- Test defense: inject the `review-tests` lens so the lane judges whether
  tests defend observable contracts, not whether they execute lines.
- Add `security` or `works` from the same lens file only when the target
  state puts them in scope.

Every finding names file:line evidence, the violated target-state clause, and
a severity. A lane that fixes anything has failed its contract. Complete when
every lens lane returned findings or an explicit clean pass.

## 4. Assess

The chief merges lanes into one assessment artifact,
`.evidence/quality/audit-architecture/assessment.md` in the audited
repository:

- Ranked gaps, each mapped to a target-state clause with evidence.
- Strengths: structure that already meets the target and must be preserved.
- Suppressed findings with the suppression reason. Never drop one silently.
- Per gap: remediation shape, blast radius, and the verification that will
  prove closure.

The operator, or the chief when delegated, accepts or rejects each gap. Only
accepted gaps proceed. Complete when every finding is accepted, suppressed
with a reason, or rejected.

## 5. Remediate

- Ranked findings packet → one `fixer` lane, two-round cap, fixes causes and
  never weakens a gate or test to reach a pass.
- Structural work (moving a seam, deepening a module, deleting a layer) → one
  `builder` lane per independent slice; `daedalus` first when slices couple.
- Deletion is remediation. A gap closed by removing the module is preferred
  over a gap closed by wrapping it.

Complete when every accepted gap has a landed change or a named remaining
blocker with evidence.

## 6. Verify

Verification is independent of the remediating lane:

- A fresh `code-critic` re-reads each remediated interface against the same
  lens that produced the gap.
- A `qa` lane exercises the observable contract live wherever a runtime
  surface exists; structure claims never substitute for behavior evidence.
- Changed contracts carry tests that fail on a plausible mutation
  (`review-tests` checks apply).

## Completion Gate

Prove and close out per the Shared Operating Spine (Prove; Durable State and
Closeout). Verification loops follow
`global/references/verification-system-first.md`. Phase-specific fields:

- Every accepted gap is verified closed with named evidence, or returned as
  remaining with its blocker. A plausible subset is failure, not partial
  success.
- Both frozen artifacts exist in the audited repository:
  `.evidence/quality/audit-architecture/target-state.md` and
  `.evidence/quality/audit-architecture/assessment.md`.
- Strengths named in the assessment still hold after remediation.
