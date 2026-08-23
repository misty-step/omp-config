---
name: deliver
description: Take one accepted spec or ready ticket to a proved, reviewed, tight, unmerged pull request.
disable-model-invocation: true
argument-hint: "[spec or ready ticket]"
---

# Deliver

One ready slice. Lights off through implementation, QA, and supported repairs.
Then stop at an unmerged pull request.

```text
claim -> isolate -> plan proof -> implement -> test and QA -> review and repair
-> tighten -> publish
```

## 1. Claim

If the invocation names a spec or ready ticket, resolve and claim that target.
Register or link a durable spec in the trusted ledger before implementation.
Use the highest-priority ready ledger item only when no target is supplied.
Skip claimed, blocked, superseded, or unshaped work.

The work is ready only when accepted intent defines the outcome, data and
ownership, invariants, interfaces, failure and recovery behavior, non-goals,
acceptance scenarios, QA surfaces, and release boundary. If a builder must
invent a material choice, stop and ask the operator to run `/shape`.

Completion criterion: One accepted, independently useful slice is claimed.

## 2. Isolate

Use a worktree from the current default branch. Leave the operator's branch and
unrelated work unchanged. Record the exact base revision.

Completion criterion: The slice has one isolated checkout and one owner.

## 3. Plan proof

Before the first production edit, map each observable claim to:

- a behavioral test that fails on a plausible defect;
- a real-interface scenario;
- a fixture and expected result;
- required baseline evidence;
- production signals and rollback checks.

Read `skill://evidence-packet`. Capture required baselines now.

Completion criterion: Every acceptance claim has a behavioral-test decision,
real-interface scenario, fixture, expected result, applicable baseline, and
applicable production signal and rollback check. Each non-applicable element
has an explicit reason. Every required baseline is captured before
implementation.

## 4. Implement

Implement the smallest coherent design. Work by dependency-ordered slices.
Make illegal states unrepresentable. Give each datum one owner and one path.
Fix the source, migrate every caller, and delete obsolete code, configuration,
tests, and documentation. Record deviations from the accepted spec.

Continue autonomously for conservative reversible deviations. Stop for an
intent, scope, compatibility, spend, destructive, or hard-to-reverse change.

Completion criterion: The accepted slice is complete with all callers migrated
and no obsolete path left.

## 5. Test and QA

Run the repository's tight checks and the applicable broader suite. Then start
every affected application and exercise the product surface as a user or
operator would.

Execute the accepted QA matrix. Cover:

- happy, boundary, risky, and illegal inputs;
- errors, interruption, retry, restart, and recovery;
- adjacent behavior around the changed path;
- every affected API, CLI, UI, TUI, persisted state, and operator surface;
- accessibility and viewport variants for UI;
- concurrency, ordering, and idempotency when applicable;
- release identity, health, and rollback probes for operated software.

Inspect every captured artifact. Automated tests, lint, CI, screenshots, and
logs do not substitute for exercising the real behavior they claim to prove.

Completion criterion: All checks pass, every QA scenario has an observed
result, and every evidence artifact is inspected.

## 6. Review and repair

Run `omp config path`. Read `references/review/COUNCIL.md` below that agent
directory and the lens files its Select section chooses. Apply the shared
Select, Run, and Classify contract to the complete system, accepted intent,
tests, QA, and evidence.

When the shared contract requires `/security-review`, stop and ask the operator
to run it. Resume only from its triaged findings.

Accepted security findings remain under `/security-review` model policy. Stop
delivery until an approved external repair lands and passes re-audit. The
primary does not design or apply that repair.

Repair every in-scope Blocker and in-scope Take autonomously. Route
out-of-scope Blockers to the operator with evidence and an owner. Rerun the
proof affected by each repair, then rerun the same groups. Repeat until:

- no in-scope Blocker or in-scope Take remains;
- all tests and QA are green;
- the same finding does not recur.

If a finding conflicts with accepted intent, expands scope, recurs after a
coherent repair, or needs external security remediation, suspend delivery.
Record every blocker with evidence and an owner. Stop before Tighten or
Publish. Resume at Review and repair after every blocker is resolved.

Completion criterion: The review loop has zero in-scope Blockers and Takes,
green tests and QA, final evidence, and no external blocker.

## 7. Tighten

Challenge, delete, then simplify. Remove incidental state, pass-through
wrappers, speculative flexibility, duplicate owners, stale comments, temporary
scaffolding, and test-only production seams.

After tightening, rerun affected tests and QA. Rerun the same review groups on
the complete final diff. Return to the repair loop for every in-scope Blocker
or in-scope Take. Tidy the green result into semantic commits.

Completion criterion: The final commit set has green tests, QA, and council
results. No supported deletion or simplification remains inside the slice.

## 8. Publish

Open an unmerged pull request. Include the work item, accepted spec, decisions,
tests, QA observations, inspected evidence, review-loop verdict, risks,
release plan, rollback path, and production signals.

Open the numbered annotated walkthrough with `skill://hunk`. Leave operator
focus unchanged. Merge and deploy belong to explicit `/release`.

Completion criterion: The operator can review one unmerged PR, step every
load-bearing change, inspect the proof, and make only the release decision.

