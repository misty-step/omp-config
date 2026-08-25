---
name: release
description: Merge and deploy one review-ready pull request, verify the exact release, and rollback on red.
disable-model-invocation: true
argument-hint: "[pull request]"
---

# Release

One review-ready pull request. Merge, deploy, verify, then hand off the soak.
Explicit invocation authorizes the declared repository rollback when release
verification fails. It does not authorize a different production mutation.

## 1. Gate

Proceed only when all conditions hold:

- the operator explicitly requested this release;
- the shaped spec or accepted intent is linked;
- required CI passes on the exact pull-request head, whose identity is recorded;
- required human approval exists;
- no blocker or accepted repair remains;
- each observable claim has evidence that opens directly from the pull request
  or its attached packet record; local paths and hashes do not satisfy this gate;
- the target environment has a repository-owned deploy path and initial
  checks;
- the runtime can report the deployed revision or artifact identity;
- rehearsal evidence proves the declared rollback path can restore health.
- the protected merge path rejects a changed head;
- automatic deployment cannot start before required post-merge CI passes.

A failed condition blocks the release before mutation.

Completion criterion: Every gate is green on the exact head.

## 2. Merge

Confirm the pull-request head still equals the gated head. Merge only that head
through the protected path. Verify the merge result contains exactly the
reviewed change. Record the immutable merge revision and built artifact.

Wait for all required CI on that merge revision and artifact. A failed or
missing check blocks deployment and marks the release blocked. Preserve the
failure evidence. Route the revert or corrective change through the protected
path. A corrected revision starts again at Gate.

Completion criterion: The merge contains the gated change, its artifact maps to
the merge revision, and required post-merge CI is green.

## 3. Deploy

Deploy that recorded artifact through the repository-owned release path.
Observe the deployment event and runtime identity.

A matching identity proceeds to Verify. Unknown, stale, or mismatched identity
is red and enters Roll back on red. That step selects one authorized recovery
action; this step does not mutate production again.

Completion criterion: Production reports the exact recorded artifact identity.

## 4. Verify

Run every repository-owned initial check against the deployed release:
health, smoke path, migration readback, and the changed user or operator
surface. Capture evidence through `skill://evidence-packet`.

If every check is green, hand `skill://watch-deploy` the repository,
environment, exact release and artifact identity, rollback path, preauthorized
rollback boundary, authorization lifetime, health check, smoke path, migration
readback, changed user or operator surface checks, production signals, and soak
window. Rollback authorization expires when identity changes or the soak
window closes.

Completion criterion: Initial production behavior is green and the soak owner
has the complete watch contract.

## 5. Roll back on red

Stop new work. Snapshot or pin volatile logs, traces, requests, metrics, and
state before recovery, without delaying restoration.

Immediately:

1. state the failing signal, first bad release, blast radius, and customer or
   operator effect;
2. mark the release blocked and link the incident to the originating work;
3. preserve the full diagnostic set;
4. assign the root-cause reproduction and investigation;
5. record the postmortem obligation when impact, data risk, rollback, or
   operator intervention was material;
6. track every corrective action with an owner and proof.

Observe the failing runtime identity. Select exactly one recovery action:

- use the declared rollback when identity matches the recorded artifact and
  its preauthorization remains valid;
- otherwise obtain fresh authorization for one repository-owned recovery.

Invoke the selected action once. Observe the resulting runtime identity.
Repeat every applicable initial check: health, smoke path, migration readback,
and the changed user or operator surface. Capture the failed and restored
states.

If the action fails, identity is unknown or wrong, or any restoration check
stays red, keep incident ownership and the new-work freeze. Select and invoke
the next authorized repository-owned recovery, then repeat the full checks.
After three failed recovery actions, stop further mutation. Keep monitoring,
preserve evidence, and escalate the recovery architecture.

Continue root-cause work whether restoration succeeds or remains red. Keep the
smallest real reproduction red while tracing the source. After three failed
repairs, stop and challenge the architecture.

Do not retry the same release. A corrected revision starts again at Gate.

Completion criterion: Healthy runtime is restored, or mutation stopped after
three failed recovery actions with an active incident, freeze, and monitoring.
In both states, the failed release is blocked, evidence is preserved, and
investigation, postmortem, and corrective actions have owners.