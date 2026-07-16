---
name: orient
description: |
  Fast orientation from live local evidence — at session start, or picking up
  work a dead session left unfinished. Use when: "orient yourself", "new
  session", "where are we", "catch me up before acting", after compaction,
  after switching worktrees, before choosing a workflow; or "pick up where it
  left off", "the session died / hit its usage limit", "continue that
  agent's work". Trigger: /orient, /ground, /session-start, /pickup.
argument-hint: "[scope|--deep]"
---

# /orient

Ground the session in repo truth — not memory, not a stale summary. Read-only,
fast.

## What it produces

A short, natural read of where things stand and the one move that follows. You
are writing to stop a wrong first step, not to fill a form. In plain prose,
cover only what the evidence supports:

- where we are (repo, branch, clean vs dirty) and what's in flight;
- the single best next move, why it wins, and what would make it wrong.

Punchy beats complete. A sentence or two when the state is obvious; a short list
only when it's genuinely tangled. No fixed template, no field-by-field rundown,
no history dump. If the user already gave a precise command and the state is
clear, that sentence is the whole report. `--deep` is the only license to dig.

Example, obvious state: *"On `master`, clean, CI green. Shaped ticket 058 is the
only thing in flight and nothing blocks it — next is `/deliver 058`."*

## Where the signal lives

Read the smallest set that explains the workspace; skip whatever the prompt
already settled. Beyond the obvious (`git status`, branch, recent commits):

- scoped then repo `AGENTS.md`; `VISION.md`/`project.md` for focus (`README.md` only if still unclear)
- active work from the registry-routed board of record: Powder for ordinary Misty Step repositories; Habitat for Adminifi and r90. Start with repository-level stats, then enumerate the repository before status slices. An empty filtered result proves only that the filter matched nothing. Treat a local backlog tree only as an explicit migration source named by the routing profile, never as a parallel ledger
- roster probe (`roster list` / roster MCP) — only when the next move is a delegation

## Picking up a dead session

Sessions die mid-work — usage limits, crashes, kills — and a dying session
cannot spare the tokens to write a handoff. It never needs to: every session
leaves a **black box** — card + work log, working tree, receipts, transcript —
written as a side effect at zero cost to the writer. You, the successor, pay
the reconstruction cost at your own rates, in your own harness, on your own
budget. Read it in cost order until you can state what was in flight, what was
proven, and what the next edit was going to be:
[references/black-box.md](references/black-box.md).

Signals that a pickup is what's being asked, even when unstated: a claimed
card with a stale lease, a dirty tree you didn't make, a fresh transcript
from another harness in this workspace. Reconstruct first, then route as
usual — the claim transfer, the finishing diff, and the commit belong to the
routed skill.

## Routing

Recommend one next skill. If the signal is mixed, name the missing evidence
rather than guess from vibes.

| Signal | Next |
|---|---|
| Shaped ticket, clean branch | `/deliver <ticket>` |
| Dirty branch, intended changes | `/deliver` (finish and land) |
| Dirty worktree, unclear ownership | Classify paths, then commit by concern or ask one scope question |
| Stale claim + predecessor's dirty tree | Read the black box, then route the reconstructed work (usually `/deliver`) |
| Unshaped idea, unclear acceptance | `/shape` |
| Empty or stale backlog | `/groom` |
| Open prioritized backlog, no active branch | `/groom` summary, then one pickup |
| Failure, broken gate, unclear root cause | `/diagnose` |
| Item already in verification | `/qa` or closeout before new delivery |
| Running surface needs proof | `/qa` |
| Finished work needing closeout | `/deliver` (Land it), then `/compound` if a reusable lesson |
| Human external blocker | Say the agent is blocked; do not invent process work |
| Readiness or profile question | `/qa` or the repo's readiness surface |
| "What happened / why does it matter" | `/orient --deep` or `/shape` |
| Skill or harness primitive change | `/harness-engineering` |

## Stay in lane

Orient reads; it never acts. Don't deliver, groom, refactor, reflect, debrief,
mine transcripts beyond the black-box tail, or mutate state. Don't label the
repo "ready" or "validated" — route that to the owning skill. Don't store
session memory; durable state lives in backlog, commits, and receipts. Don't
spin up provider lanes unless scope is broad, stale, or contested. Scoped
`AGENTS.md` governs — respect it.

## Verification

Editing this skill in the roster source repo:

```sh
cargo run --locked -p roster-cli -- check
```

Invoked in another repo, that command isn't required — acceptance is the
report's cited live evidence and a next move the operator can act on.
