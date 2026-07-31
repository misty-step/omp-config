# Test-class catalog

Apply the three selection rules from `SKILL.md` to each class below. Record
refusals in the assessment; refusal with reason is a valid outcome.

Tier vocabulary comes from `global/skills/ci/SKILL.md`: fast (pre-commit /
pre-push), full (merge), scheduled (nightly or weekly, opt-in).

## Unit

- Detects: broken logic contracts at a function or module boundary.
- Select when: the repo has logic-bearing code — almost always.
- Refuse when: only pure plumbing exists — re-exports, type-only modules,
  config threading (the `review-tests` non-goals).
- Target: fast tier; mutation-resistant on core logic; assertions on
  observable contracts, boundaries, transitions, precedence, and real errors.

## Integration

- Detects: broken seams between repo-owned modules, storage, or services.
- Select when: the repo owns a seam whose failure a unit test mocks away.
- Refuse when: every seam is third-party; use contract or replay tests at
  that boundary instead.
- Target: real internal seams; mock external I/O only; fast or full tier by
  duration.

## End-to-end

- Detects: broken user-visible flows across the wired system.
- Select when: a user-facing surface exists — UI, API, CLI.
- Refuse when: no user-visible surface exists, or an integration test already
  covers the same wiring.
- Target: few, highest-value paths; full tier; failure artifacts mandatory —
  screenshots, video, or trace for UI; transcripts for API and CLI.

## Property

- Detects: invariant violations across a generated input space.
- Select when: inputs have algebraic structure — parsers, serializers,
  codecs, normalizers, round-trips, idempotent operations.
- Refuse when: no invariant exists beyond "matches the example"; a
  table-driven unit test is honest and cheaper.
- Target: shrinking enabled; every failing case persisted as a permanent
  regression fixture; seed logged and replayable.

## Mutation

- Detects: tests that execute code without defending it.
- Select when: core logic exists and its suite must be trusted —
  agent-authored suites especially.
- Refuse when: the suite is too young to gate; run report-only first and
  promote by the quality-gates ratchet path.
- Target: diff-scoped in the gate (`cargo-mutants --in-diff`, Stryker
  incremental, `mutmut`); full runs scheduled; every survivor is a finding.

## Jitter

- Detects: race conditions, ordering assumptions, and timeout brittleness in
  concurrent or async code.
- Select when: the repo has concurrency, async scheduling, retries, or
  time-dependent logic.
- Refuse when: the code is strictly sequential.
- Target: randomized delay and scheduling perturbation with a logged seed;
  scheduled tier; every failure replayable from the seed; a jitter failure is
  a bug, never noise.

## Performance

- Detects: latency, throughput, or footprint regressions against a stated
  contract.
- Select when: a performance contract exists or a regression would be
  user-visible.
- Refuse when: nobody can state the threshold; a benchmark without a baseline
  and threshold is decoration
  (`global/references/verification-system-first.md`).
- Target: fixed workload, committed baseline, threshold, variance note;
  scheduled or full tier; raw output archived.

## Torture (soak / stress)

- Detects: leaks, resource exhaustion, degradation, and restart or recovery
  failures under sustained or extreme load.
- Select when: long-running processes, connection or memory pools, or
  recovery paths exist.
- Refuse when: short-lived batch code holds no accumulated state.
- Target: scheduled tier only, never pre-merge; bounded duration and
  resources; exit criteria stated up front — for example, no RSS or handle
  growth, recovery within a named bound; artifacts: metrics timeline plus
  logs.
