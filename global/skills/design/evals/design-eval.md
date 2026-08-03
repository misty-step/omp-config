# design — null-case eval

## The one claim

An agent using this skill must produce a rendered screen that the operator
judges better than the same agent's pass without it.

## Protocol

Three arms on one real project screen, same worker model, same brief:

1. **skill** — this SKILL.md, followed exactly.
2. **null** — the bare brief, no design guidance.
3. **incumbent** — only when comparing against a prior version of this skill.

Each arm edits its own full copy of the app. Keep behavior working. Render every
arm and the untouched baseline in a real browser. Take desktop (~1440w) and
mobile (~390w) screenshots.

Judge rendered surfaces from screenshots, never source text. Use screenshots
only as grading input. Keep labels opaque and seal the key until every grader
reports.
Graders: a vision-capable blind model ranking plus the operator's blind pick.
Keep the skill only if its arm beats null. Give ties to null because the skill
costs context.

## First instance

2026-07-22 rebuild trial: three arms (old skill / new skill / null) on the
comms-lab review app. Evidence:
`~/Development/misty-step/crucible/runs/local/design-rebuild/` (screenshots, sealed
key, arm reports, verdict). Operator judgment recorded on Powder card
`design-skill-rebuild`.
