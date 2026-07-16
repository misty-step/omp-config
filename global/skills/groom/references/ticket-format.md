# Ticket Format

Create work in the repository's registry-routed board. Ordinary Misty Step
repositories use Powder; Adminifi and r90 use Habitat. Never create a local
ticket file as an unregistered fallback.

## Required card fields

- **Title:** imperative outcome, not implementation trivia.
- **Goal/body:** one sentence naming the user or system outcome, followed by
  constraints and non-goals where needed.
- **Acceptance:** mechanically verifiable criteria. Rough oracles are better
  than none, but every active card has one.
- **Proof plan:** for M+ or ready work, name claim, falsifier, driver, grader,
  evidence packet, cadence, and known gaps per
  `primitives/shared/references/verification-system-first.md`.
- **Lifecycle:** priority P0–P3, estimate S–XL, status, autonomy, repository,
  labels, and explicit relations (`blocked_by`, `blocks`, `related`).

Epics are the default strategic emission. Give the epic its own goal and
acceptance, then model child outcomes as related or blocked cards when they are
independently runnable. An umbrella with no done criteria is storage, not an
epic.

Before moving M+ work to ready, apply `/shape`'s
`references/prd-ticket-quality.md`. If the card still lacks a bounded outcome,
executable acceptance, or proof path, keep it in backlog. When grooming Roster,
also apply `references/backlog-doctrine.md`.
