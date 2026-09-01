---
name: backlog
description: Summarize a named backlog scope from current evidence.
disable-model-invocation: true
argument-hint: "[project, repository, or board scope]"
---

Use the board's current instructions and read the scope named by the operator.
For Misty Step, run `powder skill`.

Read the affected items and their direct blockers, duplicates, proofs, and
owners. Read the full board only when the operator requests a full snapshot or
the scope cannot otherwise be resolved. Check source, pull requests, decisions,
or the running product only when an item's disposition depends on that claim.

Distinguish current fact, inference, and unresolved operator choice. Age alone
does not make work stale; an implementation claim alone does not make it
delivered.

Return a dated scoped snapshot with:

- the query and evidence limits;
- each relevant item, state, owner, and direct relation;
- contradictions, duplicates, delivered-but-open work, and evidence gaps;
- the highest-leverage unresolved choice.

Done when the requested scope can be checked from the cited item IDs and primary
records without a full portfolio reconstruction.
