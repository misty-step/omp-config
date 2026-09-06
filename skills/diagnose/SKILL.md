---
name: diagnose
description: Find a root cause with a tight red reproduction; challenge the design after three failed fixes.
disable-model-invocation: true
---

# Diagnose

Turn one failed claim into a repeatable red reproduction. Preserve exact input,
output, state, environment, and revision.

## Isolate

List a few falsifiable hypotheses and test the cheapest discriminating
observation first. Use logs, traces, a debugger, or bisection only to separate
hypotheses. Fix the confirmed source mechanism, then repeat the reproduction
and affected contract scenario.

After three failed fixes, stop patching. Name the data, state, ownership, or
interface that permits the failure and route the redesign through `/shape`.

Return the reproduction, confirmed mechanism, fix and evidence, or the explicit
architectural blocker.
