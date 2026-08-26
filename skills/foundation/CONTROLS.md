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

## Context budget

An agent works reliably on code it can hold whole. The budget applies to the
**irreducibly atomic module**: the largest unit that must be understood
together because its parts share invariants (a proof kernel, a compiler core,
a schema plus its owner). A repository may be any size; each atomic module
packs inside a declared token budget. Default 100k tokens — roughly half a
frontier context window, leaving the other half for the task.

Measure with `repomix --include "<module>/**" --token-count-tree` for the
coverage-style view, and gate in CI with:

```sh
repomix --include "<module>/**" --no-file-summary --no-directory-structure \
  --quiet --token-budget <N> -o /dev/null
```

Non-zero exit on overflow. The gate counts the packed output, not raw source;
the two flags drop ~400 tokens of pack boilerplate so the count tracks the
module. Declare each module root and budget in one committed file the gate
reads.

A module over budget is a design finding, not a formatting problem. Respond in
order: delete dead weight; split along an existing seam into isolated modules
behind a small stable interface; only then raise the budget, with a recorded
reason. Enforce the resulting boundaries with the stack's own tool:
dependency-cruiser or Nx boundaries (JS/TS), import-linter (Python), ArchUnit
(JVM), `internal/` packages (Go), crates (Rust). A "module" whose boundary is
not enforced is one refactor away from re-merging.

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

Gate expensive matrices, live evals, and external-provider runs with one cheap
end-to-end smoke. One deterministic fixture or case must cross setup,
environment and output propagation, scoring or aggregation, schema and evidence
validation, and artifact publication. Fan-out starts only after this path passes.

## Local run and fixtures

Own one deterministic start command for each runnable application. Keep
sanitized fixtures or seed data in the repository. The command must create the
same topology and wiring that production uses, except for documented local
substitutes. Startup errors name the missing dependency or repair.

## Public smoke

Own one executable smoke path through the public interface. Use representative
fixtures. Assert the returned payload, rendered output, stored state, or
operator signal. A process start or open port is not product proof.

## Merge and release

Protect the default branch. Require the repository-owned checks on the exact
head and post-merge artifact. Deploy only an immutable merged revision. The
runtime reports that revision or artifact identity.

Own a health check and rollback command. Rehearse rollback in a safe
environment before production release. The rehearsal verifies restored
identity, health, smoke behavior, migration readback, and changed surfaces.

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
8. Missing or malformed local fixture → start command fails with the repair;
   restored fixture → application starts with expected state.
9. Broken public behavior → smoke path fails on the result; restored behavior
   → smoke passes.
10. Disposable failing required check → protected merge is blocked; restored
    check → the disposable change becomes mergeable.
11. Safe-environment bad release → health or smoke goes red; repository
    rollback → prior identity and every restoration check pass.
12. Budget lowered below the module's measured tokens → gate exits non-zero;
    restored budget → gate passes. A synthetic cross-boundary import → the
    boundary tool fails; removed → it passes.

Remove the probes. Run the complete clean path.
