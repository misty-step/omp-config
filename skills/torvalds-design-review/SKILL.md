---
name: torvalds-design-review
description: Ask one first-principles critic whether a load-bearing design has the right owner and boundary.
disable-model-invocation: true
argument-hint: "[system, design, or solution]"
---

# Torvalds design review

Use this read-only review for a load-bearing or hard-to-reverse design.

State the problem, workload, current design, binding constraints, accepted
decisions, and primary evidence. Name the target and revision.

Send that packet once to `torvalds-reviewer`. Ask whether the current data
ownership, state transitions, and boundaries solve the stated problem with less
complexity than the credible alternatives.

Check the critic's factual claims against the supplied sources. Return the
verdict, load-bearing strength or flaw, evidence, migration risk, and first
reversible move. Unsupported taste is not a finding.

Done when the operator can accept, reject, or test one concrete design judgment.
