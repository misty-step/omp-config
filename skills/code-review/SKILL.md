---
name: code-review
description: Run a multi-angle review, repair supported defects, and repeat until the complete change is tight.
disable-model-invocation: true
argument-hint: "[change, pull request, or commit]"
---

# Code Review

Review the completed system, not only its diff. Repair supported in-scope
findings. Repeat until green.

## 1. Resolve the target

Use the named change, pull request, or commit. For a pull request, create its
dedicated checkout. For a commit, create an isolated repair branch and
worktree from that commit. Default to the current change only when the
invocation names no target.

Record the base, head, diff, and writable checkout before review. Leave the
operator's branch unchanged.

Completion criterion: One exact target and isolated repair destination exist.

## 2. Establish intent

Reconstruct from the request, accepted decisions, repository authority, and
runtime evidence:

- outcome and user value;
- data, owners, lifetimes, states, transitions, and invariants;
- interfaces, callers, operators, and compatibility;
- intentional changes, removals, non-goals, and unchanged behavior;
- tests, QA scenarios, production signals, and rollback;
- proof that separates success from a plausible regression.

A concern that changes accepted intent is a design conflict, not a repair.

Completion criterion: Intent, invariants, scope, and proof are explicit.

## 3. Load the council

Run `omp config path`. Read `references/review/COUNCIL.md` below that agent
directory. Read only the sibling lens files selected by its Select section.

Completion criterion: The shared council contract and selected references are
loaded from the deployed plain-reference source.

## 4. Council

Apply Select, Run, and Classify from the shared council contract. Review the
complete relevant system, tests, QA observations, and inspected evidence.

Completion criterion: Every selected group returns, and every supported
finding is Blocker, Take, or Drop.

## 5. Repair loop

Security-review findings remain under `/security-review` model policy. Record
accepted guidance and stop. Do not design or apply that repair until an
approved writable mechanism or external repair exists. Re-audit an external
repair before resuming this loop.

Repair all in-scope Blockers and in-scope Takes. Route out-of-scope Blockers
to the operator with evidence and an owner. Delete first. Fix the source.
Migrate every caller. Remove obsolete paths. Run the narrowest real scenario
and applicable contract tests after each repair.

Then rerun the same council over the repaired boundary. Continue until:

- zero in-scope Blockers and in-scope Takes remain;
- tests and product-surface QA are green;
- evidence matches the final behavior.

Stop and ask the operator only when a repair changes accepted intent or scope,
requires a hard-to-reverse choice, or the same supported finding recurs after a
coherent repair. A failed check is a new finding.

Completion criterion: The loop is green, one explicit decision blocks it, or
an accepted security finding has one named external remediation blocker.

## 6. Report

Write one report and one numbered Hunk sidecar to OS temporary paths:

```markdown
# Code review
## Target, intent, and scope
## Council groups
## Cycles and repairs
## Final verdict
## Dropped and out-of-scope findings
## Proof and residual risk
```

The sidecar covers each load-bearing decision, repaired finding, caller
migration, and proof. Write it before choosing an interactive or
non-interactive delivery path.

In an interactive Herdr session, open the annotated walkthrough per
`skill://hunk` and preserve operator focus. Otherwise return both artifact
paths without launching Hunk.

Completion criterion: The final verdict is green, or the report names every
blocking decision and external remediation blocker. Both artifacts exist. An
interactive walkthrough is loaded with live numbered notes, or a
non-interactive response returns both paths. No supported finding or failed
check remains hidden.
