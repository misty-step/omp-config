---
name: diagnose
description: Find a root cause with a tight red reproduction; challenge the design after three failed fixes.
disable-model-invocation: true
---

# Diagnose

A theory without a red reproduction is a guess. A third patch on the same
failure is usually a design warning.

## Make it red

State the failed claim. Produce the smallest current command or interaction that
shows it. Preserve exact input, output, state, environment, and revision.

Done when one repeatable observation separates failure from success.

## Isolate the mechanism

List a few falsifiable hypotheses. Test the cheapest discriminating observation
first. Use logs, traces, a debugger, or bisection only to separate hypotheses.
Fix the confirmed source mechanism, then run the same reproduction and adjacent
contract checks.

Done when the reproduction is green for the identified reason.

## Stop at three

After three failed fixes, stop patching. Name the data, state, ownership, or
interface that permits the failure. Put the redesign through `/shape`.

Done when the incident is fixed and defended, or the architectural blocker is
explicit.
