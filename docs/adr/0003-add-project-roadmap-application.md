# ADR 0003: Add a project roadmap application

- Status: Superseded (2026-08-07)
- Superseded-by: `/groom` (vision + board) and Powder; the `/roadmap` skill and `ROADMAP.html` app are removed
- Date: 2026-07-30

## Context (historical)

Root `VISION.md` stated durable project direction.
Powder stored actionable work.
Neither surface gave the operator a small visual plan for early strategic work.

## Decision (historical)

A hand-only `/roadmap` skill created root `ROADMAP.html` as a browser planning
surface with a JSON data block, five to twelve strategic items, and exactly one
current item. Vision and the work ledger stayed separate.

## Supersession (current)

Product direction is `/groom` (including vision mode) plus Powder cards.
Do not recreate `ROADMAP.html` or a parallel roadmap skill.
Sequence and proof live on the board under `VISION.md`.

## Consequences (historical)

Operators could open a local roadmap artifact without promoting speculative
items to tickets. The cost was a second durable planning surface beside vision
and Powder, which this supersession removes.
