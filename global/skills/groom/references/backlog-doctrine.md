# Backlog Doctrine

## Work ledger

| Tier | Board state | Purpose | Queue health |
|------|-------------|---------|--------------|
| **Shaped work** | Ready / claimed / running | Goal + oracle + proof plan + sequence | Evidence-backed, ordered, actively maintained |
| **Raw idea** | Backlog | Preserve a promising outcome before it is shaped | Named owner or reason to keep; no execution claim |

Resolve the board through the routing registry: use GitHub Issues for Misty Step
repositories and Habitat for Adminifi and r90.
Treat a discovered local backlog tree as a migration source only when the
profile says so. Never treat it as an active lifecycle.

Ideas move through board states during `/groom`:
- **Shape:** raw idea → bounded card with goal, acceptance, and proof plan.
- **Promote:** backlog → ready when dependencies and proof are executable.
- **Demote:** ready → backlog with evidence for deprioritization.
- **Close:** done, shipped, abandoned, or superseded with proof or a successor.

## What the active backlog is for

The board is the current plan, not storage for every thought.
Keep it ordered, transparent, and current so the next decisions stay obvious.

## omp-config Product Lens

omp-config is the agent declaration and primitive source.
It projects into the live agent home (`~/.omp/agent`).
Its repo validates patterns before they spread.

When shaping omp-config issues on the GitHub board, prefer work that is one of:
- a reusable primitive, scaffold, reference, or policy other repos can adopt
- a proving-ground validation of a pattern meant to transfer outward
- debt removal that materially blocks downstream adoption or trust

If an item only improves omp-config's own repo and has no clear transfer value,
demote it, merge it into a broader reusable effort, or rewrite it until the
downstream payoff is explicit.

## Core rules

- **Backlog size is telemetry, not policy.** Large queues demand evidence:
  duplicates, stale owners, orphaned themes, unclear sequencing, or weak
  oracles. Consolidate because outcomes overlap, not because the count reached a
  threshold.
- Reduce the backlog while adding work. Include consolidation and deletion
  proposals in the same strategic groom that adds new ambition.
- Ready work names the proof loop, not only the desired outcome. For M+ tickets,
  use `global/references/verification-system-first.md` to state claim,
  falsifier, driver, grader, evidence packet, cadence, and gaps.
- **The backlog describes the best version of the software**, not the next safe
  increment. Rank by impact. Discount impact by confidence. Give effort little
  weight because agents execute.
- Prefer one canonical item per outcome.
- Split discovery from delivery.
- Order work by user value, risk reduction, learning, and enablement.
- For omp-config itself, optimize for downstream leverage first and local convenience second.
- Keep active work narrow. High WIP destroys prioritization.
- Keep ideas that are not execution-ready as backlog issues with an explicit
  reason.

## Closure protocol

Close shipped work on its routed card with the exact proof link or command.
Supersede duplicates through relations and status. Never maintain a second file
lifecycle.

## Healthy item shapes

### Epic

The default shape for strategic groom emissions is an epic.
Use an epic for a multi-issue initiative with a clear product outcome.
Explain why the theme matters, what success looks like, and which child issues
carry execution.
Give the epic its own done criteria. An umbrella without an oracle is storage,
not an epic.

### Feature

Use a feature for a user-visible capability or operator-facing behavior change.
Make the feature valuable on its own, not only a mechanical subtask.

### Bug

Use a bug when the current behavior is wrong.
State the failure, repro, expected behavior, and user or business impact.

### Task / Refactor / Research

Use these issue types only when the work is not a feature or bug.
Keep each type outcome-linked:
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
- only improve omp-config's own repo without reusable payoff

## Cadence

- Triage new intake quickly into keep, merge, demote, or close.
- Re-read the active backlog often enough to remove stale assumptions.
- Run pruning passes, not only addition passes.
- Update the canonical issue body when the plan changes. Do not bury the truth
  in comments.
- Review `.groom/BACKLOG.md` every groom session. Promote, archive, or leave.

## Smells

- 5 tickets that all mean the same thing
- “Polish” items that belong as sub-points in a deeper item
- implementation tasks with no user or system outcome
- giant omnibus tickets with unclear done criteria
- items that require tribal knowledge to start
- “investigate” tickets with no decision target
- many open items with no ordering, theme, owner, oracle, or verification system
- stale items sitting open for weeks without review
- BACKLOG.md not updated in 3+ groom sessions (the backlog is stale)

## Definition of ready

Before an issue is execution-ready, verify:
- the problem is specific
- the outcome is explicit
- dependencies are visible
- scope boundaries are present
- verification is executable
- downstream leverage or proving-ground rationale is explicit for omp-config issues
- the issue can be completed in one coherent pass or needs a split

## AI-agent adaptation

See `agent-issue-writing.md` for agent-specific issue shaping.

## Sources

- https://scrumguides.org/scrum-guide
- https://www.atlassian.com/agile/project-management/backlog-refinement-meeting
- https://www.atlassian.com/agile/project-management/product-backlog
