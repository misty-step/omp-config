---
name: foundation
description: Inspect a project, agree on one engineering gap, and install the smallest useful control.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Foundation

Strengthen the existing project. Do not apply a standard stack or control
checklist.

## Inspect

Read the current build, test, run, CI, release, operating, and review paths.
Identify the smallest observed gap that makes change unsafe or unnecessarily
difficult. Repeated human or agent comments about the same locally decidable
violation are evidence of a missing executable control. Treat an existing
equivalent control as sufficient.

Done when one gap, its consequence, supporting evidence, and current owner are
source-grounded.

## Agree

Propose the smallest control that closes the gap through the project's current
tools and interfaces. For a locally decidable invariant, prefer the existing
lint host and use `/custom-linters` to design the rule. State its cost, operator
burden, and proof. Include migration or rollback only when the change affects
persisted state or release behavior. Put material human choices through
`/shape`.

Done when the operator accepts one bounded change.

## Install

Implement the accepted control. Show that it fails on one safe representative
defect, then remove the probe and run the clean path. Exercise any changed
developer or operator interface.

Return the gap, control, checks, observed result, and remaining limitation.

Done when the control catches the named defect without adding a parallel
workflow.
