---
disable-model-invocation: true
name: groom
description: |
  Backlog grooming uses one always-on loop: tidy the board, then sweep.
  Investigate, research, critique, and shape ambitious work. Tidy every run.
  Use when: "groom", "backlog", "what should we build", "prioritize",
  "rethink this", "biggest opportunity", "moonshot", "audit skills",
  "skill quality audit".
  Trigger: /groom, /groom audit, /backlog, /rethink, /moonshot, /scaffold.
argument-hint: "[audit|--emphasis explore|rethink|moonshot|scaffold] [context]"
---

# /groom

Keep the board of record true and make the project more ambitious.
Normal strategic `/groom` is a mega-sweep, not triage.
Cover the full project, then distill it into a world-class plan and backlog diff.
A groom that only lists, lightly prioritizes, or emits a small set of issues is incomplete unless the user narrows the run.

The backlog diff is the artifact. Use prose to justify it.
Groom is a conversation about the operator's judgment, which is scarce input.
At intake, interrogate the operator about ambition, vision deltas, and hidden priors.
Use the `grill-me`-style posture from
`global/references/interrogate-first.md` by default.
Use this posture even when no backlog item arrives.
Keep the investigation sweep autonomous.
Read the codebase for facts.
Reserve interrogation for the operator's judgment, not facts you can read.

Use julius-caveman only for interim synthesis. Keep findings, code, commits, and final artifacts in normal English.

## Project Vision

Every strategic groom creates, refreshes, or validates a durable project vision before it ranks work.
Without a vision, brainstorming and backlog movement become local cleanup.

Read root VISION.md when it exists.
If it is missing or stale, route to /vision (owned by `/vision`).
When no vision exists, draft the smallest durable vision artifact.
Prefer root `VISION.md`.
Use `docs/product.md`, a roadmap doc, or a named backlog epic only when repository evidence rejects root vision.
Treat that draft as a groom emission.
Do not wait for a separate `/vision` pass.

- Keep the vision concrete: name the audience, job-to-be-done, category,
  standards, non-goals, strategic bets, and what excellent looks like in 6-12
  months.
- Revise the vision when live evidence contradicts it.
- Do not hide direction changes in chat, issue comments, or the final report.
- Backchain each theme and ticket to the part of the vision it advances, de-risks, simplifies, or deliberately rejects.
- A vision or moonshot artifact can carry a system map when prose cannot show
  the relationships or sequence:
  `global/references/image-generation.md`.

## Tidy (mandatory)

Keep the board of record true: use Powder cards, not stale files (Shared Operating
Spine: Durable State and Closeout; Powder skill, Powder MCP/CLI).
Read the card store. Close only through Powder tools
(`update_status`/`complete_card`). Do not invent side-channel closure:

- **Close shipped work.** When work merges, move its card to done/shipped with
  `update_status`/`complete_card`. Carry the shipping evidence. Never act on an
  assumption; Powder audits actor, time, and change.
- **Flag stale claims.** Surface an `in_progress` card for the operator when its
  branch merged or was deleted, or when it has no changes for 30+ days. Do not
  flip it silently.
- **Surface duplicates.** Propose consolidation. Never merge silently.
- **Backlog size is telemetry, not policy.** When the active queue looks too
  broad, report evidence: count, age, duplicates, stale owners, orphaned themes,
  and unfocused small items. Consolidate only when tickets share one outcome.
  Never veto an evidenced emission because of an arbitrary item count.

Do not use repository-local ticket directories.
Ordinary Misty Step repositories use Powder. R90 repositories use Habitat.
If you discover a legacy ticket tree, preserve its contents in the routed work
plane. Verify live readback. Remove the tree before normal grooming.

## Delegation

Delegate per the Shared Operating Spine (Act).
Strategic grooming is high-stakes by declaration. Default to the swarm.
Use independent lanes for product/value, operator experience, runtime reliability,
architecture, simplification/deletion, security/privacy, docs/onboarding,
ops/infra, testing/verification, agent readiness, and external exemplars.
Keep final prioritization with the lead.
Scale routine grooming—a tidy-only pass or scoped ticket check—to the stakes.
Use the Shared Operating Spine to choose fewer lanes instead of running the full
swarm.

## Mega Sweep

For any strategic groom, load `references/mega-groom.md`.
Treat it as the contract for swarm size, coverage map, source matrix, and output
shape. Use `references/investigation-bench.md` only for lane prompt shapes.
Treat it as a template library, not the whole run.

## Ambition Floor

Calibrate scope to what frontier agents can execute, not what a human team can
staff. Execution costs less. Vision remains scarce.
Strategic grooming must describe the best version of the whole project.
Then backchain from that standard into epics, deletions, sequencing, and first
pickups.

- **Brainstorm deeply from perspectives composed for this repo.**
  No canonical layer list exists. Pick obvious axes this codebase demands.
  Add lenses that stock lists miss: invert a premise, borrow from an adjacent
  domain, and ask what a competitor, operator, or first-time user would notice.
  Run perspectives in parallel fresh-context lanes.
  Pull in `/research` when outside knowledge would change a verdict.
  When the sweep returns only obvious findings, route divergence through
  `nous-creative-ideation`.
  Use its routed library of named methods (lateral provocations,
  analogy/biomimicry, premortem-and-inversion) to produce non-obvious lenses.
  Judge diversity and exploration depth fresh each session.
- **Describe the best version of this software,** not the next safe increment.
  Make it elegant, easy to change, personalizable, delightful, operationally
  boring, and valuable in practice.
  Treat the gap between that vision and the live repo as backlog material.
  Close it with epics.
- **Epic-scoped by default.** Strategic emissions are epics: a product outcome
  with an ordered child sequence. Do not split them into tasks first.
  Keep small items as children of an epic or as genuine isolated fixes.
- **Ambition requires evidence.** Vet every epic's premise as you vet every
  finding. A perspective that returns "all fine here" makes a claim; it does not
  prove that no work remains. Raise scope, not tolerance for unevidenced claims.

## Judgment (the actual grooming)

Investigate before giving opinions.
Run a tidy-only pass only when the user asks for one.
All other sessions require the `references/mega-groom.md` sweep.
Run genuinely independent perspectives in parallel.
Use `/research` when outside context would change a verdict.
Keep fresh-context lanes to decorrelate judgment, not fill a roster.

- **Read the live code, not only ticket text.** Read hotspots, debt
  concentrations, and the oldest stuck ticket.
  Every codebase has findings. "Everything is fine" means the investigation was
  shallow.
- **Challenge premises of the top items.** Ask whether each item names a symptom
  or a root cause. Treat each ticket's framing as a first draft. Reframe before
  re-ranking.
- **Propose deletions.** The best groom reduces the backlog. Give every deletion
  a rationale. Humans ratify removals.
- **Audit the repo's own harness.** Treat agent readiness as backlog work, not a
  separate process.
  Check for a verification skill with its real routes and commands (the
  highest-impact skill category).
  Check whether an agent can discover verified build, test, and lint commands and
  conventions without prior context.
  Check for runbooks for deployed surfaces.
  Check whether a CI gate would catch likely failures.
  Identify whether the quality floor is meaningful and enforced, or only
  advisory and arbitrary (`global/references/quality-gates.md`).
  Check security gates for secret leaks in files and Git/PR metadata before
  publication.
  Check for stale AGENTS/CLAUDE prose and missing product context for a cold
  agent. Treat each gap as a ticket.
- **Vet findings before presenting them.** Re-check each claim against the live
  repo. Open the file and run the command. Remove any claim that fails the
  second check.
  A false finding reduces trust.
- **Theme, then recommend.** Group findings by shared root cause.
  Rank impact after discounting by confidence. Agent execution makes effort a
  small discount. Argue for one concrete action per theme.
  Keep synthesis with the lead.
  When the plan is contestable, use the same `grill-me` method with the operator.
  Walk the decision tree one branch at a time: sequencing, deletions, then the
  next pickup. Recommend each branch instead of asking for approval of the full
  plan at once.

## Shape the board, not one ticket

Shaping is part of the groom. Do not run a separate one-ticket shaping workflow.
A request about one card still requires its board, dependencies, competing
priorities, and project vision.
The groom can conclude that one card is the only necessary change.
Base that conclusion on the surrounding board and vision.

Before promoting an epic or its children:

- **Challenge the premise.** Name the user or operator outcome. Treat the
  requested mechanism as one candidate.
- **Anchor it in live evidence.** Cite the owning code, tests, contracts,
  previous decisions, and one repository convention.
- **Choose a direction.** Compare credible alternatives that fail differently.
  Reject the alternatives and name one decision.
- **Define the scope.** State the outcome, non-goals, and invariants that must
  survive.
- **Make the oracle executable.** Name exact commands, routes, rendered
  behavior, or reviewer actions plus a falsifier.
- **Make execution cold-start safe.** Give each child enough repo anchors,
  dependencies, acceptance, and stop conditions for a focused lane.
- **Keep the premise durable.** Cite a digest, card, source path, or explicit
  waiver with residual risk.

Use `references/prd-ticket-quality.md` for M+ work,
`references/executable-oracles.md` when proof is disputed, and
`references/cli-design.md` for command-line surfaces. For a voice-derived
premise, use `references/voice-transcript-metadata.md`.

The groom output is a board-level decision packet: vision, themes, chosen and
rejected directions, ordered epics, dependencies, executable oracles, risks, and
the first pickup.
Do not create an isolated context packet that hides nearby work or conflicts.

## Ticket Format

Every card carries Goal + Oracle. Add a Verification System for M+/ready work.
Use the full template, epic shape, and promotion rules in
`references/ticket-format.md`.

## Audit Mode

`/groom audit` is a read-only harness-health report, not a grooming run.
Read the harness's skill/prompt usage signal (hook logs where present) and its
age since the last edit.
Judge the signal: low usage with high value-when-used is fine; say so.
Treat low usage with no demonstrated value as a deletion candidate.
Order findings by severity. Do not auto-fix.
Read harness-native skill-invocation logs and session evidence.
This repo deliberately has no semantic telemetry engine.

## Refuse

- Never auto-delete or silently merge tickets.
- Never archive a ticket whose trailer points at an unmerged branch.
- Never let backlog size alone veto an evidenced ticket or epic.
- Run the swarm for a strategic/mega-sweep groom when subagent, peer CLI, or
  sprite lanes are available. Strategic grooming is high-stakes by declaration.
  If delegation is blocked, report degraded mode and run the local matrix.
  Scale routine grooming to the stakes per the Shared Operating Spine.

## Gotchas

- **Stock-lens grooming.** Do not use the same investigator roster in every repo.
  Compose revealing perspectives for this codebase and session.
- **Stale backlog.** Treat age as a stale signal, not an automatic verdict.
  Inspect branch, owner, and live relevance before flipping, archiving, or
  proposing deletion.

## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract; this phase adds:

1. **Tidy diff** — Archive, change status, and flag items by ID. Add no padding.
2. **Source matrix** — swarm lanes, local commands, external research,
   skipped/failed lanes, and what each contributed.
3. **World-class plan** — vision, gaps, themes, sequencing, deletion/
   consolidation candidates, and the one best next pickup.
4. **Emissions** — Make epic/ticket edits with `**Why:**` naming the evidence
  lane. Make sure strategic emissions cover the domain map, not only the easiest
  implementation slice.
5. **Residual** — open questions, blocked dependencies, unverified areas,
   and what would make the sweep stronger.

Apply non-destructive backlog edits when the user asks for grooming.
Keep deletions, abandonments, and silent merges as proposals unless the user
explicitly approves them.
A groom run ends with a clean tree after it commits archives and writes
emissions. Deletions await ratification.
