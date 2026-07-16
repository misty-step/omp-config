---
name: groom
description: |
  Backlog grooming as one always-on loop: tidy the board, then sweep —
  investigate, research, critique, and shape ambitious work. Tidy every run.
  Use when: "groom", "backlog", "what should we build", "prioritize",
  "rethink this", "biggest opportunity", "moonshot", "audit skills",
  "skill quality audit".
  Trigger: /groom, /groom audit, /backlog, /rethink, /moonshot, /scaffold.
argument-hint: "[audit|--emphasis explore|rethink|moonshot|scaffold] [context]"
---

# /groom

Keep the board of record true and make the project more ambitious. Normal
strategic `/groom` is a mega-sweep, not triage: boil the ocean on purpose, then
distill it into a world-class plan and backlog diff. A groom that only lists,
lightly prioritizes, or emits a tiny handful of issues is incomplete unless the
user explicitly scoped the run down.

The backlog diff is the artifact; prose exists to justify it. Groom is a
conversation at the seams where the operator's judgment is the scarce input. At
intake, interrogate the operator on ambition, vision deltas, and hidden priors
so the sweep aims true — the `grill-me`-style posture in
`primitives/shared/references/interrogate-first.md` is the default here, not a
fallback gated on arriving with a backlog item. The investigation sweep stays
autonomous: explore the codebase for what it can answer, and reserve
interrogation for the operator's judgment, not facts you can read.

julius-caveman for interim synthesis only; findings, code, commits, and final
artifacts stay normal English.

## Project Vision

Every strategic groom creates, refreshes, or explicitly validates a durable
project vision before ranking work; without one, brainstorming and backlog
movement collapse into local cleanup.

Read root VISION.md when present; if missing or stale, route to /vision
(owned by `/vision`). Groom's delta: it drafts the smallest durable
vision artifact itself when none exists — prefer root `VISION.md`;
`docs/product.md`, a roadmap doc, or a named backlog epic only when repo
evidence says root vision is the wrong fit — and treats that draft as a
first-class groom emission rather than waiting on a separate `/vision` pass.

- Keep the vision concrete: audience, job-to-be-done, category, standards,
  non-goals, strategic bets, and what excellent looks like in 6-12 months.
- Revise the vision when live evidence contradicts it; don't bury direction
  changes in chat, issue comments, or the final report only.
- Backchain: themes and tickets should say which part of the vision they
  advance, de-risk, simplify, or deliberately reject.
- A vision or moonshot artifact can carry a one-glance system map when
  relationships or sequencing are too complex for prose alone:
  `primitives/shared/references/image-generation.md`.

## Tidy (mandatory)

Keep the board of record true — Powder cards, not stale files (Shared Operating
Spine: Durable State and Closeout; misty-powder skill, Powder MCP/CLI). Consume the card store; don't
hand-roll closure:

- **Close shipped work.** A card whose work merged moves to done/shipped via
  `update_status`/`complete_card`, carrying the shipping evidence — never on a
  hunch (Powder audits actor, time, and change).
- **Flag stale claims.** An `in_progress` card on a merged or deleted branch,
  or one untouched 30+ days, gets surfaced for the operator — not silently
  flipped.
- **Surface duplicates** with a proposed consolidation; never merge silently.
- **Backlog size is telemetry, not policy.** When the active queue looks too
  broad, report the evidence: count, age, duplicates, stale owners, orphaned
  themes, unfocused small items. Consolidate only when tickets genuinely share
  one outcome; never veto an evidenced emission on an arbitrary item count.

Repository-local ticket directories are forbidden. Ordinary Misty Step
repositories use Powder; R90 repositories use Habitat. If a legacy ticket tree
is discovered, preserve its contents in the routed work plane, verify live
readback, and remove the tree before continuing normal grooming.

## Delegation

Delegate per the Shared Operating Spine (Act). Strategic
grooming is high-stakes by declaration and defaults to the swarm: independent
lanes for product/value, operator experience, runtime reliability,
architecture, simplification/deletion, security/privacy, docs/onboarding,
ops/infra, testing/verification, agent readiness, and external exemplars,
with the lead keeping final prioritization. Routine grooming — a tidy-only
pass, a scoped ticket check — scales the bench down to the stakes per the
Shared Operating Spine instead of running the full swarm.

## Mega Sweep

For any strategic groom, load `references/mega-groom.md`. It is the contract
for swarm size, coverage map, source matrix, output shape, and the
"world-class plan" bar. Use `references/investigation-bench.md` only for lane
prompt shapes; it is a template library, not the whole run.

## Ambition Floor

Calibrate scope to what frontier agents can execute, not what a human team
can staff. Execution is cheap; vision is the scarce input. Strategic grooming
must describe the best version of the whole project, then backchain from that
standard into epics, deletions, sequencing, and first pickups.

- **Brainstorm deep, from perspectives composed for this repo.** There is
  no canonical list of layers to sweep. Pick the obvious axes this codebase
  demands, then add lenses no stock list would hand you — invert a premise,
  borrow from an adjacent domain, ask what a competitor, operator, or
  first-time user would notice. Fan the perspectives out as parallel
  fresh-context lanes; pull in `/research` when outside knowledge would
  change a verdict. When the sweep keeps returning the obvious (the *mundane
  harvest* failure), route the divergence through `nous-creative-ideation` — a
  routed library of named methods (lateral provocations, analogy/biomimicry,
  premortem-and-inversion) that manufactures non-obvious lenses on purpose. The
  bar is genuine diversity and depth of exploration, judged fresh each session.
- **Describe the best version of this software,** not the next safe
  increment: elegant, easy to change, personalizable, delightful,
  operationally boring, and valuable enough to matter. The distance between
  that vision and the live repo is backlog material; close it with epics.
- **Epic-scoped by default.** Strategic emissions are epics — a product
  outcome with an ordered child sequence — never pre-shredded tasks. Small
  items exist as children of an epic or as genuine isolated fixes.
- **Ambition is not slop.** Every epic's premise earns the same vetting as any
  finding; a perspective that returns "all fine here" is making a claim, not
  clearing the bar. The floor raises scope, not tolerance for unevidenced
  claims.

## Judgment (the actual grooming)

Investigate before opining. A tidy-only pass exists, but only when the user
asks for one; any other session owes the `references/mega-groom.md` sweep,
with genuinely independent perspectives run in parallel and `/research` when
outside context would change a verdict. Fresh-context lanes exist to
decorrelate judgment, not to fill a roster.

- **Read the live code, not just ticket text.** Hotspots, debt
  concentrations, the oldest stuck ticket. Every codebase has findings;
  "everything is fine" means the investigation was shallow.
- **Challenge premises of the top items.** Symptom or root cause? A ticket's
  framing is a first draft. Reframe before re-ranking.
- **Propose deletions.** The best groom shrinks the backlog. Every deletion
  is a proposal with rationale — humans ratify removals.
- **Audit the repo's own harness.** Agent readiness is backlog work, not a
  separate ceremony: does this repo have a verification skill with its real
  routes/commands (the highest-impact skill category)? Verified build/test/
  lint commands and conventions an agent can discover cold? Runbooks for
  its deployed surfaces? A CI gate that would catch the likely failure?
  A meaningful, enforced quality floor that gates the diff and ratchets legacy
  debt, or only advisory, arbitrary gates
  (`primitives/shared/references/quality-gates.md`)? Security gates that catch
  secret leaks in files and Git/PR metadata before publication? Stale
  AGENTS/CLAUDE prose? Product context a cold agent would need? Each gap is a
  ticket like any other.
- **Vet findings before presenting them.** Re-check each claim against the
  live repo — open the file, run the command. A plausible finding that
  doesn't survive a second look is noise that erodes trust in the whole
  groom.
- **Theme, then recommend.** Group findings by shared root cause, rank by
  impact discounted by confidence — effort barely discounts now that agents
  execute — and argue for one concrete action per theme. Synthesis stays on
  the lead; when the plan is contestable, land it with the operator the same
  `grill-me` way — walk the decision tree (sequencing, deletions, the next
  pickup) one branch at a time, recommending each — instead of dropping the
  full plan for a rubber-stamp.

## Ticket Format

Every card carries Goal + Oracle always, plus a Verification System for
M+/ready work — full template, epic shape, and promotion rules:
`references/ticket-format.md`.

## Audit Mode

`/groom audit` is a read-only harness-health report, not a grooming run: read
the harness's skill/prompt usage signal (hook logs where present) and staleness
vs last edit. Judge it — low usage with high value-when-used is fine, say so;
low usage with no story is a deletion candidate. Order findings by severity; do
not auto-fix. Read harness-native skill-invocation logs and session evidence;
Roster deliberately has no semantic telemetry engine.

## Refuse

- Never auto-delete or silently merge tickets.
- Never archive a ticket whose trailer points at an unmerged branch.
- Never let backlog size alone veto an evidenced ticket or epic.
- Never skip the swarm on a strategic/mega-sweep groom when subagent, peer
  CLI, or sprite lanes are available — it's high-stakes by declaration; if all
  delegation is blocked, report degraded mode and do the local matrix.
  Routine grooming may scale the bench down per the Shared Operating Spine.

## Gotchas

- **Stock-lens grooming.** Running the same investigator roster in every repo
  is process, not thought. The revealing perspectives are composed for this
  codebase, this session.
- **Backlog as graveyard.** Age is a stale signal, not an automatic verdict.
  Inspect branch, owner, and live relevance before flipping, archiving, or
  proposing deletion.

## Completion Gate

See `primitives/shared/AGENTS.md` (Prove; Durable State and Closeout) for the
shared core; this phase adds:

1. **Tidy diff** — archived, flipped, flagged; by ID, no padding.
2. **Source matrix** — swarm lanes, local commands, external research,
   skipped/failed lanes, and what each contributed.
3. **World-class plan** — vision, gaps, themes, sequencing, deletion/
   consolidation candidates, and the one best next pickup.
4. **Emissions** — epic/ticket edits with `**Why:**` naming the evidence
   lane; strategic emissions show breadth across the domain map, not just
   the easiest implementation slice.
5. **Residual** — open questions, blocked dependencies, unverified areas,
   and what would make the sweep stronger.

Apply non-destructive backlog edits when the user asked for grooming;
deletions, abandonments, and silent merges stay proposals unless explicitly
approved. A groom run ends with a clean tree: archives committed, emissions
written, deletions awaiting ratification.
