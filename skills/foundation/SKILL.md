---
name: foundation
description: Inspect a project, agree on its engineering baseline, and install the next useful controls.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Foundation

A foundation is a small set of controls that makes invalid changes fail early
and names the repair. It is not a standard stack or a reason to rewrite working
systems.

Read `CONTROLS.md` when classifying controls.

## Inspect

Map the product, users, current architecture, domain owners, languages, run
paths, tests, CI, release, operations, documentation, and agent context. Read
existing interfaces before proposing new ones. Verify consequential runtime
claims.

Classify each applicable control as present, equivalent, missing, or an accepted
deviation. Treat persisted representation changes as high risk.

Done when the current baseline and its real gaps are source-grounded.

## Recommend

Propose one coherent package:

- tight local and CI checks for the existing stack;
- one cheap end-to-end result-path smoke before any expensive eval or matrix;
- one deterministic start path and representative fixture;
- one real-interface smoke path;
- protected exact-head merge checks where the repository supports them;
- deploy identity, production verification, and rollback for operated software;
- the smallest product-shaped outcome that proves the baseline.

Prefer current tools and direct interfaces. Delete obsolete setup. State cost,
migration, operator burden, risks, and rejected alternatives. Put material
human choices through `/shape`.

Done when the operator can accept or reject one bounded package.

## Lock and execute

Record the accepted outcome, baseline scope, product scope, invariants,
deletions, proof, and rollback. Implement in small slices. Prove each new
control goes red on a safe synthetic defect, then run the clean path. Exercise
the changed real interface and inspect evidence.

Remove probes and temporary scaffolding. Return implemented controls, retained
equivalents, deviations, checks, real-surface proof, and remaining gaps.

Done when the accepted baseline works from a clean checkout and the next useful
outcome works on its real interface.
