---
name: extract-module
description: Decide whether and how a named subsystem should cross one boundary.
disable-model-invocation: true
argument-hint: "[subsystem and intended boundary]"
---

# Extract module

This work is read-only. Design only the boundary the operator is considering;
do not blueprint later package or repository phases.

Trace the exports, callers, dependencies, shared state, and release paths needed
to judge that boundary. Use `lsp references` for public symbols. Prefer deletion
or an internal reorganization when it removes the same coupling without a new
release path.

If extraction is justified, return the owner, minimal public contract, affected
callers, deleted paths, chosen destination, ordered migration, proof, and
rollback through that destination. Resolve only coupling that crosses the
chosen boundary.

If it is not justified, state the direct alternative and the evidence that
makes extraction unnecessary.

Done when the operator can accept or reject one bounded extraction without
paying for unchosen phases.
