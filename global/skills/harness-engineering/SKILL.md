---
disable-model-invocation: true
name: harness-engineering
description: |
  Engineer OMP harness primitives in omp-config: skills, agents, models, MCP,
  install/check. Use for harness work, skill health, create/eval/lint skills,
  bootstrap drift. Trigger: /harness-engineering, /harness, /skill.
argument-hint: "[create|eval|lint|convert|engineer|audit|models] [target]"
---

# /harness-engineering

Engineer the harness. Keep it thin.
This skill is for **omp-config work**, not product feature delivery.

## Lifecycle

1. Read `global/AGENTS.md` (chief contract). This skill never overrides it.
2. Change source under `global/` and `bin/`.
3. Run `bin/check`. Run `bin/check --installed` when projection must change.
4. Run `bin/install` to project onto `$PI_CODING_AGENT_DIR` (default `~/.omp/agent`).
5. No other build or multi-harness sync step exists.

## Modes

| Need | Load |
|---|---|
| create skill or agent | `references/mode-create.md` |
| eval skill | `references/mode-eval.md` + `skill://skill-eval` |
| lint skill | `references/mode-lint.md` |
| skill-authoring standard | `global/references/skill-authoring-standard.md` |
| catalog audit / delete candidates | `references/mode-audit.md` |
| convert agent/skill | `references/mode-convert.md` |
| doctrine, gates, hooks | `references/mode-engineer.md` |
| open-model defaults | `references/open-model-roster.md` |
| stack defaults | `references/preferred-stack.md` |
| model/provider facts | `/home/phaedrus/.omp/agent/skills/harness-engineering/references/model-provider-harness-index.md` |
| every-project floor | `skill://foundation` |
| route work to agents | `skill://dispatch` |
| repo-local skill scaffold | `references/repo-local-skill-generation.md` + `templates/repo-local-skill/` |

## Hard rules

- Prefer deletion. Require evidence the lazy path fails before adding mechanism.
- Distribute through filesystem, `SKILL.md`, and agent frontmatter only.
- Keep skills OMP-native. No adapter or multi-harness projection layer.
- Put product QA/deploy skills in the product repo `.agents/skills/`, not here.
- Encode judgment, not generic procedure. Wire scripts into gates.
- New multi-agent process changes need `global/references/process-adversarial-testing.md`.

## Primitive test

- **Local prompt** if retyping works.
- **Skill** if slash discovery or repeated judgment needs a folder.
- **Doctrine line** in `AGENTS.md` if every session must pay the cost.
- **Mode B** unavailable — keep unattended loops out until a product owns them.

## Completion

- `bin/check` green on the change.
- Projection matches source after install when install is required.
- Retired skills and links are gone.
- Name residual risk.
