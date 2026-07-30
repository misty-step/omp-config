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

When you change omp-config, read root `global/AGENTS.md` first.
That file defines the chief-executive contract for every OMP session.
This skill extends that contract and never overrides it.
`bin/check` validates the source tree (config-contract shape, agent/skill frontmatter, and no leaked secrets).
`bin/install` projects the declared `global/` surfaces onto the live agent home
(`$PI_CODING_AGENT_DIR`, default `~/.omp/agent`) and re-verifies the
projection.
It keeps runtime-owned cotenants in place.
No other build/codegen/sync step exists.

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
persona probes) go directly into that repo's `.agents/skills/`.
Use the repo's real routes and commands.
This skill owns the craft in both cases.
Keep the process, provenance header, and eval-stub shape in
`references/repo-local-skill-generation.md` and
`templates/repo-local-skill/`.
For a repo verification skill, interview the operator first.
The operator's manual checks after the agent responds and before merge define
the specification.
Encode each check that has a tool.
Use the primitive test below before you turn a proven session pattern into a
first-party primitive.
Most patterns are prompts, not skills.

## Contract

- Fix the root cause in the highest-leverage layer: type, test, hook, gate,
  skill, or `AGENTS`, in that order.
- Prefer deletion. Harness prose creates context tax.
- Use Ponytail before you add or expand primitives, provider layers,
  harness-specific accelerators, gates, wrappers, or skill prose.
  Require evidence that the lazy viable path fails before you add a larger
  harness mechanism.
- Distribution uses filesystem, `SKILL.md`, and agent frontmatter only.
  `bin/install` symlinks `global/` onto the live agent home.
  No per-harness adapter, projection format, or multi-harness sync step needs
  maintenance.
  Skills and agents are OMP-native only.
- Peer-lane model diversity still matters for review and decorrelated
  critique.
  Prefer smoke-tested open-model lanes through Pi, Goose, and OpenCode on
  OpenRouter (`references/open-model-roster.md`).
  Keep Claude, Antigravity, Cursor, and Grok conditional unless their specific
  surface answers the task.
- Skills stay self-contained. Keep scripts, libraries, and references under
  the skill.
  Keep state roots in the invoking repo.
- Code outside a skill serves only omp-config's own repo maintenance
  (`bin/check`, `bin/install`, `bin/config_contract.py`, `provenance.yaml`)
  or harness configuration (`global/config.yml`, `global/mcp.json`,
  `global/models.yml`, `global/extensions`, `global/themes`,
  `global/presets`).
  Do not put skill behavior there.
- Treat a skill as a folder, not a Markdown file.
  Use scripts, references, examples, templates, assets, evals, or append-only
  data when prose would make the agent reconstruct repeatable work.
- Keep model, provider, and harness selection facts in the peer-harnesses
  skill (`global/skills/peer-harnesses/references/model-provider-harness-index.md`).
  Keep that file factual: model ids, context, price, latency/smoke evidence,
  tool support, benchmark sources, deprecations, and freshness.
  Do not put role-fit policy there.
  The `dispatch` skill owns task-specific composition policy.
- omp-config's own skills live in `global/skills/`.
  A consumer repo's `.agents/skills/` is bespoke project content, not a
  projection of the global catalog.
- `global/skills/dispatch/SKILL.md` is the routing authority; `global/AGENTS.md`
  is the chief contract.
  `bin/install` installs the chief contract by symlink at `~/.omp/agent/AGENTS.md`.
- OMP discovers task agents by precedence:
  nearest project `.omp/agents` > user `~/.omp/agent/agents` >
  Claude plugin `agents/` roots (when enabled) > bundled (`task`, `scout`,
  `librarian`, `designer`, `sonic`).
  Skills follow the analogous native-provider precedence:
  project/user `.omp`/`.agents` skills first.
  Auto-learn managed skills always defer to a same-named authored skill.
  No resolved-bundle or catalog-projection step exists beyond that lookup.
  Repo-local vendoring is exceptional and must earn its complexity.
- Provider CLIs are tools.
  Do not wrap them in semantic orchestration unless a shaped ticket asks.
- Harness-specific accelerators (for example, orchestration-workflow templates)
  may live inside a skill folder as optional assets.
  A harness without the feature must lose nothing by ignoring them.
  Build one only after telemetry shows the pattern recurring.
  Never pre-author one.

## Delegation Judgment

Delegate according to the Shared Operating Spine (Act).

Local lane guidance: use OMP `task`-tool lanes for doctrine critique, runtime
compatibility, gate design, and regression risk.
A missing project-local `.omp/agents` definition is not a waiver.
Use the real discovery precedence (project, then user, then bundled) before you
assume a capability is unavailable.

## Primitive Test

Before you create or grow anything, classify it (2026-06 audit):

- **Local prompt** — Ask, "Is this only what the operator would retype for a
  strong model?"
  Keep it in chat, local scratch, or a skill template only when a skill truly
  needs reusable wording.
  Do not add a repo-level prompt layer.
  If the operator expects OMP slash or `$` discovery, use a skill instead.
- **Skill** — Ask, "Does this change what a frontier model does, for the better,
  repeatedly?"
  Encode judgment and context that the model cannot derive.
- **Doctrine line** — Ask, "Is this worth paying for in every session?"
  Put it in `AGENTS.md`, not a folder.
- **Mode B** — Ask, "Is this event-triggered (on PR-ready, on production
  error, or on schedule)?" Mode B is currently unavailable. Keep this work in
  Mode A and do not invent a replacement workflow service.
  This repo is the ad-hoc operator layer plus the shared disk contracts.
  Load `../../shared/references/loop-readiness.md` before proposing a future
  unattended loop.

History: slash commands moved into skills when skills arrived.
Saved prompts then masqueraded as skills, and the catalog tripled.
Do not recreate that pattern.
Counter-history: OMP's `/skill:<name>` discovery is skill-shaped.
High-frequency operator commands that must appear there are skills, even when
their body is lightweight.

## Quality Bar

- `SKILL.md` encodes judgment, not a procedure the model already knows.
- Frontmatter descriptions are model trigger classifiers, not human summaries.
  Include explicit `Use when:` phrases and `Trigger:` aliases.
- Instruction prose is compression, not literature.
  Sacrifice grammar before clarity.
  Keep terse imperatives, named failure modes, and concrete oracles.
- Put long mode detail in `references/`.
  Keep the entry file short.
- Build gotchas from repeated agent failures.
  If a script, hook, or eval can assert a gotcha, codify it there and point the
  skill at that artifact.
- Ad-hoc `task`-tool lanes beat static project subagents unless tool
  permissions need isolation.
- New mechanisms need a verification system:
  gate, eval, benchmark, QA path, smoke path, or probe that can fail for the
  real error.
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

- Phase prose is not judgment.
  Frontier models know the SDLC.
  A skill that repeats implement, refactor, and review steps adds railroading.
  Encode the bespoke part: oracles, repo facts, and taste.
  Otherwise, delete it.
- Process bureaucracy trains checkbox compliance, not quality.
  Strong models fill multi-field completion gates, oracle hashes, and
  learning-packet ceremonies with plausible content.
  Use tests, CI, and the live surface for verification.
- Evals, benchmarks, and QA verify behavior only when they have a driver,
  grader, evidence packet, and cadence.
  A directory, prompt, or transcript without a falsifier is not proof.
- Deterministic scaffold is the historical failure mode here.
  Agents unsure about harness engineering fall back to scripts that enforce
  prose.
  Ask every gate, "What real failure did you catch in the last 90 days?"
  If no answer exists, delete the gate.
- Check telemetry before you add or keep a skill.
  The 2026-06 audit found ~15 of 36 skills unused.
  Usage is a power law.
  Low usage with high value-when-used is fine when you state the reason.
  Low usage without a reason calls for deletion.
- A new frontier model release can silently turn some skill prose from judgment
  into railroading.
  After a major model ships, re-audit skill and doctrine prose.
  Prefer deleting an instruction over updating it.
- Name harness features by capability, not vendor.
  "Use the harness's large-scale orchestration feature when it has one" works
  across harnesses.
  "Use dynamic workflows" confuses harnesses that lack them.
- Meta-work ratio: if this repo's commit rate rivals the product repos',
  the flywheel feeds itself.
- Stale AGENTS prose is worse than missing prose.
- Duplicated repo-local skill copies are usually stale context unless a repo
  needs checked-in vendored harness state.
- `bin/check --installed` drift means the source tree changed but the
  projected symlinks or digests at `~/.omp/agent` were not re-installed.
- An agent frontmatter entry missing `model`, `thinkingLevel`, or `tools` is
  not a soft warning.
  `bin/check` fails the whole gate on it by design.
- Structural eval trees are not semantic proof.
  Objective graders must assert behavior or carry an explicit waiver.
- Helper scripts that are not wired into a gate become optional folklore.
- Regexes over agent prose are usually the wrong boundary.
- Enforce important rules outside prose.

## Verification

Run `bin/check` after you change harness primitives, gates, skills, agents, or
shared doctrine.
Run it after you change `global/config.yml`, `global/mcp.json`, or
bootstrap/install logic.
Run `bin/check --installed` when the change should reach `~/.omp/agent`.
After `bin/install`, confirm that installed skills, agents, and config match the
source tree.
Confirm that retired file links are pruned.
