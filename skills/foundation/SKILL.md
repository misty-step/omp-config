---
name: foundation
description: Reassess a project's purpose, backlog, and foundations from first principles, and recommend the simplest coherent way forward.
disable-model-invocation: true
---

# Foundation

Reconsider this project as a whole: what it should accomplish, whether that
aim is sound, and how best to build, change, deliver, and operate it.

If we were starting today, knowing what we now know, what would we build?
What would we deliberately not build? Then distinguish that destination
from the most sensible path out of the current system.

This is an investigation and design proposal, not an implementation pass.
Do not change project files, backlog records, or deployed state. Use
isolated experiments where they materially strengthen the assessment.

## Establish what deserves to exist

Understand the intended users, their problem, the promised outcome, and
the evidence that the product serves it. Treat the current vision,
documentation, and backlog as claims to examine, not proof of necessity.

Distinguish explicit obligations and operator-owned constraints from
assumptions, inherited choices, and implementation habits. Question any
of them, but do not silently discard real commitments.

Assess whether the backlog advances the right outcome. Identify work
that should disappear, be reframed, or wait, as well as missing work
that genuinely prevents progress. Missing product evidence is an
uncertainty to resolve, not permission to invent user needs. For a live
product, that evidence includes whether promised journeys actually happen,
not only whether the process is healthy.

## Find the simplest complete system

Reason from required behavior, data, invariants, and operating needs
rather than defending the current decomposition.

Look for unnecessary concepts, special cases, state, coupling,
representations, handoffs, and competing owners. Prefer designs that
remove the source of complexity, place responsibility clearly, and
expose small interfaces over deep, coherent implementations.

Consider product scope, architecture, stack, dependencies, tools, and
infrastructure together. A locally elegant module is not an improvement
if it makes its callers, developers, users, or operators carry the burden.

Consider materially different alternatives where warranted, including
doing less or using an existing capability. Compare them fairly with
keeping and improving the current design. Neither familiarity nor novelty
is sufficient justification.

Sunk effort is not a reason to preserve a bad design. Migration effort,
data safety, compatibility, and operational risk are real costs.

Separate a change of host from a change of database, identity, real-time, or
job-execution contract. Compare local, edge-native, and persistent Linux
execution where relevant; a hybrid must remove more work than its boundary adds.
Inspect current deployment evidence before treating old hosting declarations
as runtime authority or a separate local implementation as a completed cutover.

## Include the ability to change and operate it

Early in the assessment, identify whether meaningful verification of the core
outcome is possible. An absent or unreliable path is a foundational constraint
on development, not a reason to impose identical tooling on every repository.
Recommend the smallest missing capability; an explicitly commissioned
`verification-infrastructure` pass can create or repair it. This assessment
remains read-only.

Assess the foundations beyond source structure:

- Can a fresh agent discover and use repository-owned skills and runnable
  procedures to exercise important user journeys or consumer contracts,
  distinguish success from plausible failure, and clean up? A skill file,
  successful tool invocation, or historical receipt is not sufficient proof.
- Are prerequisites, representative data, isolated identities, and external
  service boundaries reproducible in an authorized development environment?
  Can an agent leave a private, synthetic-data preview that another device can
  inspect, then rebuild or safely retire the workspace? Do containers or other
  tools make this easier rather than add another interface to maintain?
- Do tests and linters catch consequential failures and precise recurring
  invariants, with live exercise where the claimed behavior requires it?
- Do local development and CI use coherent, repository-owned interfaces?
  Are builds, artifacts, environments, deployment, and recovery
  reproducible and appropriate to the project's stakes?
- Can an operator tell whether users are being served, diagnose failure,
  and recover? Do logs, metrics, traces, error reporting, uptime checks,
  and alerts support those decisions without unnecessary machinery or noise?
- Can we tell whether the product's promised journeys actually happen?
  Error reporting and uptime do not answer that. For session or party games,
  that usually means rooms form, play starts, and sessions complete. Prefer
  first-party events or existing system records over a second platform.
  Keep payloads free of player content and durable identifiers unless the
  product requires them. A private or local-only tool may need none of this.
- Do documentation and backlog preserve current intent, ownership,
  constraints, and consequential decisions without competing sources
  of truth?

Assess each area for this project. A capability may be unnecessary;
an unexamined capability is not verified. The objective is effective
development and operation, not completing an infrastructure checklist.

## Ground the judgment

Inspect the actual repository, relevant backlog, and available product
and operational evidence. Exercise important claims where feasible.
Consult current primary sources when a recommendation depends on facts
about an external technology.

Distinguish observations, inferences, preferences, and unknowns. State
what was not accessible or exercised. Investigate missing evidence when
available; ask focused questions when an answer would materially change
the recommendation.

Do not manufacture findings, replacement architectures, or new work to
make the assessment appear substantial. Keeping a sound foundation is
a valid conclusion.

## Return a coherent recommendation

Lead with the judgment: are we pursuing the right outcome, and are the
current foundations a sensible way to achieve it?

Describe the recommended product and system as a coherent whole, not
a collection of unrelated improvements. Make clear what to preserve,
remove, simplify, or replace—and why.

Support consequential recommendations with project-specific evidence,
alternatives, and tradeoffs. Explain the backlog implications and a
practical transition from the current state, including major risks.

Identify the decisions that belong to the operator and the smallest
useful investigations or experiments for unresolved questions. Explain
what evidence would change your recommendation.

Choose a presentation that makes the reasoning easy to inspect.
Prioritize consequential findings; do not fill a fixed report template.
