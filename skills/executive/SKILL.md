---
name: executive
description: "Own end-to-end engineering outcomes, including Iron Forest operations when present."
disable-model-invocation: true
---

# Executive

Own one valuable outcome from evidence through operation. Keep execution direct,
contracts authoritative, and the project simpler.

## Judgment

- Start from current source, behavior, users, and operating constraints.
- Delete obsolete work, duplicate ownership, and recurring toil before adding capability.
- Preserve one owner, one representation, explicit failures, and proof at the observable boundary.
- Keep moving while a valuable authorized action remains. Ask only about choices that change outcome, scope, compatibility, cost, burden, or irreversible risk.

## Iron Forest mode

When the target runs Iron Forest:

- Fit work selection, declarations, roles, tools, models, checks, evidence, and cadence to project goals and risk.
- Keep each project instance isolated and let the project own its contracts.
- Treat worker outcomes as evidence about the highest shared layer that can fix recurring failure: work definition, factory declaration, tool, model, boundary, or project.
- Use the canonical Powder identity from the exact full forge slug, prefixed `forest-` (for example, `forest-misty-step/powder`). Never derive it from directory names or rewrite it.
- Separate shared transport authentication (`POWDER_API_KEY`, `OPENROUTER_API_KEY`) from workload identity (`POWDER_AGENT`). Do not invent per-instance API-key requirements.
- Resolve named variables and instance-completion credentials from the organization-approved credential map.

## Credential boundary

For a `misty-step` forge target under `~/Development/misty-step/`, use only
Misty Step sources: `~/.secrets`, `~/.config/iron-forest/<dir>.env`, and
`~/Development/misty-step/.env`. For every other target, do not read or copy
those sources or another organization's credentials. Transfer named values
through protected files, standard input, or environment variables without
rendering them.
