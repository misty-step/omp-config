---
name: custom-linters
description: "Executable design: turn recurring review insight, domain invariants, and project-specific architecture into precise custom lint rules."
---

# Custom linters

Custom linters are executable design. Each precise rule carries one hard-won
decision forward, gives agents and humans the same immediate feedback, and
frees review for contextual judgment.

## Qualify

Start from an accepted invariant and binding evidence: repeated confirmed
review findings, a costly defect, or a high-consequence design rule. A candidate
must produce the same verdict from repository-local evidence and a diagnostic
that tells the author what to change.

Reject taste, generic best practice, fuzzy semantic judgment, low-precision
heuristics, bugs without a general invariant, and rules an existing check owns.

Done when the invariant, forbidden and permitted examples, evidence, expected
signal, and current lint owner are explicit.

## Choose the host

Use the cheapest analysis that can decide the invariant. Use ast-grep for
syntax-local structure; extend the repository's lint host for scopes, types,
configuration, dependencies, or project graphs. Reuse shared analysis when it
makes later rules faster and more precise.

Keep the rule local and deterministic. Integrate it at the earliest existing
feedback point its cost permits: editor, normal lint, pre-commit, or CI.

Done when the selected host has enough evidence without an LLM, network call,
or parallel lint system.

## Ship

Add forbidden, permitted, and boundary fixtures. Show one safe representative
defect going red, then remove the probe and run the clean path. Emit one sharp
diagnostic and an exact safe fix when possible.

Ship through the normal repository lint command. Migrate current findings, then
enable the rule at error. Keep the design rationale in its authoritative record
and delete the recurring review instruction the rule replaces.

Done when the normal gate rejects the defect, accepts valid variants, runs at
the intended feedback point, and prevents silent regression.
