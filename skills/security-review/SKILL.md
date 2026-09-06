---
name: security-review
description: Validate concrete security risk in one bounded target.
disable-model-invocation: true
argument-hint: "[pull request, revision, file, or trust boundary]"
---

# Security review

Review the named target read-only. Do not substitute a generic vulnerability
catalog.

## Bind

Record the exact revision and scope. Name the assets, untrusted inputs,
privileges, trust boundaries, persistence, and exclusions needed to trace an
attacker-controlled path.

## Review

Dispatch one bounded packet to `security-reviewer`. Add an independent pass only
for a named high-risk surface.

A finding needs an attacker-controlled source, a reachable path through current
controls, a dangerous sink or broken invariant, reproducible preconditions, and
concrete impact.

## Validate

Check candidates against current source or a safe reproduction. Reject
unreachable, controlled, speculative, duplicate, and unrelated candidates.

Return confirmed findings, rejected candidates, unavailable checks, residual
risk, and the owner of each accepted remediation. Do not apply repairs.
