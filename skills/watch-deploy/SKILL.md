---
name: watch-deploy
description: Own the soak gate after a change merges and deploys — verify health every way available across the soak window before any new work starts. Use when this session's or this project's change has just reached a deployed environment.
---

# Watch Deploy

A deployment is not done when it goes out. It is done when health is proven
across the soak window, by you, before anything new starts.

## Claim

Identify the deploy under watch: repository, exact release or artifact identity,
environment, rollback path, preauthorized rollback boundary, health signals,
and soak window. An absent rollback is a finding.

## Gate

1. Required CI is green on the exact merge revision and artifact.
2. The observed runtime identity matches the handed release identity.
3. Health is green through every exposed signal: metrics, logs, traces, and a
   smoke probe against the real surface.
4. Hold the project's soak window. If none is defined, hold one deploy cycle
   or thirty minutes. Record that the window was improvised.
5. Recheck runtime identity throughout the window. An unknown, mismatched, or
   changed identity invalidates the soak.

## On red

Stop all new work. Record the failing signal, runtime identity, blast radius,
and time-to-effect. Preserve the logs, traces, metrics, requests, and state
needed for diagnosis.

Immediately before recovery, observe runtime identity again. Select exactly one
action:

- use the declared rollback when identity matches, the path is available, and
  authorization is valid, unexpired, and inside the handed boundary;
- otherwise obtain fresh authorization for one repository-owned recovery.

Invoke the selected action once. Verify the resulting identity and every
handed initial check: health, smoke, migration readback, and changed user or
operator surfaces.

If the action fails, identity is unknown or wrong, or a check stays red, keep
incident ownership and the new-work freeze. Select and invoke the next
authorized repository-owned recovery, then repeat every restoration check.
After three failed recovery actions, stop further mutation. Keep monitoring,
preserve evidence, and escalate the recovery architecture. Do not close while a
check is red.

A fix-forward is a new revision. It must start again at `/release`; this skill
never deploys it. Re-soak each released or restored identity through this gate.

Block the originating release. Reproduce the failure through the smallest real
boundary. Keep that scenario red while tracing the source. After three failed
repairs, stop and challenge the architecture. Write a blameless postmortem when
impact, data risk, rollback, or operator intervention was material. Track
corrective actions with owners and proof. A failed release never retries
unchanged.

## Close

Report the release watched, each identity observation, each signal inspected,
observations across the full window, final runtime identity, rollback status,
and gate result. Close only when one unchanged release identity owns the full
green window.
