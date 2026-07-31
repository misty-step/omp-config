# Test rigor constraints

These constraints bind every selected class. Audit against them in phase 3;
remediation lanes apply them in phase 5. The fix-vs-weaken rule in
`global/skills/review-tests/SKILL.md` binds every change to an existing test.

## F.I.R.S.T. floor

- Fast: the fast-tier suite runs in seconds, or nobody runs it.
- Independent: any subset, any order, in parallel; no test consumes another's
  state.
- Repeatable: same result on any machine, any time of day, offline.
- Self-validating: pass or fail without human log reading.
- Timely: a new observable contract lands with its tests in the same change.

One behavior per test; the name states the expected behavior. Tests are
first-class code: the repo's lint and typecheck gates apply to them
unweakened.

## Determinism and reproducibility

- Banned inside tests: wall clock, unseeded random, live network, shared
  ports, shared mutable fixtures, sleep-based synchronization.
- Controlled randomness (property, jitter, fuzz) logs its seed on every run
  and replays from an environment variable or flag.
- Every failure is reproducible from its artifact alone: exact command, seed,
  fixture snapshot. A failure that cannot be replayed is itself a finding.

## Flake protocol

- Detection: a CI rerun-on-red sweep marks pass-on-retry as flaky. Never
  blanket auto-retry to green — that hides the defect the retry skips.
- A flaky test is a defect: quarantine it explicitly in a skipped-with-ticket
  list, keep that list as a shrink-only ratchet, and set a fix-or-delete
  deadline.
- A non-deterministic gate is not a gate (`review-tests` check 7).

## Timing budgets

- Each tier has a committed budget: fast in seconds, full in minutes,
  scheduled bounded per run.
- Every test has a timeout; a hung test fails, never hangs the suite.
- A budget breach is an audit finding. The remedy is tier reassignment or a
  faster test, never deletion of the invariant.

## Failure artifacts

- On failure, persist the command, seed, and logs — plus screenshots, video,
  or trace for end-to-end; survivors for mutation; raw output and baseline
  for performance; the metrics timeline for torture.
- Artifacts land under `.evidence/` or the CI artifact store, with the path
  recorded in the assessment.
- Every shipped defect becomes a permanent fixture-backed regression test so
  it cannot return silently.
