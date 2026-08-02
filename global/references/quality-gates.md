# Quality Gates

The repo's STANDING quality floor lists gates that run on every change.
`global/references/verification-system-first.md` defines the quality bar and proof loop for one change.
This file defines automatic enforcement. Humans and agents do not need to remember these gates.

Every gate names the real failure it catches, or the repo deletes it.
Google's Tricorder kept analyzer false positives below ~5% for this reason.
A gate that nobody trusts is worse than no gate.

## Gate the diff, not the codebase

Enforce strict standards on **new/changed code**. Improve legacy by ratchet.
SonarSource's "Clean as You Code", Google's presubmit, and Meta's diff-time analysis use this model.
They gate the change, not the baseline.
This model adds a high bar to a brownfield repo without a large cleanup.
Use `diff-cover` for patch-scoped coverage and a committed baseline for everything else.
Never gate a global average. Legacy can make it unmeetable or trivial to pass.

## Three tiers

Place controls by latency before choosing hard-block, ratchet, or report:

- **Pre-commit:** target 2 seconds warm, hard ceiling 5; offline and staged-file scoped.
- **Pre-push:** target 60 seconds warm, hard ceiling 120; offline, cancellable,
  range/affected-work scoped, and never the unbounded full suite.
- **CI/ship:** exhaustive applicable checks with timeouts, cancellation, durable
  evidence, and required enforcement. It repeats or subsumes every local invariant.

Hook logic and installers are version-controlled; `.git/config` activation is
reversible machine state. Preserve and chain existing hook systems. Use
TruffleHog as the secret-scanning standard: staged and outbound-range scans
locally, history plus Git/PR/release metadata in CI, immutable CI pins,
fail-closed errors and missing tools, and redacted findings.

Goodhart's law applies when a measurement becomes a target.
People and agents then optimize the number instead of the measured quality.
Treat most metrics as diagnostics, not gates.

| Tier | Use for | Mechanism |
|---|---|---|
| **Hard-block** | Goodhart-resistant, behavioral, diff-scoped invariants | Fail the build: tests green / no-merge-on-red, diff-coverage floor, mutation score on core logic, supply-chain (vuln / license / dep-existence), secret scan over source + git/PR metadata. |
| **Ratchet** | Structural debt with a real but gameable signal | Baseline the current state; block new violations and any regression; let the baseline only shrink. God-files, duplication, dead code, lint-warning count, binary size. |
| **Report** | Diagnostics that guide judgment but get gamed as gates | Emit a reviewable artifact (trend, per-file, hotspots) under `.evidence/`; never block. Cyclomatic/cognitive complexity, maintainability index, coupling, churn × complexity hotspots. |

A gate moves up by ratchet: start report-only, tighten to ratchet, and promote to hard-block after the baseline is clean.
Never move a gate down to pass. Red line: do not lower gates.

## Meaningful, not arbitrary

Each number must trace to a failure mode. Otherwise it adds no gate value:

- **Coverage → diff coverage + mutation, not global %.** Line coverage proves execution, not bug detection.
  Agent-written tests can corrupt the percentage.
  Gate changed lines and mutation score on core logic. Ask whether the suite kills an injected bug.
- **God-file → multi-signal, LOC as the first check.** A god-file has high responsibility × churn × fan-in. Length is a free proxy.
  Ship the LOC ratchet first. Use churn × complexity (Tornhill hotspots) to rank files to split.
- **Line/complexity limits → per-function, ratcheted, reported.** Absolute caps invite extraction.
  Logic scatters into tiny functions and the gate passes. Readers then follow call chains.
  Cap the worst outliers, ratchet the rest, and report the metric.
- **Duplication → token-level, diff-scoped.** Detect new clones, not the Rule of Three's second copy.

## Gating agent-authored code

The distinguishing case occurs when an agent writes the code and runs its check.
It may optimize the check instead of the quality.
Measurements show 47–74% of self-improving-agent optimizations produce proxy gains without real gains.
The gap increases during longer iteration.

- **Tamper-evident and externally enforced.** An author can weaken, delete, or self-attest a gate.
  That gate cannot provide reliable evidence.
  Keep thresholds monotonic and committed. Use a fresh context because the verifier is not the producer.
- **Behavior-anchored, not metric-anchored.** Anchor to live oracles, tests, and mutation.
  These checks prevent an agent from satisfying the gate by gaming a number.
- **Dependency existence before install.** About 1 in 5 LLM-suggested packages do not exist, and agents auto-install them ("slopsquatting").
  Resolve dependencies against the registry before install, not at PR time.
- **Check common agent shortcuts.** Check clones, `as any` / `@ts-ignore`, swallowed errors, `todo!()` stubs, and dead scaffolding.
  These can compile and pass tests. Gate them mechanically.
- **Convert corrections into rules.** A repeated agent mistake shows a missing gate, not a missing instruction.
  Write the project-specific rule that fails the build on it: custom ESLint rule, `ast-grep` pattern, or Clippy `disallowed_methods`.
  Delete the corresponding prose instruction.
  Rules that encode this repo's invariants outperform generic rulesets. Each correction then becomes permanent without context cost.

## The menu (illustrative — compose for the repo, free/OSS only)

Each entry is a gate type, not a checklist to install all at once.
Choose what names a real failure in this repo and language.
Default to free and open-source, self-hostable, or a ~20-line homebrew check.
Never force a paid SaaS on a consumer.

- **Behavioral:** tests pass / no-merge-on-red; executable acceptance specs
  (Gherkin) when business-owned; end-to-end flows for user-visible surfaces;
  property-based tests where inputs have algebraic structure. The suite is the
  gate.
- **Coverage quality:** `diff-cover` (patch coverage from any LCOV/Cobertura);
  `cargo-mutants --in-diff` / Stryker / mutmut (mutation).
- **Structure (ratchet):** homebrew god-file LOC check; jscpd / PMD-CPD
  (duplication); knip / cargo-machete / vulture (dead code, unused deps).
- **Supply chain (hard-block):** cargo-deny / osv-scanner / pip-audit /
  govulncheck (vuln + license + bans); cosign + SLSA provenance; OpenSSF
  Scorecard.
- **Surface:** cargo-semver-checks / cargo-public-api / api-extractor;
  size-limit / cargo-bloat budgets.
- **Architecture (fitness functions):** ArchUnit / dependency-cruiser /
  import-linter — layering and dependency-direction rules as a build failure.
- **Project invariants:** custom ESLint rules / `ast-grep` patterns / Clippy
  `disallowed_methods` + `disallowed_types` — one rule per mistake this repo has
  actually made.
- **Decision record:** a diff that changes architecture, adds a dependency, or
  alters a public contract fails without an ADR. The gate is the record's
  existence and linkage, never its prose quality.
- **Hygiene:** secret scan over source AND commit/PR metadata; forbidden
  markers; warnings-as-errors (`-D warnings`, strict typecheck).

- **Homebrew options:** the god-file ratchet, an orphan-marker grep, and a
  baseline-ratchet wrapper (run any count-emitting tool, fail on growth) each
  avoid an unnecessary dependency.

Tooling note: prefer `ast-grep` (MIT) over Semgrep (maintained rules relicensed
2024); replace Codecov/Coveralls/SonarCloud (hosted) with `diff-cover` + raw
coverage artifacts or self-hosted SonarQube Community.

## Adoption

- A repo missing a meaningful floor is epic-scoped backlog work for `/groom`;
  start report-only and ratchet up.
- A structural win from `/refactor` (a god-file split, a removed dependency) gets
  ratcheted into a gate so it does not return.
- `/ci` audits the floor and strengthens it. The two-tier fast-local / full-CI
  split decides where each gate runs (fast & offline → local; networked or
  expensive → CI/ship).

## Prior art

Clean as You Code (SonarSource); fitness functions (Thoughtworks, *Building
Evolutionary Architectures*); the Tricorder false-positive bar and the Beyoncé
Rule (*Software Engineering at Google*); hotspots = churn × complexity
(Tornhill); characterization tests (Feathers); reward-hacking in self-improving
code agents; slopsquatting (hallucinated-dependency research). Treat
coverage-as-target and single-number metric thresholds as Goodhart-prone.
