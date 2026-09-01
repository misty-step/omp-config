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
diff, affected code, real-surface proof, and current pull-request comments.

Run the fastest repository-owned deterministic gates first and treat their
output as authoritative. Repair changed-caused failures and restart Bind on the
new head. Return unrelated required-gate failures without spending a model
review. Review only the exact green head.

Done when a reviewer can judge the residual risk without inventing context or
rediscovering deterministic failures.

## Inspect

Review only risk that the green gates cannot decide: accepted intent, domain
behavior, state transitions, ownership boundaries, non-local interactions, and
the concurrency, recovery, security, or operating consequences the change
actually touches.

Send the packet to `reviewer`. Use one bounded review for a routine executable
change. Add a focused independent review only for a material high-risk surface;
use `/security-review` for changed trust boundaries. Treat green deterministic
gates as authoritative for the patterns they own.

Require each finding to name the exact location, trigger, failure mechanism,
violated contract, evidence, and smallest coherent repair. Validate every
finding against the current source. Reject unsupported, pre-existing,
taste-only, and out-of-scope findings. A Blocker must be caused or worsened by
this change and make release unsafe.

A recurring finding whose invariant is decidable from syntax, types, dependency
graphs, configuration, or other local evidence is a control candidate. Report
it once with the invariant, recurrence or consequence evidence, required
analysis, forbidden and permitted examples, and owning repository command. It
is a Blocker only when the current violation itself makes release unsafe.

Done when every finding is confirmed, rejected, or classified as a control
candidate.

## Close

Repair confirmed Blockers. Rerun the deterministic gates and affected real
scenario. If the head changes, review only the repair on the new head.

Record accepted control candidates in the project's trusted work record and
route their separate implementation through `/custom-linters` (or `/foundation`
when the repository lacks a lint host).
Once a control ships, its normal lint command owns the invariant; delete the
corresponding recurring review instruction.

Return the final head, confirmed Blockers, control candidates, non-blocking
findings, rejected findings, checks, proof, and residual risk.

Done when no Blocker or failed required gate remains.
