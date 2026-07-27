# design — null-case eval

## The one claim

An agent running a design pass with this skill produces a rendered screen the
operator judges better than the same agent's pass without it.

## Protocol

Three arms on one real project screen, same worker model, same brief:

1. **skill** — this SKILL.md, followed exactly.
2. **null** — the bare brief, no design guidance.
3. **incumbent** — only when comparing against a prior version of this skill.

Each arm edits its own full copy of the app; behavior must keep working.
Render every arm and the untouched baseline in a real browser; screenshot
desktop (~1440w) and mobile (~390w).

**Rendered surfaces are never judged from source text.** Grading input is
screenshots only, opaque labels, key sealed until every grader reports.
Graders: a vision-capable blind model ranking plus the operator's blind pick.
The skill keeps its place only if the skill arm beats null; ties go to null
because the skill costs context.

## First instance

2026-07-22 rebuild trial: three arms (old skill / new skill / null) on the
comms-lab review app. Evidence:
`~/Development/crucible/runs/local/design-rebuild/` (screenshots, sealed
key, arm reports, verdict). Operator judgment recorded on Powder card
`design-skill-rebuild`.
