---
name: verification-infrastructure
description: Create or repair a repository's runnable verification capability and agent-facing skill, reusing existing tools and preserving product ownership.
disable-model-invocation: true
argument-hint: "[optional repository, journeys, or constraints]"
---

# Verification infrastructure

Make it possible for a fresh agent to establish whether meaningful product
behavior works, without rediscovering setup, identities, navigation, and the
correctness criteria in every conversation. Create what is missing; reconcile
what already exists. A working capability is the outcome, not a generated
skill file or a standard directory tree.

Work in the commissioned repository and scope. This is capability authoring,
not an automatic portfolio rollout, recurring job, or grant to operate a shared
backend. Ordinary feature work should use and maintain the resulting repository
skill rather than rerun this authoring process.

## Start from the product and existing machinery

Identify the important user journeys or consumer contracts, the intended
outcomes, and the constraints. Separate observed facts from hypotheses. Resolve
consequential uncertainty with the smallest useful experiment rather than a
large speculative design or an exhaustive feature catalog.

Inspect existing repository skills, development commands, fixtures, checks,
CI, and operational documentation before designing anything. Preserve useful
names and interfaces. A specialized gameplay skill or self-contained smoke
command may already provide most of the capability. Link and complete it;
do not wrap a working command just to impose a common spelling or schema.

Bespoke means product knowledge, not bespoke machinery. A library may need an
executable consumer example; a CLI needs its real command behavior; a desktop
application needs the actual surface. Do not create a browser application,
container stack, or test suite for a repository that does not need one.

## Make the runtime reproducible and bounded

Reuse repository-owned setup across local development, CI, and an approved
remote workspace where practical. Establish prerequisites, exact source and
artifact identity, representative data, service readiness, and external-service
boundaries. Never substitute fake product behavior for a missing real backend
or treat a historical receipt as current readiness.

Choose existing working infrastructure first. Worktrees isolate source;
containers package dependencies and services; VMs provide a machine boundary.
They do not grant credentials or make arbitrary candidate code safe. Read the
relevant infrastructure skill and current vendor documentation before operating
it, including `skill://using-exe-dev` for exe.dev. Do not modify vendored skills
to encode product-specific behavior.

Before provisioning, transfer, sharing, or new recurring execution, resolve the
account, inputs, capabilities, spend, exposure, and lifetime. Keep production
write authority out of ordinary verification. Hidden integration credentials
still grant API authority; copied tags, auto-attached integrations, scheduled
jobs, and persistent state need deliberate ownership when cloning a workspace.

Prefer browser and application co-location for a first remote exercise. A human
preview is a separate routing and authentication contract: browser-facing API
origins, realtime connections, cookies, and dev-server origin restrictions must
work from the reviewer's device. A private frontend URL alone proves none of
that. Do not make a service public or weaken an existing guard to obtain proof.

Give each run its required isolated application state and identities. Different
tabs are not necessarily different users, and isolated browser contexts do not
isolate shared server-side accounts. Name the owner and teardown behavior of
processes, browsers, containers, data, and any retained preview. Preserve
unrelated resources; distinguish stopping services from destructive reset.

## Expose behavior and its correctness criteria

Use the current harness's native interaction and inspection tools where they
fit, and preserve repository-pinned Agent Browser, Playwright, or other existing
workflows. Do not install several overlapping browser stacks by default. Hosted
browser infrastructure is an optional capability with its own connectivity,
credential, retention, and lifecycle requirements, not a verification oracle.

Build a small helper only when it removes recurring application-specific work:
preparing fixtures, selecting the correct runtime, establishing a difficult
state, or waiting for an observable application condition. Keep logic with its
owning product. Reuse supported APIs for setup and inspection, but do not replace
rendered user interaction with backend mutations when the claim concerns the UI.

Make recurring helpers composable and discoverable through their existing CLI
or API conventions. Give failures actionable diagnostics, bound waits, report
machine-readable results when a consumer needs them, and provide inspection or
dry-run for consequential operations where useful. A dry-run is not permission
to perform the operation.

The repository skill should be a thin, discoverable entry point in its existing
skill convention, normally `.agents/skills/<project-specific-name>/SKILL.md`.
Keep a sufficient existing skill instead of generating a competing one. Load
journey details on demand and link current commands, fixtures, and documentation
rather than copying their implementation or ephemeral accessibility references.
For supported journeys, make these questions easy to answer:

- What user or consumer outcome does this exercise establish, and when is it
  relevant rather than an unnecessary full-suite run?
- What target, prerequisites, data, identities, and authority does it require?
- How can an agent reach and exercise the behavior through the intended surface?
- Which observable postconditions distinguish success from plausible failure,
  including persistence, rejection, recovery, or timing when consequential?
- Where can it inspect meaningful state and collect appropriate evidence?
- What are the limitations, failure recovery, and owned cleanup operations?

Controllability, observability, and correctness criteria are separate needs.
Screenshots, agent self-reports, schema-valid receipts, and passing unit tests
are not interchangeable proof. Use deterministic assertions for stable contracts
and live interaction where the claim requires it; neither replaces the other.
Do not introduce a universal receipt protocol when the repository or execution
system already owns one.

## Prove the capability, including discovery

For a new or materially repaired executable path, exercise the documented setup,
behavior, inspection, and teardown from a fresh authorized state. Use the actual
product and repository-owned checks. Verify that the intended agent can discover
and use the skill without unpublished conversation context. Explicit-resource
runners may disable ambient skill loading: verify their approved composition
path rather than assuming that a global installation or file's existence is
sufficient. Do not broaden a runner's authority to make discovery convenient.

When adding a correctness check, choose a plausible failure it must detect and
establish that the check rejects it in an isolated exercise where practical.
Keep a regression test when it protects a real uncertain contract, not to test
skill wording or manufacture coverage. Reuse sound existing evidence and checks.
Prose-only maintenance needs meaning, reference, and relevant discovery checks;
it does not by itself justify model evaluations or an application smoke run.

Tie evidence to the actual source, run, target, and exercised surface. Inspect
results rather than trusting process exit or an agent's completion message.
Missing prerequisites, skipped exercises, stale artifacts, unsupported surfaces,
and unknown outcomes must remain explicit; none is a pass. Sanitize evidence
before sharing, and keep per-run artifacts in approved storage rather than Git
by default. A local test or emulated device does not prove a hosted deployment
or physical hardware.

Finish all reachable scoped work if a prerequisite is unavailable. Explain the
precise missing capability or authority and what remains unverified; do not
install a fake fallback, mark an unexercised path complete, or expand the task.

## Keep the knowledge with the change

The product owns its skill, fixtures, helpers, and reusable journey knowledge.
Changes to setup, identity, navigation, behavior, or cleanup update the affected
verification path in the same change. Keep commands authoritative and prose
small; preserve existing ownership instead of regenerating accurate references.

Use existing CI to exercise meaningful repository checks and catch deterministic
drift. Reference integrity is useful hygiene, not proof of semantic freshness.
External-service or tool drift may justify a bounded fresh-environment review,
but a separately authorized execution system owns its trigger, capabilities,
resources, and lifetime. This skill does not install that scheduler or create
an automatic backlog.

Repository onboarding should establish a usable capability, not merely a skill
filename. Wider adoption needs an explicit repository scope. `foundation`
identifies missing or unreliable verification as a development constraint and
recommends the smallest repair; it remains a read-only assessment.

Return the canonical entry points, what was preserved or changed, observed
verification and cleanup, and remaining limits. Put reusable procedures in the
repository and change-specific conclusions in its existing work record. Judge
the result by less rediscovery, fewer human interventions, and better detection
of real failures, not generated files, recorded videos, or PR volume.
