# Prompting Fable-class models

Adapted for this harness from Matt Shumer's "How I Prompt Fable" (2026-07-03).
The operator ratified it the same day and added a directionality correction.
These rules define how to commission FABLE: the operator prompts the lead, or the lead prompts a rare peer-Fable lane.
They do not loosen downward commissioning. The lead has superior judgment in the pair and owns broad design and implementation decisions.
Cheaper-model briefs stay prescriptive; lower capability requires more prescription.
Every lane receives bars, not adjectives; builder-never-grades verification; live status artifacts; evidence expectations; and house rules.

## Commissioning contract

1. **Goal, not steps.** Give Fable large, underspecified outcomes. Each dictated step overrides its judgment. Downward, FABLE may dictate design and mechanism.
2. **House rules, not scripts.** State short, absolute, checkable invariants: repo red lines, ratified design verdicts, and security boundaries.
   Describe behavior in the agent's prompt instead of hard-coding special cases. Store the rules in `AGENTS.md`, `VISION.md`, or the lane card's constraints block.
3. **Executable bars.** Define a measuring stick (`global/references/verification-system-first.md`). Delegate metric invention when you cannot define it.
4. **The builder never grades.** Fresh context verifies rendered pixels, the running app, or the live route; never use the diff alone. Commission verification to prove failure against the bar and house rules before shipping.
5. **Loop to the bar.** Build, fresh-check, name the biggest gap, close it, and repeat until the bar passes or the operator stops.
   The model never declares itself finished. Keep a live Bridge feed or status page, viewable from a phone, with screenshots, the current gap, and the next move.
6. **Use prior work.** Point to prior artifacts as bars: match them, then beat them. Read session traces for what worked and use them as techniques.
   QMD holds Claude/Codex history; Powder runs, comments, links, and `~/.factory-lanes/wave*/` hold lane receipts. Do not re-explain solved work.
7. **Remove blockers early.** Set budgets instead of asking permission; document key locations, never values. Tell lanes to make their own calls and return only when truly blocked or facing an operator-only decision. For huge, hard-to-reverse foundations, request the plan and upfront uncertainty questions, then run without stopping.

## Review before the diff

Dax/OpenCode observation, operator-ratified 2026-07-04: ask the builder or a fresh reader for per-file narration after a large lane change.
Ask what changed and why; include file names and function signatures, not function bodies.
Narration reveals unusual items early; one or two follow-ups usually resolve them.
Use the diff as final authority for the gate; use narration to select files to read.
Apply this order to documentation surfaces: overview pages, PR bodies, and receipts.
Show signatures and flows first. Load bodies on demand.

## Two approaches

- **Engineering:** Run parallel sessions, each triple-checked by its sub-agents, with evidence in the PR. One integrator merges only, runs end to end as a real user, and keeps checks passing. Overlapping lanes read another lane's traces while building and integrating arriving work.
- **Creative:** Use the same loop and bar. Assign subagents per piece, run independent parallel attempts, keep the best attempt, and carry successful methods forward.

## Foundations

Reserve Ultracode for a new foundation you will build on for months, where a correct base improves later work. A good loop with an ambitious bar covers nearly everything else.
The ShadCN lesson: existing scaffolding can obstruct matching; starting from nothing can provide a better foundation.

## Anti-patterns

- Recipe briefs to frontier lanes that dictate mechanism without a ruling.
- Adjective oracles such as "polished" or "world-class" without a measuring stick.
- Builder-graded "done" based on a lane checklist (see the self-graded-oracle-inflation incident, 2026-07-03).
- Long runs without a live status artifact; results stay in scrollback (see the memory-bakeoff loss).
- Lanes repeating work covered by a prior trace.
