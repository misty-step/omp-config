---
name: brief
description: One-screen executive brief — verdict, open calls, ranked moves, risks.
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

Cut to what changes an operator decision; process narration drops. Return
only the brief, under 200 words:

- **Verdict** — one or two sentences: where the work stands and whether
  it is on track.
- **Decisions** — at most three open calls, highest stakes first. Each:
  the question, the options, your recommendation, the cost of waiting.
  When more wait, one clause gives the count. Omit when none.
- **Moves** — at most five, highest first. Each: identifier, what it is,
  why next, and the move (`do`, `wait`, `drop`).
- **Watch** — at most three risks, stale claims, or surprises. Omit when
  none.

Do not implement; do not groom the board.

Completion criterion: every open call is decidable from the brief or
counted by it — no follow-up question from them, no essay from you.
