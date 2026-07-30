# Prompting Fable-class models

Adapted for this harness from Matt Shumer's "How I Prompt Fable" (2026-07-03).
The operator ratified it the same day and added a directionality correction.
**These rules describe how to commission FABLE: the operator prompts the lead, or the lead prompts a rare peer-Fable lane.**
These rules do not loosen how Fable commissions downward.
When the lead dispatches non-Fable subagents (codex, sonnet, GLM), the lead has superior judgment in the pair.
The lead owns broad design decisions and specific implementation decisions.
Briefs to cheaper models remain prescriptive. Make them more prescriptive as capability drops.
Every lane receives bars, not adjectives; builder-never-grades; live status artifacts; evidence expectations; and house rules.

## The seven rules

1. **Goal, not steps** (when commissioning Fable). Hand large, underspecified outcomes.
Each dictated step overrides Fable's judgment.
Downward, a FABLE may dictate design and mechanism to a lesser lane.
This is intended and places frontier judgment at the higher tier.
2. **House rules, not scripts.** Define the few invariants that must survive every path.
Use repo red lines, ratified design verdicts, security boundaries, and "describe behavior in the agent's prompt instead of hard-coding special cases."
Store house rules in AGENTS.md / VISION.md / the lane card's constraints block.
Keep them short, absolute, and checkable.
3. **A bar, not adjectives.** "High quality" stops at the model's own idea of good enough.
Give an executable bar (see verification-system-first.md).
When you cannot define the measuring stick, DELEGATE ITS INVENTION.
"Figure out how to measure X, then hit it" is a legal, often superior oracle assignment.
4. **The builder never grades its own work.** A build lane can justify its own result.
Use a FRESH context to verify the real output: rendered pixels, the running app, or the live route.
Never use the diff alone.
Commission verification to PROVE THE WORK FAILS the bar and the house rules before anything ships.
Extend fresh-context-critique: target the artifact in reality, not the artifact in the repository.
5. **Loop until the bar, never until satisfied.** For creative or quality-chasing work, use this sequence.
Build → fresh-check → name the biggest gap → close it → repeat.
The model never declares itself finished. The loop ends at the bar or by operator call.
Long runs keep a LIVE STATUS ARTIFACT that the operator can view from a phone.
In this shop, post to the Bridge feed and/or a dedicated status page with screenshots, current gap, and next move.
6. **Use prior work.** Point lanes to prior artifacts as the quality bar ("match this, then beat it") and prior SESSION TRACES as technique.
Read what the prior build tried and learn what worked.
In this shop, QMD collections cover Claude/Codex session history.
Powder runs/comments/links and `~/.factory-lanes/wave*/` hold lane receipts.
Re-explaining a solved problem to a fresh lane wastes time.
7. **Remove blockers early.** Set budgets instead of asking permission.
Document key LOCATIONS, never values.
Write "make your own calls, return only when truly blocked or facing an operator-only decision" into the brief.
For huge, hard-to-reverse foundations, demand the plan first and surface every uncertainty as upfront questions.
Then run without stopping.

## Reviewing lane work: narration before diff

(Dax/OpenCode observation, operator-ratified 2026-07-04.) After a large lane change, do not start with the raw diff.
Ask the builder or a fresh reader for per-file narration.
Ask what changed and why. Include file names and function signatures, not function bodies.
Narration reveals unusual items early. One or two follow-ups usually resolve them.
Use the diff as final authority for the gate. Use narration to select files to read.
Apply the same principle to documentation surfaces: overview pages, PR bodies, and receipts.
Show signatures and flows first. Load bodies on demand. Show the overview before detail.

## Two approaches

- **Engineering:** Run several sessions in parallel, each triple-checked by its own sub-agents, with evidence in PR.
  ONE integrator session merges only, runs everything end-to-end as a real user, and keeps all checks passing.
  For overlapping features, one lane reads another lane's traces while it builds and integrates work as it arrives.
- **Creative:** Use the same loop and bar. Assign subagents per piece.
  Run independent parallel attempts. Keep the best attempt and carry successful methods into the next round.

## Ultracode

Reserve for FOUNDATIONS: a new system you will build on for months, where a correct base improves later work.
A good loop with an ambitious bar covers nearly everything else.
The ShadCN lesson: when cloning or matching something, existing scaffolding can obstruct work.
Starting from nothing can provide a better foundation.

## Anti-patterns in this file

- Recipe briefs to frontier lanes (mechanism dictation without a ruling behind it).
- Adjective oracles ("polished", "world-class") with no measuring stick.
- Builder-graded "done": a lane's own checklist used as acceptance evidence (see the self-graded-oracle-inflation incident, 2026-07-03).
- Long runs without a status artifact; results remain only in scrollback (see the memory-bakeoff loss, 2026-07-03).
- Lanes repeating work already covered by a prior trace.
