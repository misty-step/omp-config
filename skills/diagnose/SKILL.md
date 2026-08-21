---
name: diagnose
description: Find the root cause with a tight red loop. After three failed fixes, question the architecture.
disable-model-invocation: true
---

# Diagnose

Do not theorize without a red reproduction. Do not patch a third time
without questioning the design.

## 1. Reproduce

State the failing claim in one sentence. Produce the tightest command,
session, or interaction that makes it fail now. Minimize input and surface
until one behavior is red.

If you catch yourself reading code to build a theory before this
reproduction exists, stop.

Completion criterion: A named command or scenario is red on this machine.

## 2. Hypothesize

Write three to five falsifiable hypotheses. Each names a mechanism and the
observation that would kill it. Instrument or bisect only to distinguish
them. Do not "look around."

Completion criterion: Every hypothesis is confirmed or killed by an
observation, or the next measurement is named.

## 3. Fix once

Fix the confirmed mechanism at the source. Watch the reproduction go green.
Add a regression only when the contract is not already defended on that
boundary.

Do not keep the first-draft production code as "reference" if it was written
before the reproduction existed. Delete it and apply the fix that the red
loop earned.

Completion criterion: The original reproduction is green. No other
hypothesis remains live without a reason.

## 4. Three-fix stop

If three attempted fixes have failed, stop patching. The representation is
the bug.

Name the data, state, or ownership that permits the failure. Route the
redesign through `explore-unknowns`. Use `audit-simplifications` when the
question is whole-repo representation, not this incident.

Completion criterion: Either a fix from step 3 holds, or patching has
stopped and the architecture question is in front of the operator.
