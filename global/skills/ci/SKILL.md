---
disable-model-invocation: true
name: ci
description: |
  Audit, design, and run repo-owned CI gates. Use a host-agnostic contract
  across local and hosted runners. Trigger: /ci, /gates.
argument-hint: "[--audit-only|--run-only]"
---

# /ci

Get confidence in correctness without adding provider or Docker cost to local work.

The harness source repo (`~/Development/omp-config`) uses `bin/check` for config-contract validation over `global/`.
Run it, then run `bin/install` after you change harness primitives.
This is harness plumbing.
Do not apply it as a framework in consumer repos.


In a consumer repo, read the root instructions, manifests, CI workflows, hook config, and shipped scripts.
Strengthen the repo-owned gate.
This skill gives CI judgment.
The consumer repo owns the implementation.
Use the standing quality floor in `global/references/quality-gates.md` for gate scope.
Read `references/host-agnostic-ci.md` for CI architecture and Dagger tradeoffs.


Use two gate tiers in consumer repos unless live evidence proves one gate is strong and fast.

- **Fast local gate** (pre-commit/pre-push): deterministic checks that agents can run during amend/push cycles — formatting, changed-path lint, typecheck, focused or changed tests, shell syntax, local-ticket bans, cheap secret scans.
- **Full ship gate** (PR/main/deploy/`ship-check`): expensive Docker, Dagger, browser, network, mutation, provider, and full-coverage checks.

Move a check out of pre-push only when the full gate still requires the same invariant.
Give a path-filtered required check a sentinel/split-check design.
Otherwise, skipped workflows remain pending.


## Modes

- Default: audit the gate surface, fix mechanical gaps, then run the repo-owned
  gate.
- `--audit-only`: audit report and gap proposals; do not run gates.
- `--run-only`: skip audit, drive the repo-owned gate green.

## Stance

1. **Repo-owned contract first.** Name a command, script, Dagger function, or build target that the repository owns.
   Hosted providers call it.
   They do not define it.
   Run the same contract locally and on every runner without provider-specific rewrites.
2. **Fast enough to use.** Treat a default local gate that takes many minutes for harness/docs changes as a design failure.
   Keep expensive, networked, mutation, browser, and provider checks opt-in or path-scoped.
   When a behavioral gate needs a supported third-party API, prefer an `emulate.dev`-backed local/CI lane over weakening it, hand-written mocks, or live sandboxes.
   Keep truly networked checks in the full gate only when real provider behavior is the point (https://emulate.dev/docs).
3. **Dagger earns its place.** Keep Dagger when portability, containerized dependencies, caching, service orchestration, or traceability outweighs its startup/debug cost.
   Do not wrap ordinary lint/typecheck/test/build in Dagger for the inner loop.
4. **No quality lowering.** Removing, splitting, or moving a check does not permit you to drop the invariant.
   Preserve it in the fast, full, or ship gate.
5. **Act, do not propose.** Apply mechanical strengthenings directly.
   Escalate only when the choice concerns product scope, not CI plumbing.
6. **Fix-until-green on self-healable failures.** Fix formatting drift, stale generated docs/index, and trivial lints.
   Diagnose logic failures precisely.
7. **Security floor is part of CI.** Scan source, generated artifacts, logs, and Git/PR metadata for secret leaks.
   Include commit subjects/bodies, PR titles/bodies, release notes, and agent summaries in scope.
   Redact matched values in reports.
   Prefer server-side push protection or pre-receive hooks.
   Otherwise, use repo hooks and CI.
8. **Reports are product.** Emit reviewable artifacts that later agents can use without chat context.
   Include a run digest, test/coverage reports, mutation or fuzz survivors, performance deltas, security findings, artifact checksums, and residual unverified paths.


## Delegation Judgment

Delegate according to the Shared Operating Spine (Act).
Each lane states its responsibilities, context boundary, output evidence, and lead verification.
Limit direct work to mechanical repair and emergency preservation.
The lead owns synthesis.


## Audit

Check the live gate surface:

- omp-config: `bin/check` passes and `bin/install` has been run.
- Consumer repos: identify the repo-owned gate and apply the same security floor.
  Confirm that local hooks run the fast gate, not the full ship gate.
  Keep the full gate required at merge/deploy.
  Run the full gate locally with an explicit command before marking a PR ready.
  Cancel stale PR runs in CI, but keep mid-release deploys running.
  Keep reports durable enough for later diagnosis.
- Secret scanning covers committed content and metadata outside the working tree.
  Scan the commit message file, outbound commit range, PR title/body, and release text.
  Redact matched values.


## Run

Run the repo-owned gate.
Use `bin/check`, then `bin/install`, for omp-config.
Use the contract from the audit for a consumer repo.
If a consumer repo has no gate, record a `high` finding.
Design the smallest native gate before you call CI meaningful.
If red, fix deterministic generated drift.
Run focused tests for the failing module.
Re-run the aggregate.
Stop after three self-heal attempts per gate.
Report the exact failing command, path, and likely cause.


## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract.
`/ci` adds:

- **Audit:** gaps found, severity, substrate choice, what was strengthened or
  deferred.
- **Run:** gate command, pass/fail, self-heals, escalations.
- **Evidence:** reports/artifacts generated or missing — test, coverage,
  performance, security, build artifacts, traces.

Never claim green from a provider status alone.
Name the repo-owned command, function, target, or artifact that proves the behavior.
