# Tests quality branch

Load this branch only when `/quality` selects `tests`. It governs the repo-owned automated test system: class selection and depth, suite rigor, flake control, timing budgets, and failure artifacts.

## Inventory

Enumerate every test framework and suite. Record each present class, runtime and duration, CI wiring, coverage and mutation tools, seed source, fixture root, and CI flake history. Record each absent surface as an explicit fact.

Use these tier names:

- **Fast:** pre-commit or pre-push.
- **Full:** merge.
- **Scheduled:** nightly or weekly, opt-in.

## Targets and probes

### Selection rules

Select a test class only when all three rules hold:

1. The repository demonstrates the failure mode that the class detects. Name the code, seam, or incident.
2. The class has a named falsifier: a concrete bug it catches that no cheaper selected class catches.
3. The class can run deterministically, or with seeded replayable randomness, in a named target tier.

Refuse a class that fails any rule. Record the failed rule and its evidence. Refusal is valid. Remove a class added only for coverage optics or template compliance.

A missing current gate is a wiring gap, not an automatic refusal, when an executed probe proves the class can meet its named target tier.

### Class targets

#### Unit

- **Detects:** Broken logic contracts at a function or module boundary.
- **Select when:** Logic-bearing code exists, almost always.
- **Refuse when:** Only pure plumbing exists, such as re-exports, type-only modules, or config threading.
- **Target:** Fast tier. Make core logic mutation-resistant. Assert observable contracts, boundaries, transitions, precedence, and real errors.

#### Integration

- **Detects:** Broken seams between repo-owned modules, storage, or services.
- **Select when:** The repository owns a seam that a unit test would mock away.
- **Refuse when:** Every seam is third-party. Use contract or replay tests at that boundary instead.
- **Target:** Exercise real internal seams. Mock external I/O only. Use fast or full tier according to duration.

#### End-to-end

- **Detects:** Broken user-visible flows across the wired system.
- **Select when:** A user-facing UI, API, or CLI exists.
- **Refuse when:** No user-visible surface exists, or an integration test already covers the same wiring.
- **Target:** Keep only the few highest-value paths in the full tier. Require failure artifacts: screenshots, video, or trace for UI; transcripts for API and CLI.

#### Property

- **Detects:** Invariant violations across a generated input space.
- **Select when:** Inputs have algebraic structure, such as parsers, serializers, codecs, normalizers, round-trips, or idempotent operations.
- **Refuse when:** No invariant exists beyond matching an example. Use a table-driven unit test instead.
- **Target:** Enable shrinking. Persist every failing case as a permanent regression fixture. Log and replay the seed.

#### Mutation

- **Detects:** Tests that execute code without defending it.
- **Select when:** Core logic exists and the suite must be trusted, especially for agent-authored suites.
- **Refuse when:** The suite is too young to gate. Run report-only first, then promote through the quality-gates ratchet path.
- **Target:** Run diff-scoped mutation in the gate, such as `cargo-mutants --in-diff`, Stryker incremental mode, or `mutmut`. Run full mutation on the scheduled tier. Treat every survivor as a finding.

#### Jitter

- **Detects:** Race conditions, ordering assumptions, and timeout brittleness in concurrent or async code.
- **Select when:** Concurrency, async scheduling, retries, or time-dependent logic exists.
- **Refuse when:** The code is strictly sequential.
- **Target:** Perturb delays and scheduling with randomized, logged seeds on the scheduled tier. Replay every failure from its seed. Treat a jitter failure as a bug, never as noise.

#### Performance

- **Detects:** Latency, throughput, or footprint regressions against a stated contract.
- **Select when:** A performance contract exists, or a regression would be user-visible.
- **Refuse when:** Nobody can state the threshold. A benchmark without a baseline and threshold is decoration; use [`verification-system-first`](../../../references/verification-system-first.md) for the threshold contract.
- **Target:** Fix the workload, commit the baseline and threshold, record a variance note, and archive raw output. Use the full or scheduled tier.

#### Torture (soak / stress)

- **Detects:** Leaks, resource exhaustion, degradation, and restart or recovery failures under sustained or extreme load.
- **Select when:** Long-running processes, connection or memory pools, or recovery paths exist.
- **Refuse when:** Short-lived batch code holds no accumulated state.
- **Target:** Use the scheduled tier only, never pre-merge. Bound duration and resources. State exit criteria before the run, such as no RSS or handle growth and recovery within a named bound. Store a metrics timeline and logs.

### Rigor probes

Apply these constraints to every selected class. One behavior belongs in one test. The test name states the expected behavior. Repository lint and typecheck gates apply to tests without weakening.

#### F.I.R.S.T. floor

- **Fast:** The fast-tier suite runs in seconds, or nobody runs it.
- **Independent:** Run any subset in any order and in parallel. No test consumes another test's state.
- **Repeatable:** Get the same result on any machine, at any time of day, offline.
- **Self-validating:** Pass or fail without human log reading.
- **Timely:** Land a new observable contract with its tests in the same change.

#### Determinism and seeds

Ban wall clocks, unseeded random values, live network calls, shared ports, shared mutable fixtures, and sleep-based synchronization inside tests.

Controlled randomness for property, jitter, or fuzz tests logs its seed on every run and replays from an environment variable or flag. Reproduce every failure from its artifact alone: exact command, seed, and fixture snapshot. Treat a failure that cannot be replayed as a finding.

#### Flake protocol

Use a CI rerun-on-red sweep to detect flakes. A pass on retry is flaky. Never blanket auto-retry to green; it hides the defect.

Treat a flaky test as a defect. Quarantine it in an explicit skipped-with-ticket list, keep that list as a shrink-only ratchet, and set a fix-or-delete deadline. A non-deterministic gate is not a gate.

#### Timing budgets

Commit a budget for each tier: seconds for fast, minutes for full, and a bounded duration for scheduled. Give every test a timeout. A hung test fails; it never hangs the suite.

Treat a budget breach as an audit finding. Reassign the test to a suitable tier or make it faster. Never delete the invariant.

## Evidence

Store all test evidence under `.evidence/quality/tests/`, or in the CI artifact store with its path recorded in the assessment. Keep the test-domain assessment at `.evidence/quality/tests/assessment.json` and `.evidence/quality/tests/assessment.md`.

On every failure, persist the exact command, seed, and logs. Also persist:

- Screenshots, video, or trace for UI end-to-end tests.
- Transcripts for API and CLI end-to-end tests.
- Mutation survivors for mutation tests.
- Raw output and the baseline for performance tests.
- A metrics timeline for torture tests.

Make every shipped defect a permanent fixture-backed regression test.

For each new or strengthened test, run a seeded-bug falsifier before declaring it protective. Introduce one concrete mutation or temporarily revert the fix. The test must fail. Restore the fix and rerun the test to pass. Record the mutation or reverted change, exact command, seed, exit code, and artifact path.

Record, for every selected or refused class, the selection rule and evidence. Record suite commands, durations against budgets, exit codes, seeds, artifacts, and flake disposition. Record each mutation or reverted-fix falsifier in the domain assessment.

## Leaf routes

Load the narrow method instead of reproducing its program:

| Need | Pointer |
|---|---|
| Gate tiers and placement | [`skill://ci`](../../ci/SKILL.md) |
| Diff-scoped test judgment and fix-vs-weaken authority (checks 1–8 on highest-risk contracts) | [`global/skills/review-tests/SKILL.md`](../../review-tests/SKILL.md) |
| Exploratory or live behavior verification by a fresh verifier | [`skill://verify-live`](../../verify-live/SKILL.md) |
| Live persona QA | [`skill://qa-users`](../../qa-users/SKILL.md) |
| Rendered design proof and design leaves | `quality` → `design` → `references/design.md` |

Keep lint, build, typecheck, and hook gates in the `toolchain` domain. Keep all live persona and exploratory behavior outside this branch.

## Domain completion

- In `--audit-only`, do not edit tests. Record class selection or refusal, rigor findings, budgets, flakes, and evidence.
- In `--remediate`, close accepted test findings without weakening an assertion, target, tier, or invariant. Apply the `review-tests` fix-vs-weaken authority.
- In `--verify`, run each affected suite twice from a clean state with disclosed seeds, then rerun each seeded-bug falsifier.
- Close a selected class only when its failure mode, cheaper-class comparison, deterministic execution, named tier, falsifier, and evidence are recorded.
- Leave residual gaps explicit when a class or probe is missing, refused, waived, or deferred.
