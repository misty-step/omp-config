---
name: code-review
description: Review one immutable change for concrete release risk.
disable-model-invocation: true
argument-hint: "[pull request, branch, or commit]"
---

# Code review

Review one exact head. Keep redesign, taste, and unrelated cleanup out of scope.

## Bind

Resolve base and head. Collect accepted intent, invariants, non-goals, diff,
affected code, real-surface proof, and current pull-request comments. Run the
fastest repository-owned deterministic gates first. Repair changed-caused
failures and restart on the new head; report unrelated gate failures without
model review.

## Inspect

Review only residual risk the green gates cannot decide: intent, domain behavior,
state transitions, ownership boundaries, non-local effects, and touched
concurrency, recovery, security, or operating consequences.

Dispatch one bounded review to `reviewer`; add an independent pass only for a
material high-risk surface. Use `/security-review` for changed trust boundaries.
Each finding needs exact location, trigger, mechanism, violated contract,
evidence, and smallest repair. Reject unsupported, pre-existing, taste-only,
and out-of-scope findings. A blocker must be caused or worsened by this change
and make release unsafe.

Classify a recurring invariant decidable from syntax, types, dependency graphs,
configuration, or local evidence as a control candidate. Report recurrence,
required analysis, forbidden and permitted examples, and the owning command.
It is a blocker only when the current violation makes release unsafe.

## Close

Repair confirmed blockers, rerun affected gates and the real scenario, and
review only the repair on a changed head. Record control candidates for
`/custom-linters` or `/foundation`; delete the recurring review instruction
after the control ships.

Return final head, blockers, control candidates, non-blocking and rejected
findings, checks, proof, and residual risk.
