# /harness-engineering create

Create a new omp-config source skill or agent from scratch.

For a project-local skill in a consumer repo (bespoke QA drivers, persona
probes), write it directly into the repo's `.agents/skills/<name>/`.
Use the repo's real routes and commands.
This mode creates first-party catalog primitives under `global/skills/`.

## The description field is everything

The description determines when the model loads the skill.
Write it assertively.
Include trigger phrases that users actually say.
If the skill does not fire, the description is wrong, not the model.

**Good:** `"Use when: 'debug this', 'why is this broken', 'investigate', 'production down'"`
**Bad:** `"A debugging utility for code analysis"`

## Structure

```
skill-name/
├── SKILL.md          # < 500 lines. Core routing + judgment.
├── references/       # Deep context loaded on demand.
├── scripts/          # Executable code for deterministic tasks.
├── examples/         # Representative inputs/outputs when useful.
├── templates/        # Copyable artifacts the model should not recreate.
├── assets/           # Images, fixtures, schemas, or static resources.
└── evals/            # Optional eval cases/graders for load-bearing skills.
```

Do not create empty folders. Add the folder when the skill has real reusable
material for that layer. If the workflow benefits from memory, define an
append-only JSONL/schema path and privacy rule; otherwise leave it stateless.

## What to encode

Encode judgment the model lacks, not procedures it already knows.

**Highest signal:** Gotchas show what goes wrong, not only what goes right.
A gotcha list has more value than pages of happy-path instructions.
List failure modes and common mistakes that the model consistently gets wrong
without the skill.

**Avoid:** Step-by-step procedures that the model can derive from context.
If you write "1. Read the file 2. Find the function 3. Edit it," you wrote a
task description, not a skill.

**In-repo exemplars worth reading before drafting:**
- `global/skills/sprites/SKILL.md` — one primitive, a routing table, gotchas.
  No daemon, no ceremony.
- `global/skills/dispatch/SKILL.md` — visible chief router with a falsifiable
  composition contract.

**External exemplars:**
- `skill-creator` (upstream `anthropics/skills`, not vendored) — the "theory
  of mind" framing.
  Explain the *why* before the *how*.
  This helps the model handle edge cases that the rules do not enumerate.
- `claude-api` (upstream `anthropics/skills`, not vendored) — stratified
  progressive disclosure.
  Use the SKILL.md body, then language-specific reference folders, then code
  examples.
- `vercel-dogfood` (installed under `global/external/`) — repro-first
  discipline.
  Document immediately before moving on.
  This lets findings survive session handoff.

## Progressive disclosure

Use three layers.
Load each layer only when needed:

1. **Description** (~100 tokens) — always in context. It decides triggering.
2. **SKILL.md body** (< 500 lines) — loads when the skill fires.
3. **References/scripts/assets/templates/examples** — load or run on demand
   when the specific situation requires them.

Keep `SKILL.md` focused on what to do and what goes wrong.
Move deep reference material, examples, boilerplate, schemas, and repeatable
mechanics into the skill folder.

## Brevity doctrine

Model instructions are not essays.

- Prefer fragments over paragraphs when the meaning survives.
- Use imperative verbs: "Probe the repo", "Write receipt", "Run gate".
- Name the failure mode directly.
- Delete throat-clearing: "it is important to", "you should consider".
- Keep examples shorter than the rule they explain.
- Put citations, long rationale, and variant-specific detail in references.

Useful source patterns:

- JuliusBrussee/caveman: token compression and terse agent dialect.
  https://github.com/JuliusBrussee/caveman
- petekp/claude-code-setup `grill-me`: a tiny, standalone interrogation skill
  that forces one question at a time with a recommended answer.
- upstream `thermos/skills` maintainability review leaf: harsh review focused
  on structural simplification, file-size pressure, and spaghetti-growth
  blockers.
- Anthropic skill authoring: description selection and progressive disclosure.
  https://anthropic.mintlify.app/en/docs/agents-and-tools/agent-skills/best-practices
- Vercel Agent Skills: concise `SKILL.md`, reusable versioned context, and
  avoiding duplicated reference content.
  https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context

## Frontmatter fields that matter

```yaml
---
name: my-skill
description: |
  What it does. When to use it. Trigger phrases.
argument-hint: "[arg1] [arg2]"      # shown in autocomplete; unknown keys are preserved as metadata
globs: ["src/**/*.ts"]              # optional: auto-apply scope (rule-file style)
alwaysApply: false                  # optional: force-load without model selection
disable-model-invocation: true      # optional: user-only invocation (hand-only skill)
hide: true                          # optional: loaded and reachable via skill://, omitted from the model-facing list
---
```

`name` and `description` are required for native `.omp` discovery
(`requireDescription: true`).
The directory name supplies `name` when you omit it.
Native discovery preserves additional frontmatter keys as unknown metadata.
Skill-specific fields, such as `argument-hint`, are safe to keep.
