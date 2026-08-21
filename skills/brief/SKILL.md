---
name: brief
description: Decision-grade executive brief grounded in evidence — why things stand, what needs a call.
disable-model-invocation: true
---

# Brief

The operator runs many sessions and projects at once and arrives with
minutes. Give them one decision-grade brief: what is true, what needs
their call, what happens next. Ground in evidence, then cut to what
changes a decision.

## 1. Ground

Collect current evidence. Mark an inference when direct evidence is
unavailable.

- **Session:** completed work and its verification, active work,
  blockers, material unknowns.
- **Ship state:** branch, its merge-base with the default branch, dirty
  paths you did not make, the last change that still defines the running
  system, and drift between the product job (README, VISION, or the live
  surface, not ticket titles) and the code that runs.
- **Ledger:** find the work tracker — `AGENTS.md`, `VISION.md`,
  `.mcp.json`, or `.omp/mcp.json` names one; else the origin host's issue
  list; else say the ledger is missing. Account for every ready,
  in-progress, and blocked item; group unscheduled work by count unless
  one is the obvious next bet. A stale in-progress claim is a finding.

Completion criterion: every material session fact, ship-state fact, and
board item is accounted for from observed evidence.

## 2. Deliver

Cut to what changes an operator decision; process narration drops. Weight
the brief mostly why, some what, a smidge of how:

- **Why first** — the causes and stakes behind the state. Why the work
  stands where it stands, why a call matters now, why the obvious next
  step is or isn't right. This is the body of the brief.
- **What second** — the facts that carry those judgments: state,
  numbers, findings. Include only what supports a why or forces a call.
- **How last** — mechanics appear only when they change a decision (the
  command that ships it, the path it lands in), never as narration.

Form follows the material; there is no mandated shape:

- Open with the bottom line in plain sentences: where things stand and
  why. A quiet session is three sentences and done.
- Surface every open call — question, live options, your recommendation,
  the cost of waiting — highest stakes first. When more than a few wait,
  name the top ones and count the rest. No calls means say so and stop.
- Beyond that, include only what a decision depends on: risks, surprises,
  stale claims worth flagging. Everything else drops.
- As long as the material earns, as short as it allows. Headings appear
  when the brief outgrows prose, never by default.

Do not implement; do not groom the board.

Completion criterion: every open call is decidable from the brief or
counted by it, and every claim traces to observed evidence or is marked
inferred — no follow-up question from them, no essay from you.
