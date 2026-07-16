---
name: ci
description: |
  Audit, design, and run repo-owned CI gates, host-agnostic by default — one
  repo-owned contract that local, GitHub Actions, Azure, or any runner calls.
  Roster's own gate is fmt/clippy/test plus `cargo run --locked -p roster-cli
  -- check`; consumer repos keep their native gate. Use when: "run ci",
  "fix ci", "ci is red", "is ci passing", "audit/design/strengthen CI", "host-agnostic CI",
  "Dagger", "gates are slow". Trigger: /ci, /gates.
argument-hint: "[--audit-only|--run-only]"
---

# /ci

Confidence in correctness without turning local work into a provider or Docker
tax.

Roster's own source-repo gate:

```sh
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cargo run --locked -p roster-cli -- check
```

The Rust checks run in `.github/workflows/ci.yml`; `roster check` (deterministic
frontmatter/path/index/conflict-marker gate over `primitives/`) lives at
`crates/roster-cli/src/check.rs`. This is roster's own plumbing, not a framework
to project into every consumer repo.

In a consumer repo, do not assume roster's Rust gate is installed. Read that
repo's root instructions, manifests, CI workflows, hook config, and shipped
scripts, then strengthen the repo-owned gate. Roster supplies CI *judgment*; the
consumer repo owns the implementation. What to gate on follows the standing
quality floor in `primitives/shared/references/quality-gates.md`; CI
architecture and Dagger tradeoffs live in `references/host-agnostic-ci.md`.

Consumer repos want a two-tier gate unless live evidence proves one loop is both
strong and fast:

- **Fast local gate** (pre-commit/pre-push): deterministic checks an agent will
  tolerate during amend/push cycles — formatting, changed-path lint, typecheck,
  focused or changed tests, shell syntax, local-ticket bans, cheap secret scans.
- **Full ship gate** (PR/main/deploy/`ship-check`): expensive Docker, Dagger,
  browser, network, mutation, provider, and full-coverage checks.

Moving a check out of pre-push is valid only when the same invariant stays
required before merge or deploy. A path-filtered required check needs a
sentinel/split-check design, or skipped workflows leave PRs stuck pending.

## Modes

- Default: audit the gate surface, fix mechanical gaps, then run the repo-owned
  gate.
- `--audit-only`: audit report and gap proposals; do not run gates.
- `--run-only`: skip audit, drive the repo-owned gate green.

## Stance

1. **Repo-owned contract first.** The gate is a command, script, Dagger
   function, or build target the repo owns. Hosted providers call it; they do
   not define it. The same contract runs locally and from any runner without
   provider-specific rewrites.
2. **Fast enough to use.** A default local gate that routinely takes many
   minutes for harness/docs changes is a design failure. Keep expensive,
   networked, mutation, browser, and provider checks opt-in or path-scoped. When
   a behavioral gate needs a supported third-party API, prefer an
   `emulate.dev`-backed local/CI lane over weakening it, hand-written mocks, or
   live sandboxes; keep truly networked checks in the full gate only when real
   provider behavior is the point (https://emulate.dev/docs).
3. **Dagger earns its place.** Keep it when portability, containerized deps,
   caching, service orchestration, or traceability outweighs its startup/debug
   cost. Do not wrap ordinary lint/typecheck/test/build in Dagger for the inner
   loop.
4. **No quality lowering.** Removing, splitting, or moving a check is not
   permission to drop the invariant — preserve it in the fast, full, or ship
   gate.
5. **Act, do not propose.** Apply mechanical strengthenings directly. Escalate
   only when the choice is product scope, not CI plumbing.
6. **Fix-until-green on self-healable failures.** Formatting drift, stale
   generated docs/index, and trivial lints get fixed; logic failures get a
   precise diagnosis.
7. **Security floor is part of CI.** The gate prevents or fails on secret leaks
   in source, generated artifacts, logs, and Git/PR metadata — commit
   subjects/bodies, PR titles/bodies, release notes, and agent summaries are in
   scope, and matched values are redacted in reports. Prefer server-side push
   protection or pre-receive hooks; otherwise repo hooks plus CI.
8. **Reports are product.** A strong gate emits reviewable artifacts a later
   agent can use without chat context: run digest, test/coverage reports,
   mutation or fuzz survivors, perf deltas, security findings, artifact
   checksums, and residual unverified paths.

## Delegation Judgment

Delegate per the Shared Operating Spine (Act). Each lane
states responsibilities, context boundary, output evidence, and lead
verification; direct work is limited to mechanical repair and emergency
preservation, and the lead owns synthesis.

## Audit

Check the live gate surface:

- Roster: the root contract names the four commands above;
  `.github/workflows/ci.yml` runs the Rust checks; `check.rs` holds the `roster
  check` lane list; `skills-index.yaml` is current after skill/primitive changes.
- Consumer repos: substitute that repo's gate contract, then apply the same
  security floor. Confirm local hooks run the fast gate (not the full ship
  gate), the full gate stays required at merge/deploy, an explicit command runs
  the full gate locally before marking a PR ready, CI cancels stale PR runs but
  not mid-release deploys, and reports are durable enough for later diagnosis.
- Secret scanning covers committed content *and* metadata never in the working
  tree: commit message file, outbound commit range, PR title/body, release text.
  Redact matched values.

## Run

Run the repo-owned gate — the four commands above for roster, or the contract
discovered in the audit for a consumer repo. If a consumer repo has none, that
is a `high` finding: design the smallest native gate before claiming CI is
meaningful. If red: fix deterministic generated drift, run focused tests for the
failing module, re-run the aggregate. Stop after three self-heal attempts per
gate and report the exact failing command, path, and likely cause.

## Completion Gate

See `primitives/shared/AGENTS.md` (Prove) for the shared core.
`/ci` adds:

- **Audit:** gaps found, severity, substrate choice, what was strengthened or
  deferred.
- **Run:** gate command, pass/fail, self-heals, escalations.
- **Evidence:** reports/artifacts generated or missing — test, coverage,
  performance, security, build artifacts, traces.

Never claim green from a provider status alone. Name the repo-owned command,
function, target, or artifact that proved the behavior.
