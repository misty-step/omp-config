# Delete-First Lens

Load this when: choosing a build path, or before adding automation,
optimization, abstractions, dependencies, wrappers, or surface — not after.

Use while shaping, refactoring, or automating. The order matters.

1. **Question the requirement.** What user outcome disappears if this is not
   built? Who owns the requirement?
2. **Delete.** Can the feature, file, process step, dependency, mode, or
   abstraction be removed entirely?
3. **Simplify.** Can stdlib, native platform behavior, existing repo code, or a
   manual step cover the need?
4. **Speed up.** Optimize only after the thing survives deletion and
   simplification.
5. **Automate.** Automate only repeated, verified, bounded work.

## Boundaries

Do not delete explicit user requirements, trust-boundary validation, data-loss
prevention, security measures, accessibility basics, or acceptance evidence.

## Prompt

Before adding or automating, answer in three lines:

- Requirement questioned:
- Deleted or simplified:
- Only then optimized/automated because:

If the third line is doing all the work, the design is probably backwards.

## Erasure (during and after the work)

Delete-first governs what you build; erasure governs what you leave behind.
Anything that only ever grows — code, comments, docs, rules, memory — is
rotting.

- Standing hunt: while working, even mid-task, remove duplicated concepts,
  dead code, and tangled logic you pass. Your own confusion marks the spot —
  what surprised you or was hard to follow is a bad abstraction; untangle it
  now, not in a follow-up.
- Swap rule: replacing X with Y includes deleting X — implementation, tests,
  docs, config. Compatibility remnants survive only on explicit request.
- Same-diff hygiene: a refactor deletes or rewrites the comments it staled; a
  completed TODO leaves with the fix; a decommissioned surface takes its
  article and inbound links with it.
- Closeout: what did this change make obsolete, and did I delete it?
