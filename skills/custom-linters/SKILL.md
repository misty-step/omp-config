---
name: custom-linters
description: "Executable design: turn recurring review insight, domain invariants, and project-specific architecture into precise custom lint rules."
---

# Custom linters

Custom linters are executable design. A growing rule set compounds: each rule
carries one hard-won decision forward and frees review for the next one.

Give each rule the evidence it needs. Use ast-grep for syntax-local invariants;
extend the repository's lint host for scope, types, dependencies, or project
graphs. Invest in shared analysis when it makes later rules more powerful and
specific.

Ship through the normal lint command with a sharp diagnostic, forbidden and
permitted examples, and an exact fix when possible. Migrate current findings,
then enable the rule at error.

Done when an accepted design decision becomes immediate feedback and cannot
regress silently.
