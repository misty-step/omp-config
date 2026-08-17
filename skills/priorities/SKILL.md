---
name: priorities
description: Brief codebase and work-ledger state, then rank what to do next.
disable-model-invocation: true
---

# Priorities

Give the operator a tight brief of the live codebase, the live board, and
the next bets. Use current evidence. Mark an inference. Do not implement.

This is a _brief_, not a session status (`orient`) and not a foundation lock.

## 1. Name the ledger

Find the work tracker for this repository. Read `AGENTS.md`, `VISION.md`,
`.mcp.json`, and `.omp/mcp.json`. Prefer the tracker those files name. If
none name one, use the origin host's issue list (GitHub, GitLab). If none
exist, say the ledger is missing.

Completion criterion: one ledger and its query surface are named, or the
brief states that no ledger exists.

## 2. Read the codebase

From the clone, establish:

- branch, merge-base with the default branch, dirty paths you did not make;
- last shipped or merged change that still defines the running system;
- product job from `README`, `VISION`, or the live UI/CLI, not from tickets;
- gaps between that job and the code that actually runs.

Completion criterion: ship state, product job, and material drift are
stated from observed files or runtime, not from ticket titles.

## 3. Read the board

Query the ledger. Account for every item that is ready, in progress, or
blocked. Summarize refining and unscheduled work by count unless one item
is the obvious next bet. Treat a stale in-progress claim as a finding.

Completion criterion: every ready, in-progress, and blocked item is
named or grouped; a dispatch would not pick a superseded or empty epic.

## 4. Brief

Return only the brief. ASD-STE100. Short sentences. One term per concept.
Start with the conclusion.

- **Situation:** What the code does now, what the board thinks is next, and
  whether those agree. At most five sentences.
- **Priorities:** At most five items, highest first. For each: the identifier
  and title; what it is; why it is next; what it does to the design; the
  move (`do`, `wait`, or `drop`) and why.
- **Watch:** Stale claims, missing ledger, or a board that still points at a
  refused design. Omit this label when none apply.

Completion criterion: the operator can pick the next lane from the brief
alone. No implementation. No grooming unless the operator asks.
