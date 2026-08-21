---
name: watch-deploy
description: Own the soak gate after a change merges and deploys — verify health every way available across the soak window before any new work starts. Use when this session's or this project's change has just reached a deployed environment.
---

# Watch Deploy

A deployment is not done when it goes out. It is done when health is proven
across the soak window, by you, before anything new starts.

## Claim

Identify the deploy under watch: repository, release or commit, environment,
rollback path. If no rollback exists — no revert plan, flag, or reverse
migration — say so first. That is a finding, not a formality.

## Gate

1. CI green on the merge commit; the deploy event observed (landmark
   evidence where the project runs it).
2. Health verified every way the project exposes: metrics, logs, traces,
   smoke probe against the real surface. If health is only answerable by
   SSH archaeology, that is a finding.
3. Hold the project's soak window. If none is defined, hold one deploy cycle
   or thirty minutes, state which, and record that the window was
   improvised.

## On red

Stop all new work. Present the failing signal, blast radius, and time-to-
effect with the rehearsed options — rollback, fix forward — and their
costs. Production mutation requires explicit operator or deployment-
controller authorization; observation does not (SE-04). After an
authorized corrective deploy, re-soak through the same gate.

## Close

Report what was watched, what was seen, the gate result, and rollback
status. Only then is the originating ticket done.
