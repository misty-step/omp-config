---
disable-model-invocation: true
name: vision
description: |
  Create or update root VISION.md as a first-class project north-star artifact.
  Interrogate the operator, research the repository, distill its philosophy, and
  wire repo-local primitives to read it. Use when: "vision", "vision.md",
  "project vision", "north star", "what is this project", "clarify product
  direction", "write/update VISION.md", "project philosophy", "why does this
  repo exist". Trigger: /vision, /north-star.
argument-hint: "[create|update|refresh|audit] [project-context]"
---

# /vision

Create or update root `VISION.md`. This compact project north star gives cold
agents, maintainers, and future contributors one answer to three questions:
"what are we building, why, and what kind of excellence matters here?"

Conversational first. Artifact always.

## Contract

- Ask the operator what the deal is unless the request already contains enough
  project intent. Batch open questions. Use the interrogate-first lens
  (`global/references/interrogate-first.md`) when hidden decisions matter.
- Read the live repository before drafting: existing `VISION.md`, `AGENTS.md`,
  `README*`, positioning or product docs, roadmap or backlog, manifests, examples,
  demos, tests, screenshots, and repo-local skills or prompts that encode
  product behavior.
- Research only what you need. Start local. Read sibling or adjacent projects
  when they explain fit. Read web or external exemplars only when category,
  audience, competition, or public-facing positioning is unclear.
- Clarify lifespan. Ask whether this is a spike, internal utility, consulting
  artifact, product substrate, long-lived product, or public standard. Lifespan
  changes tone, maintenance bar, backlog ambition, and non-goals.
- Write the root artifact at `VISION.md`. Do not place the canonical artifact in
  `docs/` unless repository evidence proves that root is wrong.
- Let the project determine the structure. Use no required headings or house
  template. Keep the artifact short enough for agents to read.
- Capture uniquely load-bearing information: intent, philosophy, audience,
  category, fundamentals, standards, non-goals, strategic bets, and excellent
  outcomes over the horizons that the project needs.
- Wire consumers, not copies. When `VISION.md` is created or materially changed,
  update relevant repo-local `AGENTS.md`, skills, prompts, or runbooks with
  pointer lines to `VISION.md`. Never duplicate vision prose into them.

## Quality Check

Load `references/vision-quality.md` when you draft, review, or update the
artifact. Use it as a taste and checklist reference, not as a template.

## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract.
`/vision` adds:

1. What changed in `VISION.md`.
2. Which questions were answered, deferred, or still need the operator.
3. Sources read: local files, sibling projects, external references, and what
   each source changed.
4. Consumers wired: `AGENTS.md`, skills, prompts, runbooks, or explicit none.
5. Residual risk: stale assumptions, missing competitive context, or unclear
   lifespan.

## Verification

For repo edits:

```sh
test -f VISION.md
rg -n "VISION\\.md" AGENTS.md .agents .codex .claude .pi .antigravitycli skills 2>/dev/null
```

Then run the repository's named gate.

## Gotchas

- Generic mission statement. If it could describe three other repositories, it
  failed.
- Over-prescribed structure. A beautiful template can erase the project's real
  shape.
- Backlog dump. Vision decides what belongs; it is not a sorted task list.
- Marketing voice by default. Use marketing language only when that is the
  repository's real surface.
- `docs/vision.md` drift. Root `VISION.md` is the default canonical path.
- Stale consumers. If local harness primitives keep making direction calls from
  old prose, the vision is decorative.
- Research that does not change a decision. A giant competitive map wastes work.
