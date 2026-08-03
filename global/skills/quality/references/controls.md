# Controls targets

## Targets

### Complete surface inventory

Inventory every row in this table. Classify each row as `present`, `recommended`, or
`not-applicable`, and record the authoritative path or command, trigger, tier,
enforcement owner, failure behavior, bypass route, and evidence.

| Domain | Required surfaces |
|---|---|
| Authority | Root instructions, manifests, lockfiles, generated authority, and policy ownership |
| Static quality | Formatting, syntax, warnings-as-errors lint, strict types, build or compile, architecture boundaries, dead code, and duplication |
| Tests | Unit, integration, contract, end-to-end or browser, property or fuzz, mutation, coverage or diff coverage, flakes, seeds, and failure artifacts |
| Hooks | Checked-in implementation, installer, effective `core.hooksPath`, foreign-hook chaining, commit and push latency, and the `--no-verify` backstop |
| CI | Workflows, repository-owned commands, required-check and branch-rule evidence, path-filter sentinels, timeouts, cancellation, and artifact retention |
| Secrets | Staged diff, outbound commits and messages, history, pull-request and release metadata, redaction, missing-tool and error behavior, and a pinned TruffleHog version |
| Security | SAST, dependency vulnerabilities, licenses, lock integrity, registry existence, provenance, signatures, and mutable action or image pins |
| Compatibility | API, schema, and migration compatibility; generated drift; and supported OS, runtime, and toolchain matrix |
| Delivery | Packaging, clean install, upgrade, rollback, release and deploy smoke checks, and live-verification ownership |
| Budgets | Performance, resources, binary or artifact size, gate duration, observability, and trend evidence |
| Agent resistance | Ignored warnings, type escapes, swallowed errors, stubs, dead scaffolding, gate or configuration tampering, and self-attestation |
| Reproducibility | Fresh clone and bootstrap, offline behavior, declared tools, cache independence, and deterministic or replayable randomness |

Search for checked-in but unwired hooks, folklore scripts, mutable pins,
fail-open scanners, local and CI drift, swallowed exit codes, exclusion growth,
threshold reductions, and controls that pass without exercising their oracle.

### Gate budgets and enforcement

- **Pre-commit:** target 2 seconds warm with a hard ceiling of 5 seconds. Keep it
  deterministic, offline, and staged or changed-file scoped. Run format, syntax,
  changed-file lint, forbidden-marker checks, and staged-diff secret scanning.
  Do not run installs, containers, network access, full builds, full typechecks,
  or broad suites.
- **Pre-push:** target 60 seconds warm with a hard ceiling of 120 seconds. Use
  one repository-owned command that is offline by default and cancellable. Run
  outbound secret and metadata scanning, range lint, affected typechecks and
  tests, lock integrity, and smoke checks. Never run an unbounded full suite.
- **CI or ship:** cover every evidenced applicable failure mode with explicit
  job timeouts, stale-run cancellation, required checks, and durable
  diagnostics. Re-run or subsume every local invariant in required CI.

## Probes

1. Run `python3 "${PI_CODING_AGENT_DIR:-$HOME/.omp/agent}/skills/quality/scripts/inventory-controls.py" REPO` for a deterministic negative-space inventory. Validate its claims against source.
2. Inspect effective hooks and branch enforcement, not only checked-in files.
   Confirm configured and effective hook paths, executable commit and push hooks,
   foreign-hook chaining, and the `--no-verify` backstop.
3. Benchmark each local gate with three warm runs. Record the median, machine
   context, and audited revision. Label every unmeasured duration `unknown`.
4. Trace each control to its trigger, enforcement owner, failure behavior,
   bypass route, and authoritative evidence.
5. Prove the audit leaves Git and external state unchanged by comparing status
   and other declared state before and after every read-only audit.

## Evidence

Store controls evidence under `.evidence/quality/controls/`. Keep an
applicability ledger with one row per required surface and these fields:
`surface | failure mode | control | tier | enforcement | duration | evidence | gap`.

Every recommendation records the demonstrated failure mode and evidence, the
exact repository-owned command or tool class, tier and latency, enforcement
point, seeded falsifier, hard-block, ratchet, or report rollout, false-positive
and maintenance cost, and why a cheaper tier is insufficient.

The assessment records the highest-risk uncovered failure modes, measured gate
map, prioritized recommendations, timing violations, bypasses, residual
unknowns, and the smallest safe implementation sequence.

## Safety

Keep inventory and audit probes read-only. Do not modify the repository, hooks,
trackers, or external state from an audit lane. Route accepted remediation to a
builder and preserve the audit transcript.

Keep hook implementations and gate configuration version-controlled. Install
local hooks reversibly, and preserve and chain foreign hook systems rather than
replacing them.

Use TruffleHog for secret scanning. Pin its CI version. Scan staged diffs and
outbound ranges locally, and scan history plus Git, pull-request, and release
metadata in CI. Fail closed when the scanner is missing or errors, and redact
matched values in reports.

## Leaf routes

- Route lint, build, type, and hook findings to `toolchain`.
- Route test depth findings to `tests`.
- Route CI placement and gate-tier findings to `/ci`.
- Route operational controls to `operations` or a `verifier` using `verify-live`.
