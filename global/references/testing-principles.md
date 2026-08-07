# Testing principles

A test defends one observable behavior. Use this reference when you write a
test, expand a suite, or judge test quality in any repository and any language.
Skills point here instead of restating the rules. This file is reference, not
a scripted passage; only the falsifier loop below is an ordered procedure.

## A test defends a contract

A passing suite proves nothing by itself. A test is protective only when a
seeded defect makes it fail and the restored behavior makes it pass again.

Measure test quality by the defects the suite would catch. Do not measure it
by assertion count, line coverage, or suite size.

## Write one journey per test

Write each test like a manual tester's script. Give one explicit setup, then
perform the actions and assertions that validate the whole journey.

Multiple related assertions in one test are a feature, not a smell. Do not
split a single journey into many tiny tests just to satisfy one assertion per
test.

Assert intermediate states inside the broader workflow that causes them. Do
not add isolated tests that only check an incidental loading or transition
state.

One journey is one behavior. The phrase `one behavior per test` means one
journey, never one assertion.

## State the setup explicitly

Put the setup inside each test. Do not hide setup in shared hooks such as
`beforeEach` or `afterEach`.

Build helpers that return ready-to-run objects, such as factories. Do not
build globals that tests consume by convention.

If the next assertion depends on the same object, request, or response, keep
it in the same test. Do not share mutable state across test cases.

## Keep a fresh slate

Start each test with clean state. A framework default that resets mocks for
the whole run is good; do not rely on leftover state from a prior case.

Mock external I/O only: network, filesystem, clock, third-party SDK. Never
mock a module or class the repository owns.

Assert results through the public contract. Never assert internal structure,
internal call counts, or implementation-shaped snapshots.

Guard test output. Make unexpected warnings and errors fail the test. Silence
known noise only through an exact allowlist, and assert what you silenced.
Never silence output with a blanket stub.

## Choose the lightest falsifier

Choose the cheapest test class that can falsify the behavior. A class earns
its place when it catches a concrete bug that no cheaper class catches. Select
a class only when three rules hold:

1. The repository demonstrates the failure mode the class detects.
2. The class has a named falsifier: a concrete bug it catches.
3. The class runs deterministically in a named target tier.

Refuse a class that fails any rule. Removing a class added only for coverage
optics is valid.

| Class | Detects | Select when | Refuse when | Tier |
|---|---|---|---|---|
| Unit | Broken logic contract at a function or module boundary | Logic-bearing code exists | Only re-exports, type-only modules, or config threading | Fast |
| Integration | Broken seam between repository-owned modules, storage, or services | The repository owns a seam that a unit test would mock away | Every seam is third-party | Fast or full |
| End-to-end | Broken user-visible flow across the wired system | A user-facing UI, API, or CLI exists | No user surface exists, or integration already covers the wiring | Full |
| Property | Invariant violation across a generated input space | Inputs have algebraic structure, such as parsers, serializers, codecs, or round-trips | No invariant exists beyond matching an example | Full or scheduled |

The heavy classes live in the `quality` program. Its `tests` branch states
when mutation, jitter, performance, and torture tests earn a tier
(`global/skills/quality/references/tests.md`).

## Stay deterministic and offline

Get the same result on any machine, at any time, offline. Ban wall clocks,
unseeded random values, live network calls, shared ports, shared mutable
fixtures, and sleep-based synchronization.

Where a test needs randomness, log the seed and replay from that seed.

## Assert behavior, not copy

Assert structured output, user-visible outcomes, or stable public contracts.
Never assert incidental prose such as descriptions, tool names, usage hints,
warnings, or configuration strings. If the behavior matters, test the
behavior, not the text that describes it.

Let the type system prove what it already guarantees. Do not write a test for
a guarantee the compiler or static type checker enforces.

## Clean up only what you own

Release external resources such as files, sockets, and servers. Use a dispose
construct only when real cleanup exists. Do not add disposal ceremony when
nothing needs release.

## Keep the bar high and the suite fast

Fewer high-value tests beat many low-value tests. Add a regression test for a
defect only when the flow matters enough to justify the maintenance cost. Do
not add a regression test for a defect that is unlikely to recur.

Keep the fast tier in seconds, or nobody runs it. Give a slow or expensive
check a named tier: fast, full, or scheduled.

Treat a flaky test as a defect. Quarantine it in an explicit skip-with-ticket
list that only shrinks. Never blanket auto-retry a suite to green; it hides
the defect.

## Name the behavior

State the expected behavior in the test name, such as `auth handler returns
400 for invalid JSON`. Prefer flat test files over deep nesting.

## The falsifier loop

Before you declare a test protective, prove the loop closes:

1. Introduce one concrete defect into the changed behavior. Flip a boundary,
   remove a guard, or revert the fix.
2. Run the test. It must fail on the defect.
3. Restore the defect. The test must pass again. Record the defect, command,
   and result.

Complete when the test fails on the defect and passes after the restore.

## Multi-agent protocols

When the system under test is a gate, lifecycle, or multi-agent workflow, also
apply `global/references/process-adversarial-testing.md`. Defend illegal
transitions and multi-run invariants, not only a single happy path.

## Sources

Adapted from Kent C. Dodds, `kody`, `docs/contributing/testing-principles.md`,
GitHub, retrieved 2026-08. The style follows
`global/skills/comms/references/ste.md` and
`global/external/mattpocock-skills/writing-for-agents/SKILL.md`.
