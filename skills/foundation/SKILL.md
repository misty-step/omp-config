---
name: foundation
description: Inspect a project, agree on one engineering gap, and install the smallest useful control.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Foundation

Install one project-owned control for an observed gap. Do not impose a standard
stack or checklist.

## Inspect

Read the current build, test, run, CI, release, operating, and review paths.
Find the smallest gap that makes change unsafe or unnecessarily difficult.
Repeated confirmed comments about one locally decidable violation justify an
executable control; an equivalent existing control is enough.

For delivery or resilience, require green repository-owned CI before automated
delivery. Require owned deploy, artifact identity, health signals, and a proved
recovery action before production fault injection. Stop at the earliest missing
prerequisite.

## Choose and install

Use the project's current tools and substrate. Prefer the existing lint host
for local invariants and use `/custom-linters` for rule design. Include
migration or rollback only when persisted state or release behavior changes.
Route material human choices through `/shape`.

Implement the accepted control. Show one safe representative defect going red,
remove the probe, run the clean path, and exercise the changed developer or
operator interface.

Return the gap, control, checks, observed result, and remaining limitation.
