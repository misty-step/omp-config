---
name: custom-linters
description: Turn recurring review insight, domain invariants, and project architecture into precise lint rules.
---

# Custom linters

Encode one accepted invariant as an executable rule. A rule should give agents
and humans the same immediate, actionable feedback.

## Qualify

Start from repeated confirmed findings, a costly defect, or a high-consequence
design rule. Require repository-local evidence, deterministic verdicts,
forbidden and permitted examples, and a diagnostic that tells authors what to
change.

Reject taste, generic best practice, fuzzy judgment, low-precision heuristics,
one-off bugs, and invariants already owned by another check.

## Choose the host

Use the cheapest analysis that can decide the invariant: ast-grep for
syntax-local structure; the existing lint host for scopes, types, configuration,
dependencies, or project graphs. Keep the rule local, deterministic, and free
of LLM or network dependence. Integrate it at the earliest affordable feedback
point.

## Ship

Add boundary fixtures. Show one safe representative defect going red, remove
the probe, and run the clean path. Emit one sharp diagnostic and an exact safe
fix when possible. Enable the rule at error through the normal lint command,
migrate current findings, record rationale in its owning document, and delete
the recurring review instruction it replaces.
