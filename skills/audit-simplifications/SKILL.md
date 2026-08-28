---
name: audit-simplifications
description: Find material simplifications in a named system scope.
disable-model-invocation: true
argument-hint: "[repo-path, subsystem, or workflow]"
---

# Audit simplifications

This audit is read-only. Search the named scope for complexity the system does
not need.

Prefer findings that delete a requirement, representation, state, owner,
coordination path, or pass-through layer. Use current callers and runtime or
operator behavior where they decide whether the complexity is necessary.

A finding needs exact symbols, current mechanism, evidence, smallest coherent
change, expected deletion, migration risk, and proof. Reject naming, style,
speculative rewrites, and changes that merely move complexity.

Return only material findings, ordered by deleted whole-system work and risk.
State a clean result when none survive validation.

Done when every reported simplification can be evaluated without a whole-repo
coverage ceremony.
