---
name: backlog
description: Summarize a named backlog scope from current evidence.
disable-model-invocation: true
argument-hint: "[project, repository, or board scope]"
---

Use the board's current instructions and read only the named scope. For Misty
Step, run `powder skill`.

Read affected items and their direct blockers, duplicates, proofs, and owners.
Read the full board only for a requested snapshot or when the scope cannot be
resolved otherwise. Check source, pull requests, decisions, or the running
product only when an item's disposition depends on that claim.

Separate current fact, inference, and unresolved operator choice. Age alone does
not make work stale; an implementation claim alone does not make it delivered.

Return a dated snapshot with the query and evidence limits, relevant item IDs,
state, owner, direct relations, contradictions, duplicates, delivered-but-open
work, evidence gaps, and the highest-leverage unresolved choice.
