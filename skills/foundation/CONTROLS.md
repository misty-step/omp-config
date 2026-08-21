# Controls

Layer local feedback, hooks, CI, and runtime diagnosis. CI is authoritative
over the same owned commands the repository documents. Hooks check and name
the repair.

## Language

Prefer a statically checked language and the strictest practical checker
settings. Existing project language wins. New services, CLIs, and tools follow
organization language defaults.

Require explicit nullability, exhaustive states, distinct domain identifiers,
typed serialization boundaries, and checked errors. Represent domain data with
named types and schemas.

## Domain and data

One owner and one authoritative representation for each datum. Enforce
invariants in types and in the store. Names are model claims. Keep one
ubiquitous language across code, API, UI, telemetry, and operations.

## Tests

Assert outcomes, boundaries, invariants, transitions, precedence, and real
errors through the real contract. Each test goes red on a plausible defect.
Weight the portfolio toward integration through real contracts; add property
or fuzz coverage where parsers or core logic demand it. Quarantine flaky
tests with an owner immediately; fix or delete them fast. Keep the full gate
inside the repository's CI latency budget.

## Hooks

Commit the hook configuration. Provide an install or bootstrap path. Pre-commit
stays tight: format, lint, secrets, schema drift. Pre-push may add typecheck,
tests, and build. Prefer the project's existing hook runner.

## CI

From a clean checkout, run the repository-owned check, test, and build
commands. Required checks block merge. Pin toolchains and actions. Treat
warnings as failures. Caches are not part of correctness.

## Secrets and supply chain

Scan staged changes and CI. Scan history during the first Foundation pass when
the repository has none. Pin or pin-hash trusted CI actions. Least-privilege
tokens. Vulnerability checks have an owner.

## Diagnosis

Operated software needs structured logs, environment and release identity,
error capture with stack context, and filtered sensitive data.

Sentry is a candidate when failures occur outside a local process and current
evidence cannot reconstruct them. Proof: trigger a controlled error on a known
release and confirm source context, tags, routing, and redaction.

## Product evidence

User-facing products need a way to answer named product questions. Treat event
names as domain API. PostHog is a candidate for that job. Session replay and
identity collection need an explicit privacy decision.

## Feedback latency

Measure queue time, run time, and flake rate. Blacksmith is a candidate when
hosted CI is a measured bottleneck. Preserve portable workflow semantics.

## Agent context

`AGENTS.md` points at product authority and invariants. Add project Watchdog
priorities or a project skill only for a project-specific review risk or
repeated workflow.

## More lenses

When architecture, testing, security, or operations are in scope:

- Parnas: what decision does this module hide, and what change must not
  propagate?
- Hickey: which concerns are complected — identity and state, policy and
  mechanism, time and value?
- Dodds: cheapest test that fails on a plausible regression through the real
  contract?
- Saltzer and Schroeder: least privilege, fail-safe defaults, complete
  mediation, economy of mechanism.
- Operability: can one bad request be explained, tied to a release, and
  recovered from?

## Probes

Run the probe for each control in the lock. Each one goes red on a synthetic
defect, then the clean path passes.

1. Type error → local checker.
2. Lint or format violation → documented gate.
3. Synthetic secret → hook and CI.
4. Broken observable contract → test.
5. Schema or generated-code drift → consistency gate.
6. Fresh checkout → documented clone-to-green path.
7. Controlled runtime error → release-aware capture and redaction.

Remove the probes. Run the complete clean path.
