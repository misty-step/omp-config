---
name: resilience
description: Prove one recovery invariant with the smallest bounded failure experiment.
disable-model-invocation: true
argument-hint: "[system, failure, and environment]"
---

# Resilience

Prove recovery, not disruption. Use the system's owned deployment substrate and
run one bounded experiment. Production fault injection is a human-owned choice.

## Gate

Read the accepted recovery invariant, target environment, target artifact's
release checks, deployed identity, health signals, rollout controls, rollback or
recovery procedure, current incidents, and operating owner.

Require the target artifact's owned release checks and repository-owned CI to be
green. Require no active incidents for the target. Require an owned delivery path
with a known artifact, observable health, and a previously proved recovery action.
Start at the earliest missing prerequisite and return that control gap; use
`/foundation` to install it before an experiment. Treat Kubernetes or another
orchestrator as an implementation choice, never a prerequisite.

Done when the system can detect the named failure and restore a known healthy
identity through an owned path.

## Design

State one measurable steady condition and one hypothesis: when a named fault
occurs, the system detects it and recovers within a named bound. Define the
smallest fault, exact target and artifact, environment, duration, maximum blast
radius, observer, evidence sources, abort thresholds, recovery action, and
incident owner.

Prefer a local, staging, or canary target that can falsify the hypothesis.
Production requires evidence that a lower environment cannot prove the real
recovery path and explicit Operator approval of the complete experiment packet.

Assign narrow agent authority:

- CI diagnosis may repair code only through a normal branch and pull request;
- release control may deploy only the candidate artifact to the target
  environment named in the approved experiment packet and perform one ordinary
  repository-owned rollback;
- experiment control may inject only the accepted fault and must recover at the
  first abort threshold.

A fix-forward is a separate accepted delivery and release. Agents preserve
failure evidence and never weaken checks to make a run green.

Done when every action, signal, bound, owner, and recovery transition is explicit
and the Operator has approved any production effect.

## Rehearse

Run the fault and recovery path against the cheapest representative environment.
Confirm that injection reaches the intended target, signals identify the fault,
abort thresholds fire, recovery restores the known identity, and the experiment
leaves no active fault.

Done when the mechanism and recovery path work without widening the accepted
blast radius.

## Run

Immediately recheck artifact identity, steady condition, operator approval for
production, clear incident state, observer availability, and recovery readiness.
If any preflight check fails, stop immediately without injecting and report the
blocker.

Inject one accepted fault. Watch until the steady condition returns, an abort
threshold fires, the maximum blast radius is exceeded, or the time bound
expires.
If the steady condition returns within the bound, mark the hypothesis proved,
stop injection, verify the injector is inactive and leaves no active fault, and
verify identity, health, state, and affected surfaces without invoking the
fallback recovery action. On an abort, blast radius breach, or timeout, mark
the hypothesis falsified, stop injection, verify the injector is inactive and
leaves no active fault, run the single accepted recovery action once, and
verify the restored identity, health, and state.

If cleanup or recovery verification fails, stop all automated mutation
immediately, preserve evidence, and escalate to the operating owner. Keep
hypothesis outcome separate from safety recovery.
Do not expand the fault, target, duration, or hypothesis during the run.

Done when the hypothesis has one recorded outcome, no active fault remains, and
the system is healthy on a known identity.

## Report

Return the invariant, environment, artifact identity, fault, timeline, signals,
hypothesis outcome, safety recovery action if used, final health, evidence, and
the smallest confirmed follow-up. A repair enters the normal trusted work
record; it does not continue inside the experiment.
