---
name: resilience
description: Prove one recovery invariant with the smallest bounded failure experiment.
disable-model-invocation: true
argument-hint: "[system, failure, and environment]"
---

# Resilience

Prove recovery, not disruption, with one bounded experiment on the owned
deployment substrate. Production fault injection is a human-owned action.

## Preflight

Read the accepted recovery invariant, target environment and artifact, release
checks, deployed identity, health signals, rollout controls, recovery procedure,
current incidents, and operating owner. Require green repository-owned gates,
no active incident, a known artifact, observable health, and a previously
proved recovery path. Start at the earliest missing prerequisite; use
`/foundation` to install it. Kubernetes or another orchestrator is optional.

## Experiment packet

State one steady condition and one falsifiable hypothesis: after a named fault,
the system detects it and recovers within a named bound. Specify the smallest
fault, target, artifact, environment, duration, blast radius, observer,
evidence, abort thresholds, recovery action, and incident owner.

Prefer local, staging, or canary environments. Production requires evidence that
lower environments cannot prove the real path and explicit operator approval of
the complete packet.

Keep authority narrow: CI diagnosis uses a normal branch and pull request;
release control deploys only the named candidate and performs one ordinary
rollback; experiment control injects only the accepted fault. Never weaken
checks. A fix-forward is a separate delivery and release.

## Exercise

Rehearse against the cheapest representative environment. Confirm that the
fault reaches the target, signals identify it, abort thresholds fire, recovery
restores the known identity, and no active fault remains.

Before a live run, recheck identity, steady condition, approval for production,
incident state, observer, and recovery readiness. Inject one fault and stop when
the steady condition returns, a threshold fires, blast radius is exceeded, or
the bound expires.

If recovery succeeds within the bound, stop injection and verify injector
inactivity, identity, health, state, and affected surfaces without invoking
fallback recovery. Otherwise stop injection, verify no active fault, run the
single accepted recovery action once, and verify restored identity, health, and
state. Keep hypothesis outcome separate from safety recovery.

On cleanup or recovery failure, stop automated mutation, preserve evidence, and
escalate to the operating owner.

## Report

Return the invariant, environment, artifact identity, fault, timeline, signals,
hypothesis outcome, recovery action, final health, evidence, and smallest
confirmed follow-up.
