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
uncertainty to resolve, not permission to invent user needs.

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

## Include the ability to change and operate it

Assess the foundations beyond source structure:

- Can a developer run the meaningful application end to end locally and
  in an isolated development environment, with realistic data and clear
  external-service boundaries? Do containers or other tooling actually
  make that reproducible, inspectable, and easy to reset?
- Can important user journeys be exercised and inspected, rather than
  inferred from passing unit tests? Are tests and linters catching
  consequential failures and precise recurring invariants?
- Do local development and CI use coherent, repository-owned interfaces?
  Are builds, artifacts, environments, deployment, and recovery
  reproducible and appropriate to the project's stakes?
- Can an operator tell whether users are being served, diagnose failure,
  and recover? Do logs, metrics, traces, monitoring, and alerts support
  those decisions without unnecessary machinery or noise?
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
