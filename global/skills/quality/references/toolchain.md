# Toolchain targets

## Targets

Set one target for each applicable surface. Name the failure mode and a
credible falsifier before selecting the target. In a brownfield repository,
apply strict targets to changed code and use a shrink-only ratchet for the
legacy baseline.

| Surface | Target and failure mode | Seeded falsifier |
|---|---|---|
| Lint | Commit one strict base ruleset per language and treat warnings as errors on changed code. Add one project-specific mechanical rule for each mistake the repository has made, with its correction or incident cited. Require a reason on the same line as every inline disable. Ratchet the disable count. Mechanically check `as any`, `@ts-ignore`, `# type: ignore`, swallowed errors, and stub or dead-scaffolding patterns. | Add a changed-file lint violation, an unexplained disable, or one forbidden shortcut and confirm the gate fails. |
| Types | Use the strictest viable checker mode, such as `tsc --strict` or `mypy --strict`. List each relaxation with its reason instead of applying a wholesale relaxation. Ratchet suppression markers so new code adds none. Run typechecking in the fast gate. | Add a changed-file type error or suppression marker and confirm the gate fails. |
| Build | Use one repository-owned build command per artifact. Make it reproducible from the lockfile, resolve dependencies against the registry before install, and treat compiler warnings as errors where supported. Run the build or cheapest whole-program compile check no later than the full gate. | Break compilation or lockfile resolution and confirm the owning build command fails. |
| Formatting | Use one formatter per language and run its check mode in the fast gate. | Add a changed-file formatting error and confirm the gate fails. |
| Hooks | Run format checks, changed-path lint, and a cheap content and commit-message secret scan in pre-commit. Run the fast gate, typecheck, and focused or changed tests in pre-push. Provide a repository-owned setup command. A fresh clone that skips local activation must still hit the same contract in CI. | Seed a bad commit or push and confirm the effective hook blocks it. |
| Gate observability | Give every gate a name, one command, a tier (`fast`, `full`, or `scheduled`), and a report path under `.evidence/` or the CI artifact store. Record duration. Treat a fast-gate budget breach as a finding. List every gate in the assessment; an unwired script is not a gate. | Remove or bypass one gate invocation and confirm the assessment reports the missing enforcement or absent evidence. |

A baseline may only shrink. Treat a rule disable, severity downgrade,
exclusion widening, or threshold lowering as a finding, not as a fix. Require a
waiver with reason and expiry when an accepted decision does not remediate it.

## Probes

1. Enumerate every language, manifest, lockfile, lint, format, typecheck,
   build, hook, CI workflow, baseline, and repository-owned gate command. Record
   each absence as a fact.
2. Load `global/references/quality-gates.md` for tiering and diff-scoped
   enforcement. Confirm the fast gate is changed-file scoped and the full gate
   preserves the same invariant.
3. Run each applicable gate from a clean state with its exact repository-owned
   command. Capture the exit code, duration, revision, and report path.
4. For every new or changed gate, run one seeded violation, such as bad format,
   lint, type, or a blocked commit. Confirm the violation fails before restoring
   the clean path.
5. Check committed thresholds, baselines, exclusions, pins, and hook installers
   for monotonic behavior and effective wiring. A gate that exists but appears
   in no tier is a finding.

## Evidence

Store toolchain evidence under `.evidence/quality/toolchain/`. Include
`assessment.json` and its rendered `assessment.md` with the audited revision,
exact gate commands, exit codes, durations, report paths, and falsifier runs.

Link each remediation diff to the gate that verified it. Record every waiver
with approver and expiry, every deferred finding with its durable ticket, and
all residual gaps with a reason. Keep seeded-violation output beside the clean
run output.

## Safety

Keep gate configurations, thresholds, baselines, and installers committed and
version-controlled. Do not lower a gate, widen an exclusion, relax a threshold,
or rewrite a baseline to obtain green. Enforce strict checks on changed code and
improve the legacy baseline only by shrink-only ratchet.

Resolve dependency existence against the registry before installation. Keep
warnings-as-errors, suppression ratchets, and project-specific rules tied to
real repository failure modes. Keep local hooks reversible and ensure CI
re-enforces the same repository-owned contract.

## Modes

- `--audit-only`: Run toolchain probes without installing hooks, editing
  baselines, or changing repository files.
- `--remediate`: Apply only accepted toolchain findings; preserve every target,
  threshold, exclusion, and ratchet.
- `--verify`: Re-run every changed gate and its seeded falsifier from a clean
  state with a fresh, non-mutating verifier.

## Leaf routes

- Route automated test-system depth to `tests` and diff-scoped test judgment to
  `review-tests`.
- Route CI architecture, gate placement, tiering, and gate execution to `/ci`.
- Route the every-project floor (full audit + remediate) to `/foundation`.
- Use `global/references/quality-gates.md` for the standing gate floor.
- Route live behavior to a `verifier` using `verify-live`.
- Route runtime operations to the `operations` domain.
