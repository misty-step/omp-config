---
disable-model-invocation: true
name: harness-engineering
description: |
  Engineer OMP harness primitives: skills, agents, models, MCP config in the
  omp-config repo. Use for "improve the harness", "harness engineering",
  "bootstrap is wrong", "AGENTS.md is stale", "skill health", "undertriggering
  skill", "description tax", "eval skill", "stack/infrastructure defaults",
  "generate repo-local skill", "domain agent skill". Trigger: /harness-engineering,
  /harness, /skill.
argument-hint: "[create|eval|lint|convert|engineer|audit|models] [target]"
---

# /harness-engineering

Engineer the harness. Keep it thin.

## Lifecycle

Read `global/AGENTS.md` before changing omp-config. It defines the chief
contract; this skill extends it and never overrides it. `bin/check` validates
config-contract shape, agent and skill frontmatter, and secret absence.
`bin/install` projects `global/` onto `$PI_CODING_AGENT_DIR` (default
`~/.omp/agent`), re-verifies the projection, and preserves runtime cotenants.
No other build, code-generation, or synchronization step exists.

## Mode Routing

| Need | Load |
|---|---|
| create skill or agent | `references/mode-create.md` |
| eval skill | `references/mode-eval.md` |
| lint skill | `references/mode-lint.md` |
| apply skill-authoring standard | `global/references/skill-authoring-standard.md` |
| clean skill catalog | `references/mode-audit.md` |
| convert agent/skill | `references/mode-convert.md` |
| engineer doctrine/gates/hooks | `references/mode-engineer.md` |
| measure skill usage/health/staleness | `references/mode-audit.md` |
| current model/provider/harness facts | `global/skills/peer-harnesses/references/model-provider-harness-index.md` |
| task-specific model, agent, and primitive routing | `../dispatch/SKILL.md` |
| open-model defaults | `references/open-model-roster.md` |
| preferred stack / infrastructure defaults | `references/preferred-stack.md` |
| adopt or audit a repo engineering fitness function | `../project-engineering/SKILL.md` |
| factory app capability routing | `../factory-apps/SKILL.md` |
| generate a focused repo-local skill for a domain agent | `references/repo-local-skill-generation.md` + `templates/repo-local-skill/` |
| public-surface "works" critique | `../../shared/references/works-critique.md` |
| model-native product boundary | `../../shared/references/model-native-product-primitives.md` |
| loop readiness / Mode B handoff | `../../shared/references/loop-readiness.md` |
| verification system first | `../../shared/references/verification-system-first.md` |
| delete-first simplification lens | `../../shared/references/delete-first.md` |
| Ponytail anti-overengineering ladder | `../../external/dietrich-ponytail/SKILL.md` |

Put consumer-repo QA, deploy, and persona skills in that repo's
`.agents/skills/`; use its real routes and commands. Keep provenance and eval
shape in `references/repo-local-skill-generation.md` and
`templates/repo-local-skill/`. For verification skills, interview the operator;
manual pre-merge checks define the specification. Encode checks that have tools.
Run the primitive test before promoting a pattern. Most patterns are prompts.

## Harness Contract

- Prefer deletion. Use Ponytail before adding mechanisms. Require evidence that
  the lazy path fails before adding a larger mechanism.
- Distribute through filesystem, `SKILL.md`, and agent frontmatter only.
  `bin/install` symlinks `global/`; maintain no adapter, projection format, or
  multi-harness sync. Keep skills and agents OMP-native.
- Keep skill scripts, libraries, and references in the skill. Keep state roots in
  the invoking repo. Keep model and provider facts in the peer-harnesses index.
- Put outside-skill code only in omp-config maintenance (`bin/check`,
  `bin/install`, `bin/config_contract.py`, `provenance.yaml`) or harness config
  (`global/config.yml`, `global/mcp.json`, `global/models.yml`,
  `global/extensions`, `global/themes`, `global/presets`).
- Treat each skill as a folder. Use scripts, references, examples, templates,
  assets, evals, or append-only data for repeatable work.
- Keep omp-config skills in `global/skills/`; consumer `.agents/skills/` remain
  bespoke. Keep dispatch as routing authority and `global/AGENTS.md` as chief
  contract. `bin/install` symlinks that contract to `~/.omp/agent/AGENTS.md`.
- Keep accelerators optional. Add them only after recurring telemetry; never
  pre-author them.

## Catalog Rules

Discover authored agents in this order: project `.omp/agents`, user
`~/.omp/agent/agents`, then the current OMP declarations in `global/agents/`:
`architect`, `builder`, `designer`, `qa-user`, `qa-user-leaf`, `researcher`,
and `verifier`. The Claude-plugin provider is disabled, and the bundled names
`task`, `scout`, `librarian`, `sonic`, `reviewer`, and `security-reviewer` are
disabled by `task.disabledAgents`; do not route work to them. Discover skills
through analogous native-provider precedence: project and user `.omp` or
`.agents` first. Auto-learn skills defer to same-named authored skills. No
resolved bundle or catalog projection exists beyond lookup. Repo-local
vendoring is exceptional.

## Primitive Test

Classify every proposed mechanism:

- **Local prompt:** Keep operator retyping in chat, scratch, or a reusable
  template. Do not add a repo prompt layer. Use a skill for OMP slash or `$`
  discovery.
- **Skill:** Encode judgment or context that repeatedly improves frontier-model
  behavior and cannot be derived.
- **Doctrine line:** Put a rule in `AGENTS.md` when every session must pay its
  cost; do not put it in a folder.
- **Mode B:** Treat PR-ready, production-error, and scheduled work as unavailable
  Mode B. Keep work in Mode A and load `../../shared/references/loop-readiness.md`
  before proposing an unattended loop.

Slash commands moved into skills, then saved prompts masqueraded as skills. Do
not recreate that catalog growth. Frequent `/skill:<name>` commands remain
skills even when their bodies are small.

## Quality and Gates

Encode judgment, not generic procedure. Use descriptions as trigger classifiers
with `Use when:` and `Trigger:` phrases. Keep terse imperatives, failure modes,
and concrete oracles. Put long mode detail in `references/`. Wire scripts,
hooks, and evals into gates. Require each new mechanism to have a gate, eval,
benchmark, QA path, smoke path, or falsifiable probe.

After changes, record live evidence and the acceptance source. Record proof and
the exact command or route. Record an artifact sha256 or a no-artifact statement.
Record the contract-change reason or none. Confirm source and projection agree.
Record the structural gate and residual risk. Use
`../../shared/references/verification-system-first.md` for shared proof.

## Gotchas

- Evals need a driver, grader, evidence packet, and cadence. Without a falsifier,
  a prompt, directory, or transcript is not proof.
- Ask each gate what failure it caught in 90 days. Delete gates with no answer.
- The 2026-06 audit found about 15 of 36 skills unused. Explain low usage with
  high value; delete low usage without demonstrated value.
- Re-audit after major model releases. Name features by capability, not vendor.
- Stale `AGENTS` prose is worse than missing prose. Duplicate local copies are
  usually stale unless vendored state is required.
- `bin/check --installed` drift means source changed without re-installation.
  Missing agent `model`, `thinkingLevel`, or `tools` frontmatter fails the gate.
- Structural eval trees are not semantic proof. Unwired scripts are folklore.
  Regexes over agent prose use the wrong boundary. Enforce important rules
  outside prose.

## Harness Checks

Run `bin/check` after skill, agent, gate, doctrine, config, MCP, or
bootstrap/install changes. Run `bin/check --installed` when projection must
change. After `bin/install`, compare installed skills, agents, and config with
source and confirm retired links are pruned.
