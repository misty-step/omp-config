---
name: security-review
description: Validate concrete security risk in one bounded target.
disable-model-invocation: true
argument-hint: "[pull request, revision, file, or trust boundary]"
---

# Security review

This review is read-only. Review the named target, not a generic vulnerability
catalog.

## Bound

Record the exact revision and scope. Name the assets, untrusted inputs,
privileges, trust boundaries, persistence, and exclusions that matter to this
target.

Done when the reviewer can trace an attacker-controlled path without inventing
system context.

## Review

Send the packet to `security-reviewer`. Add another independent pass only when a
named high-risk surface warrants it.

A finding needs an attacker-controlled source, a reachable path through current
controls, a dangerous sink or broken invariant, reproducible preconditions, and
concrete impact.

Done when each candidate has a complete mechanism or is rejected.

## Deliver

Validate candidates against current source or a safe reproduction. Reject
unreachable, controlled, speculative, duplicate, and unrelated findings.

Return confirmed findings, rejected candidates, unavailable checks, residual
risk, and the owner of each accepted remediation. Do not apply repairs.

Done when every reported finding is actionable without another security survey.
