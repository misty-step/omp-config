# ADR 0003: Add a project roadmap application

- Status: Accepted
- Date: 2026-07-30

## Context

Root `VISION.md` states durable project direction when a repository has one.
Powder stores actionable work, claims, attempts, relations, and proof.
Neither surface gives the operator a small visual plan for early strategic work.
Early roadmap items are questions and outcomes, not ready tickets.
A backlog makes these items look more complete than they are.

## Decision

Add a hand-only `/roadmap` skill with `disable-model-invocation: true`.
The skill creates or updates root `ROADMAP.html` and opens it in a browser.
The artifact summarizes and links `VISION.md` when that file exists.
The artifact does not replace `VISION.md` or a work ledger.

The artifact stores project content in one JSON data block.
The surrounding HTML owns the visual structure and browser behavior.
Each roadmap item has a stable identifier, outcome, proof, open question, and coverage links.
Each artifact has exactly one current item and five to twelve strategic items.
The artifact contains no ticket state, claim state, or attempt history.

The skill loads `/grilling` and asks all open decisions in batches.
The skill confirms shared understanding before it changes files.
The skill applies ASD-STE100 rules to all operator-facing text.
The skill validates the artifact and checks desktop and mobile browser views.

## Consequences

The operator gets one concise repository surface for vision and sequence.
Agents get a clear boundary between strategic direction and actionable work.
A repository can use the artifact without a web build or a running service.
The JSON block lets an agent update content without rewriting the layout.

The artifact is a projection, not a new authority system.
Powder remains the work ledger.
Source repositories remain authoritative for their products and services.

## Reversal condition

Remove this surface when another system supplies the same small, versioned, offline, and repository-local planning view.
