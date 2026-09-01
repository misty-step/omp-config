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

For delivery or resilience work, enforce the dependency order: green
repository-owned CI, including its deterministic fast gates, before automated
delivery; repository-owned deploy, artifact identity, health signals, and a
previously proved recovery action relevant to the named invariant before
production fault injection. Stop at the earliest missing prerequisite.

Done when one gap, its consequence, supporting evidence, and current owner are
source-grounded.

## Agree

Propose the smallest control that closes the gap through the project's current
tools, deployment substrate, and interfaces. Change orchestration platforms only
when workload or operating evidence requires it. For a locally decidable
invariant, prefer the existing lint host and use `/custom-linters` to design the
rule. State cost, operator burden, and proof. Include migration or rollback only
when the change affects persisted state or release behavior. Put material human
choices through `/shape`.

Done when the operator accepts one bounded change.

## Install

Implement the accepted control. Show that it fails on one safe representative
defect, then remove the probe and run the clean path. Exercise any changed
developer or operator interface.

Return the gap, control, checks, observed result, and remaining limitation.

Done when the control catches the named defect without adding a parallel
workflow.
