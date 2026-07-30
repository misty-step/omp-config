# Ticket Format

Create work in the repository's registry-routed board.
Ordinary Misty Step repositories use Powder. Adminifi and r90 use Habitat.
Never create a local ticket file as an unregistered fallback.

## Required card fields

- **Title:** imperative outcome, not implementation trivia.
- **Goal/body:** one sentence naming the user or system outcome, followed by
  constraints and non-goals where needed.
- **Acceptance:** mechanically verifiable criteria. Rough oracles are better
  than none, but every active card has one.
- **Proof plan:** for M+ or ready work, name claim, falsifier, driver, grader,
  evidence packet, cadence, and known gaps per
  `global/references/verification-system-first.md`.
- **Lifecycle:** priority P0–P3, estimate S–XL, status, autonomy, repository,
  labels, and explicit relations (`blocked_by`, `blocks`, `related`).

Use epics for strategic emissions.
Give each epic its own goal and acceptance.
Model child outcomes as related or blocked cards when they are independently
runnable.
An umbrella without done criteria is storage, not an epic.

Before moving M+ work to ready, apply `references/prd-ticket-quality.md`.
If the card lacks a bounded outcome, executable acceptance, or proof path, keep
it in backlog.
When grooming this repo, also apply `references/backlog-doctrine.md`.
