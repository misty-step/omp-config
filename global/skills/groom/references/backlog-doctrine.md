# Backlog Doctrine

## Work ledger

| Tier | Board state | Purpose | Queue health |
|------|-------------|---------|--------------|
| **Shaped work** | Ready / claimed / running | Goal + oracle + proof plan + sequence | Evidence-backed, ordered, actively maintained |
| **Raw idea** | Backlog | Preserve a promising outcome before it is shaped | Named owner or reason to keep; no execution claim |

Resolve the board through the routing registry: Powder for ordinary Misty Step
repositories; Habitat for Adminifi and r90. A discovered local backlog tree is a
migration source only when the profile says so, never an active lifecycle.

Ideas move through board states during `/groom`:
- **Shape:** raw idea → bounded card with goal, acceptance, and proof plan.
- **Promote:** backlog → ready when dependencies and proof are executable.
- **Demote:** ready → backlog with evidence for deprioritization.
- **Close:** done, shipped, abandoned, or superseded with proof or a successor.

## What the active backlog is for

The board is the current plan, not storage for every thought. It stays ordered,
transparent, and actively maintained so the next decisions are obvious.

## Roster Product Lens

Roster is the agent declaration and primitive source for other repositories. Its own repo is where
patterns get validated before they spread.

When shaping Roster cards, prefer work that is one of:
- a reusable primitive, scaffold, reference, or policy other repos can adopt
- a proving-ground validation of a pattern meant to transfer outward
- debt removal that materially blocks downstream adoption or trust

If an item only improves Roster's own repo and has no clear transfer value, demote it,
merge it into a broader reusable effort, or rewrite it until the downstream payoff is explicit.

## Core rules

- **Backlog size is telemetry, not policy.** Large queues demand evidence:
  duplicates, stale owners, orphaned themes, unclear sequencing, or weak
  oracles. Consolidate because outcomes overlap, not because a counter fired.
- Reduce while adding: consolidation and deletion proposals are part of the
  same strategic groom that emits new ambition.
- Ready work names the proof loop, not just the desired outcome. For M+
  tickets, use `primitives/shared/references/verification-system-first.md` to
  state claim, falsifier, driver, grader, evidence packet, cadence, and gaps.
- **The backlog describes the best version of the software**, not the next
  safe increment. Rank by impact discounted by confidence; effort barely
  discounts when agents execute.
- Prefer one canonical item per outcome.
- Split discovery from delivery.
- Order work by user value, risk reduction, learning, and enablement.
- For Roster itself, optimize for downstream leverage first and local convenience second.
- Keep active work narrow. High WIP destroys prioritization.
- Ideas that are not execution-ready remain backlog cards with an explicit reason.

## Closure protocol

Close shipped work on its routed card with the exact proof link or command.
Supersede duplicates through relations and status; never maintain a second file
lifecycle.

## Healthy item shapes

### Epic

The default shape for strategic groom emissions. Use for a multi-issue initiative with a clear
product outcome. The epic should explain why the theme matters, what success looks like, and
which child issues carry execution. The epic itself still needs done criteria; an umbrella with
no oracle is the omnibus smell, not an epic.

### Feature

Use for a user-visible capability or operator-facing behavior change. The feature should be
valuable on its own and not just a mechanical subtask.

### Bug

Use when the current behavior is wrong. State the failure, repro, expected behavior, and user or
business impact.

### Task / Refactor / Research

Use only when the work is not a feature or bug. Keep these issue types outcome-linked:
- `task`: enabling work with a clear downstream payoff
- `refactor`: complexity reduction with preserved behavior
- `research`: a decision-seeking investigation with a deliverable

## Ordering guidance

Move items up when they:
- unblock or de-risk other work
- fix trust, correctness, or safety failures
- improve a critical user path
- create leverage across multiple future issues
- create leverage across multiple downstream repositories

Move items down when they:
- are polish without evidence
- duplicate a broader surviving issue
- depend on undefined architecture
- represent “maybe someday” ideas with no current owner
- only improve Roster's own repo without reusable payoff

## Cadence

- Triage new intake quickly into keep, merge, demote, or close.
- Re-read the active backlog regularly enough to remove stale assumptions.
- Run pruning passes, not just addition passes.
- Update the canonical issue body when the plan changes. Do not bury the truth in comments.
- Review `.groom/BACKLOG.md` every groom session — promote, archive, or leave.

## Smells

- 5 tickets that all mean the same thing
- “Polish” items that should be sub-points in a deeper item
- implementation tasks with no user or system outcome
- giant omnibus tickets with unclear done criteria
- items that require tribal knowledge to start
- “investigate” tickets with no decision target
- many open items with no ordering, theme, owner, oracle, or verification system
- stale items sitting open for weeks (ungroomed noise)
- BACKLOG.md not updated in 3+ groom sessions (icebox is rotting)

## Definition of ready

Before an issue is execution-ready, verify:
- the problem is specific
- the outcome is explicit
- dependencies are visible
- scope boundaries are present
- verification is executable
- downstream leverage or proving-ground rationale is explicit for Roster cards
- the issue can be completed in one coherent pass or should be split

## AI-agent adaptation

See `agent-issue-writing.md` for agent-specific issue shaping.

## Sources

- https://scrumguides.org/scrum-guide
- https://www.atlassian.com/agile/project-management/backlog-refinement-meeting
- https://www.atlassian.com/agile/project-management/product-backlog
