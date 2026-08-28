---
name: code-review
description: Review one immutable change for concrete release risk.
disable-model-invocation: true
argument-hint: "[pull request, branch, or commit]"
---

# Code review

Review one exact head. Keep redesign, taste, and unrelated cleanup out of scope.

## Bind

Resolve the base and head. Collect the accepted intent, invariants, non-goals,
diff, affected code, checks, real-surface proof, and current pull-request
comments.

Done when a reviewer can judge the change without inventing context.

## Inspect

Send the packet to `reviewer`. Use one bounded review for a routine executable
change. Add a focused independent review only for a material high-risk surface;
use `/security-review` for changed trust boundaries.

Require each finding to name the exact location, trigger, failure mechanism,
violated contract, evidence, and smallest coherent repair. Validate every
finding against the current source. Reject unsupported, pre-existing,
taste-only, and out-of-scope findings. A Blocker must be caused or worsened by
this change and make release unsafe.

Done when every finding is confirmed or rejected.

## Close

Repair confirmed Blockers. Rerun each affected check and real scenario. If the
head changes, review only the repair on the new head.

Return the final head, confirmed Blockers, non-blocking findings, rejected
findings, checks, proof, and residual risk.

Done when no Blocker or failed required check remains.
