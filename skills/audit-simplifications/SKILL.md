---
name: audit-simplifications
description: Find material simplifications in a named system scope.
disable-model-invocation: true
argument-hint: "[repo-path, subsystem, or workflow]"
---

# Audit simplifications

Review the named scope for complexity the system does not need. Prefer deletion
of a requirement, representation, state, owner, coordination path, or
pass-through layer.

Use current callers and runtime or operator behavior when they decide necessity.
A finding needs exact symbols, current mechanism, evidence, smallest coherent
change, expected deletion, migration risk, and proof. Reject naming, style,
speculative rewrites, and changes that merely move complexity.

Return only material findings, ordered by deleted whole-system work and risk.
Return a clean result when no finding survives the evidence.
