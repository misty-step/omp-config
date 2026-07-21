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

When changing omp-config itself, read root `global/AGENTS.md` first — it is
the chief-executive contract every OMP session runs under, and this skill
extends it, never overrides it. `bin/check` validates the source tree
(config-contract shape, agent/skill frontmatter, no leaked secrets);
`bin/install` projects the declared `global/` surfaces onto the live agent home
(`$PI_CODING_AGENT_DIR`, default `~/.omp/agent`) and re-verifies the
projection. It keeps runtime-owned cotenants in place. There is no other
build/codegen/sync step.

## Route

| Need | Load |
|---|---|
| create skill or agent | `references/mode-create.md` |
| eval skill | `references/mode-eval.md` |
| lint skill | `references/mode-lint.md` |
| apply skill-design lessons | `references/skill-design-principles.md` |
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
| Ponytail anti-overengineering ladder | `../.external/dietrich-ponytail/SKILL.md` |

Repo-local skills for consumer repos (bespoke QA drivers, deploy runbooks,
persona probes) are written directly into that repo's `.agents/skills/`
with its real routes and commands; this skill owns the craft either way.
Process, provenance header, and eval-stub shape:
`references/repo-local-skill-generation.md` +
`templates/repo-local-skill/`. For a repo's verification skill, interview
the operator first: the manual checks they run after the agent responds and
before merge are the spec — encode each check that has a tool. Turning a
proven session pattern into a first-party primitive starts at the primitive
test below — most patterns are prompts, not skills.

## Contract

- Fix root cause in the highest-leverage layer: type/test/hook/gate/skill/
  AGENTS, in that order.
- Prefer deletion. Harness prose is context tax.
- Use Ponytail before adding or expanding primitives, provider layers,
  harness-specific accelerators, gates, wrappers, or skill prose. The lazy
  viable path has to lose on evidence before a larger harness mechanism earns
  its place.
- Distribution is filesystem + `SKILL.md`/agent-frontmatter, full stop:
  `bin/install` symlinks `global/` onto the live agent home; there is no
  per-harness adapter, projection format, or multi-harness sync step to
  maintain. Skills and agents are OMP-native only.
- Peer-lane model diversity still matters for review and decorrelated
  critique: prefer smoke-tested open-model lanes through Pi, Goose, and
  OpenCode on OpenRouter (`references/open-model-roster.md`); keep Claude,
  Antigravity, Cursor, and Grok conditional unless their specific surface
  answers the task.
- Skills stay self-contained: scripts/libs/references under the skill; state
  roots from invoking repo.
- Code outside a skill serves only omp-config's own repo maintenance
  (`bin/check`, `bin/install`, `bin/config_contract.py`, `provenance.yaml`)
  or harness configuration (`global/config.yml`, `global/mcp.json`,
  `global/models.yml`, `global/extensions`, `global/themes`,
  `global/presets`). It is not a place for skill behavior.
- Treat a skill as a folder, not a markdown file. Use scripts, references,
  examples, templates, assets, evals, or append-only data when prose would
  make the agent reconstruct repeatable work.
- Model/provider/harness selection facts live in the peer-harnesses skill
  (`global/skills/peer-harnesses/references/model-provider-harness-index.md`).
  Keep that file factual: model ids, context, price, latency/smoke evidence,
  tool support, benchmark sources, deprecations, and freshness. Do not encode
  role-fit policy there. The `dispatch` skill owns task-specific composition
  policy.
- omp-config's own skills live in `global/skills/`; repo-local
  `.agents/skills/` in a consumer repo is bespoke, project-specific content,
  not a projection of the global catalog.
- `global/AGENTS.md` is a router, not a manual, installed by symlink at
  `~/.omp/agent/AGENTS.md`. Keep non-obvious facts only.
- OMP discovers task agents by precedence: nearest project `.omp/agents` >
  user `~/.omp/agent/agents` > Claude plugin `agents/` roots (when enabled)
  > bundled (`task`, `scout`, `reviewer`, `librarian`, `designer`, `sonic`).
  Skills follow the analogous native-provider precedence: project/user
  `.omp`/`.agents` skills first, auto-learn managed skills always defer to a
  same-named authored skill. There is no resolved-bundle or catalog-projection
  step beyond that lookup; repo-local vendoring is exceptional and must earn
  its complexity.
- Provider CLIs are tools. Do not wrap them in semantic orchestration unless a
  shaped ticket explicitly asks.
- Harness-specific accelerators (e.g. orchestration-workflow templates) may
  ride inside a skill folder as assets the prose names as optional — a
  harness without the feature must lose nothing by ignoring them. Build one
  only after telemetry shows the pattern recurring; never pre-author.

## Delegation Judgment

Delegate per the Shared Operating Spine (Act).

Local lane guidance: use OMP `task`-tool lanes for doctrine critique, runtime
compatibility, gate design, and regression risk. A missing project-local
`.omp/agents` definition is not a waiver — fall back through the real
discovery precedence (project, then user, then bundled) before assuming a
capability is unavailable.

## Primitive Test

Before creating or growing anything, classify it (2026-06 audit):

- **Local prompt** — "is this just what the operator would retype to a strong
  model?" Keep it in chat, local scratch, or a skill template only when a skill
  truly needs reusable wording. Do not add a repo-level prompt layer. If the
  operator expects OMP slash or `$` discovery, use a skill instead.
- **Skill** — "does this change what a frontier model does, for the better,
  repeatedly?" Judgment + context the model can't derive.
- **Doctrine line** — "worth paying for in every session?" Goes in AGENTS.md,
  not a folder.
- **Mode B** — event-triggered (on PR-ready, on production error, on
  schedule)? It belongs in the event plane (bitterblossom), not this harness.
  This repo is the ad-hoc operator layer plus the shared disk contracts.
  Load `../../shared/references/loop-readiness.md` before proposing any
  unattended loop.

History: slash commands were collapsed into skills when skills arrived, so
saved prompts masqueraded as skills and the catalog tripled. Do not recreate
that. Counter-history: OMP's `/skill:<name>` discovery is skill-shaped, so
high-frequency operator commands that must appear there are skills even when
their body is lightweight.

## Quality Bar

- `SKILL.md` encodes judgment, not a procedure the model already knows.
- Frontmatter descriptions are model trigger classifiers, not human summaries:
  include explicit `Use when:` phrases and `Trigger:` aliases.
- Instruction prose is compression, not literature. Sacrifice grammar before
  clarity; keep terse imperatives, named failure modes, and concrete oracles.
- Put long mode detail in `references/`; keep the entry file short.
- Build gotchas from repeated agent failures. If a gotcha can be asserted by a
  script, hook, or eval, codify it there and point the skill at the artifact.
- Ad-hoc `task`-tool lanes beat static project subagents unless tool
  permissions must be isolated.
- New mechanisms include a verification system: gate, eval, benchmark, QA
  path, smoke path, or probe that can fail for the real error.
- Every run ends clean: no untracked or modified files.

## Post-Change Acceptance

After changing skills, agents, shared doctrine, `global/config.yml`,
`global/mcp.json`, or bootstrap/install logic, prove the output is repo-fit,
not merely structurally valid.

```markdown
## Acceptance Evidence
- Live repo evidence read: source skill/agent, shared doctrine, config, or install output inspected.
- Acceptance source: backlog oracle, skill/agent contract, config-contract, or explicit absence.
- Evidence that proves it: command output, diff, generated artifact, install transcript, or gate output.
- Exact command/path/route exercised: `bin/check`, `bin/install`, smoke path, or route run.
- Oracle / acceptance artifact hash: sha256 digest for any fixture, generated artifact, transcript, or contract used as the oracle, or state that no artifact-backed oracle exists.
- Contract-change acknowledgment: reason when the change alters an acceptance contract, generated source, or assertion surface, or state that no contract changed.
- Repo-fit check: source/projection agree; no stale generated docs, wrong skill root, stale command, or copied bridge remains.
- Structural gate: `bin/check` result, or the specific sub-gate exercised.
- Residual risk: skipped harness, external dependency, or none with reason.
```

## Gotchas

- Phase prose is not judgment. Frontier models know the SDLC; a skill that
  restates implement/refactor/review steps is railroading (Anthropic's own
  top skill lesson: don't state the obvious, avoid railroading). Encode the
  bespoke part — oracles, repo facts, taste — or nothing.
- Process bureaucracy trains checkbox compliance, not quality. Multi-field
  completion gates, oracle hashes, and learning-packet ceremonies get filled
  in plausibly by strong models. Verification is tests, CI, and driving the
  live surface.
- Evals, benchmarks, and QA are verification systems only when they have a
  driver, grader, evidence packet, and cadence. A directory, prompt, or
  transcript with no falsifier is not proof.
- Deterministic scaffold is the historical failure mode here: agents unsure
  of harness engineering fall back to scripts that enforce prose. Every gate
  must answer "what real failure did you catch in the last 90 days?" — no
  answer, delete it.
- Check telemetry before adding or keeping a skill. The 2026-06 audit found
  ~15 of 36 skills unused; usage is a power law. Low usage with high
  value-when-used is fine (say so); low usage with no story is deletion.
- A new frontier model release silently converts some skill prose from
  judgment into railroading: instructions tuned for the last model anchor
  the new one to stale patterns. After a major model ships, re-audit skill
  and doctrine prose; prefer deleting an instruction over updating it.
- Name harness features by capability, not vendor. "Use the harness's
  large-scale orchestration feature when it has one" degrades gracefully
  across harnesses; "use dynamic workflows" confuses every harness that
  lacks them.
- Meta-work ratio: if this repo's commit rate rivals the product repos',
  the flywheel is feeding itself.
- Stale AGENTS prose is worse than missing prose.
- Duplicated repo-local skill copies are usually stale context unless a repo
  needs checked-in vendored harness state.
- `bin/check --installed` drift means the source tree changed but the
  projected symlinks or digests at `~/.omp/agent` did not get re-installed.
- An agent frontmatter missing `model`, `thinkingLevel`, or `tools` is not a
  soft warning — `bin/check` fails the whole gate on it, by design.
- Structural eval trees are not semantic proof; objective graders must assert
  behavior or carry an explicit waiver.
- Helper scripts that are not wired into a gate become optional folklore.
- Regexes over agent prose are usually the wrong boundary.
- If a rule matters, enforce it outside prose.

## Verification

Run `bin/check` (and `bin/check --installed` when the change should reach
`~/.omp/agent`) after changing harness primitives, gates, agents, or install
logic. After running `bin/install`, confirm the installed skills/agents/config
match the source tree and that retired file links are pruned.
