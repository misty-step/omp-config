# omp-config Agent Guidelines

This repository is the source of truth for the OMP coding harness configuration across Misty Step environments. Changes made here deploy to `~/.omp/agent` via `./install`.

## Skill Provenance Policy

We strictly delineate between externally sourced skills and homebrew skills:

### 1. Externally Sourced Skills
- **Rule: NEVER edit externally sourced skills.**
- External skills (`frontend-design`, `audit-choices`, `herdr`, `ast-grep`, and vendored ecosystem skills) are preserved verbatim as authentic references to other engineering paradigms, vocabularies, and design philosophies.
- Do not compress, rewrite into local dialect, or "futz" with external skills. Their value lies in being unvarnished reference implementations.
- If a project needs custom behavior divergent from an external skill, write a distinct, cleanly named homebrew skill or handle it via configuration. Do not modify the external copy.
- When updating an external skill, re-fetch it directly from the upstream authority without local drift.

### 2. Homebrew Skills
- Misty Step native skills (`custom-linters`, `dispatch`, `evidence-packet`, `exocortex`, `research`, `show-me`, etc.) are actively maintained to Misty Step standards: terse, causal, evidence-first, and zero filler.
- Reject micro-wrappers that merely invoke an existing subagent or alias a one-line command.
- Keep skill boundaries sharp. If two homebrew skills overlap in purpose, consolidate them.

### 3. Harness Iteration Discipline
- We iterate constantly on our harness: evaluating, adding, consolidating, and pruning primitives.
- Before introducing a new skill, check for conceptual overlap with existing tools and skills.
- When deprecating or replacing a skill, perform a clean cutover: migrate callers, update documentation, and delete obsolete directories.

## Workflow & Deployment

1. Always edit configuration, models, themes, and skills inside this repository. Never edit the live deployed files in `~/.omp/agent/` directly.
2. Run `./install` to validate sources, check syntax, merge MCP auth, and deploy changes atomically.
3. Keep commits atomic and conventional (`feat`, `fix`, `refactor`).
