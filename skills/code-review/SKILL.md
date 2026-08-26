---
name: code-review
description: Run an explicit multi-model review of one immutable change and repair release blockers.
disable-model-invocation: true
argument-hint: "[pull request, branch, or commit]"
---

# Code Review

Use this skill for exhaustive review when the change class warrants it. Review
one immutable head. Do not turn every improvement into release scope.

## Bind

Resolve the target and record its base, head SHA, diff, accepted intent,
invariants, non-goals, proof, and affected production surfaces. Use an isolated
checkout. Load `references/review/COUNCIL.md` from `omp config path`.

Done when every lane receives the same immutable review packet.

## Review

Run the council once. Each lane must report its resolved model and either
findings or an explicit clean result. A missing yield, wrong model, stale SHA,
or incomplete packet fails that lane.

Reconcile review comments already present on the pull request before
classification.

Done when every required lane returned against the recorded head.

## Classify

A **Blocker** needs a concrete trigger, failing mechanism, violated accepted
contract, and causal connection to this change. Correctness, security, data
integrity, migration, rollback, and required release-proof failures can block.
A required but absent persisted-state migration is a Blocker.

A **Take** is useful but not required for safe release. Record it as follow-up
work unless the operator accepts it into this change. Style, speculative
flexibility, unmeasured performance, and unrelated debt are Drops.

Done when every finding has evidence, scope, severity, and disposition.

## Repair and close

Repair in-scope Blockers and operator-accepted Takes. Run the narrowest contract
check and real scenario touched by each repair. A new head invalidates prior
receipts; run one fresh targeted review of the repair and reconcile PR comments
again. Do not repeat the council to converge on zero Takes.

Return the final SHA, lane receipts, Blockers repaired, follow-up Takes, Drops,
checks, production proof, and residual risk.

Done when the final head has no open Blocker or failed required check.
