---
disable-model-invocation: true
name: audit-quality-controls
description: Exhaustively inventory and assess a repository's quality-control system without modifying it.
argument-hint: "[repo-path] [--revision REF]"
---

# /audit-quality-controls

Audit the complete quality-control system read-only. Be exhaustive about
surfaces and selective about recommendations: every proposed control names a
demonstrated failure mode.

## Audit contract

1. Record the repository, revision, dirty state, languages, frameworks, package
   managers, and root instructions. Run `scripts/inventory.py REPO` for a
   deterministic negative-space inventory; validate its claims against source.
2. Read `references/control-surfaces.md`. Mark every surface `present`,
   `recommended`, or `not-applicable` with path or command evidence. Inspect
   effective hooks and branch enforcement, not merely checked-in files.
3. Safely benchmark each local gate with three warm runs and report the median,
   machine context, and revision. Label unmeasured durations `unknown`.
4. Build an evidence ledger:
   `surface | failure mode | control | tier | enforcement | duration | evidence | gap`.
5. Produce the assessment contract from
   `global/references/quality-assessment.md`. Stop after assessment; modify no
   repository, hook, tracker, CI, or external state.

## Timing tiers

- **Pre-commit:** target 2 seconds warm, ceiling 5. Deterministic, offline, and
  staged/changed-file scoped: format, syntax, changed-file lint, forbidden
  markers, and staged-diff secret scanning. No installs, containers, network,
  full builds, full typechecks, or broad suites.
- **Pre-push:** target 60 seconds warm, ceiling 120. Offline by default,
  cancellable, and one repo-owned command: outbound secret and metadata scan,
  range lint, affected typecheck/tests, lock integrity, and smoke checks. Never
  run an unbounded full suite.
- **CI/ship:** exhaustive for every evidenced applicable failure mode, with
  explicit job timeouts, stale-run cancellation, required checks, and durable
  diagnostics. Re-run or subsume every local invariant in required CI.

Hook implementations and gate configuration are version-controlled. Local hook
activation is machine state and must be installed reversibly without replacing
foreign hook systems. Secret scanning uses TruffleHog, pins CI versions, scans
staged and outbound ranges locally, scans history and Git/PR metadata in CI,
fails closed on missing tools/errors, and redacts matched values.

## Recommendation contract

Every recommendation states the failure mode and evidence, exact repo-owned
command or tool class, tier and latency, enforcement point, seeded falsifier,
hard-block/ratchet/report rollout, false-positive and maintenance cost, and why
a cheaper tier is insufficient. Never weaken a threshold or bypass a gate to
obtain green.

Route implementation by pointer: lint/build/type/hook work to
`quality-toolchain`; test depth to `quality-tests`; CI placement to `/ci`;
operational controls to `quality-operations` or `verify-live`.

## Completion Gate

Follow the Shared Operating Spine (`Prove`; `Durable State and Closeout`). Add
the complete applicability ledger, highest-risk uncovered failure modes,
measured gate map, prioritized recommendations, timing violations, bypasses,
residual unknowns, and smallest safe implementation sequence. Prove the audit
left Git and external state unchanged.
