# Loop Readiness

OMP currently supports Mode A only. Mode B requires a named product with an active event plane for unattended schedules, webhooks, queues, or recurring workers.
Keep this work in Mode A until a future product is explicitly named. Keep the Mode A/Mode B boundary explicit in the product contract.

## Loop test

A workflow becomes a loop only when all conditions pass:

1. The work repeats.
2. A verifier decides progress or completion without worker self-judgment.
3. The runner reproduces the environment it changes or inspects.
4. Token, dollar, time, and blast-radius budgets absorb failed attempts.

If any condition fails, keep an ad-hoc operator session or a shaped ticket.

## Thirty-second check

- Trigger: event, schedule, PR-ready state, incident, or manual run.
- State file: durable progress between ticks.
- Gate: command, probe, or artifact that proves progress.
- Hard stops: maximum iterations, no-progress detection, and token/dollar budget.
- Review boundary: fresh verifier or human approval before irreversible action.

## Minimum loop

Use one automation, one skill or lane card, one state file, one gate, and one halt rule. Earn more only after a concrete failure.

## Handoff fields

- Owner repository and Mode B system; trigger and cadence; lane card path or embedded card; state file path.
- Verifier command; evidence or receipt path; human review boundary.
- Halt behavior for failure, no progress, and budget exhaustion.

## Reject by default

Reject loops for architecture rewrites, vague "keep improving" goals, one-off research, work without an automated verifier, or tasks where the worker grades its own output.
