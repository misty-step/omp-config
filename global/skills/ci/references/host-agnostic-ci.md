# Host-Agnostic CI Design

Use this when you design, audit, or repair CI across local machines, GitHub Actions, Azure Pipelines, self-hosted runners, or future hosts.

The `/ci` skill teaches agents to shape repo-local CI.
The consumer repo owns the implementation.
Do not build a CI framework in the skill itself.


## Core Rule

One repo-owned contract runs everywhere:

```text
local shell / hook
GitHub Actions
Azure Pipelines
self-hosted runner
future runner
        |
        v
repo-owned gate command / Dagger function / build-system target
```

Keep provider YAML as a thin caller.
If changing CI behavior requires edits to GitHub or Azure YAML instead of the repo-owned gate, move the contract.


## Substrate Choice

Choose the smallest substrate that preserves the invariant.

| Substrate | Use When | Avoid When |
|---|---|---|
| Direct host command (`scripts/check.sh`, `bin/gate`, package script, Make/Just/Task) | Tools are already native, fast, deterministic, and easy to install locally and in hosted CI. | Environment drift is the real bug, or service orchestration dominates. |
| Dagger | The repo needs portable execution across local and hosted runners, pinned container/service dependencies, graph caching, service orchestration, or traceable pipeline functions. | It only wraps ordinary lint/typecheck/unit/build commands and makes the inner loop slower. |
| Build-system target (Bazel/Pants/Nix-backed) | The repo already earns that build graph through scale, language mix, remote cache/execution, or reproducible environments. | The build system would be introduced only to satisfy CI taste. |
| Provider reusable workflow/template | Repeating provider boilerplate across repos, while the real gate stays repo-owned. | It becomes the only source of truth or hides logic from local agents. |

Dagger is neither mandatory nor legacy by default.
Use Dagger for host-agnostic CI when its benefits carry the design: typed functions, containerized dependencies, services, cache graph, and OpenTelemetry-backed observability.
Do not make it the default when it turns a 20-second local gate into a multi-minute Docker bootstrap for ordinary checks.


## Two-Tier Gate

Every non-trivial repo should expose two gates:

- **Fast gate:** Keep it from seconds to low minutes.
  Make it deterministic and avoid network unless local emulation is the point.
  Run it from hooks and the agent inner loop.
  Typical checks include format, lint, typecheck, changed/focused tests, shell syntax, cheap secret scan, and generated drift for touched surfaces.
- **Full gate:** Require it before merge, deploy, or release.
  It can use Dagger, browser, network, provider sandboxes, mutation, full coverage, performance, packaging, and live-readiness checks.

Move a check out of the fast gate only when the full gate still requires the same invariant.
If the full gate is too slow for every push, split it.
Do not delete it.


## Comprehensive Coverage

Choose checks for failures this repo can actually suffer:

- Correctness: unit, integration, contract, e2e, replay, and golden fixtures.
- Type and static checks: typecheck, lint, shell syntax, and schema validation.
- Coverage quality: start with diff coverage, track project coverage as a trend, and use mutation or fuzzing on core logic when feasible.
- Generated drift: docs, indexes, clients, schemas, fixtures, and lockfiles.
- Security: scan source, logs, generated artifacts, commit messages, and PR/release metadata for secrets.
  Add dependency and license scans and IaC policy where relevant.
- Supply chain: pin tool versions, lockfiles, provenance, artifact hashes, and release packaging parity.
- Performance: report benchmark deltas with confidence or an explicit noise floor.
  Track bundle size and performance budgets for user-facing surfaces.
- Reliability: detect flaky tests, report retries instead of hiding them, cancel stale PR runs, and avoid cancellation for deploy/main release unless safe.

Avoid global gates that only display metrics.
Treat global coverage, complexity, or maintainability numbers as reports unless you ratchet or diff-scope them.


## Observability And Reports

A strong gate leaves context for future agents:

- Run digest: command, host, commit/range, duration, critical path, queue time when available, and cache hit/miss summary when available.
- Test report: JUnit/TAP/native JSON plus failing test logs.
- Coverage: project trend plus patch/diff coverage; raw LCOV/Cobertura when possible.
- Mutation/fuzz/perf: survivors, seeds, input corpus, and confidence/noise note.
- Security: redacted findings with rule, field, path/metadata source, and severity.
- Artifact evidence: build outputs, checksums, SBOM/provenance when relevant, deploy manifest, and rollback/readiness proof.
- Trace/log link: Dagger trace, hosted workflow run, OTel trace, or structured logs with correlation id when the substrate supports it.

Do not require every report in every repo.
Require enough evidence for a fresh agent to answer: what ran, why it failed, what changed, and what remains unverified.


## Host Portability Checks

When you audit or design a gate, ask:

- Can I run the same repo-owned contract locally and on GitHub/Azure?
- Does CI install the same tool versions as local, or pin them explicitly?
- Are secrets required only for lanes that truly need them?
- Are network/provider checks isolated from offline deterministic gates?
- Can path filters skip a required workflow into a pending or false-green state?
- Are advisory workflows visibly advisory?
- Are duplicate job names avoided so branch protection stays unambiguous?
- Are stale PR runs cancelled while main/deploy runs stay protected?
- Is cache configuration keyed by real inputs, not mutable outputs?
- Is the report artifact durable and linked from the completion summary?

Agents need CI to be legible:

- Name the one command the agent should run before claiming done.
- Name the fast command and the full command separately.
- Keep sidecar workflows classified: required, advisory, scheduled, deploy, release, bot/review.
- Fail with actionable, redacted diagnostics.
  Do not make agents inspect a provider UI for basic errors.
- Keep generated artifacts and evidence packets in predictable paths.
- Record skipped heavyweight checks as residual risk, not as green.
- Treat hooks as convenience, not trust boundaries.
  CI or branch protection must enforce the merge/deploy floor.

## Source Anchors

- Dagger docs: https://docs.dagger.io/
- Dagger CI quickstart: https://docs.dagger.io/0.16.3/ci/quickstart/
- Dagger observability: https://docs.dagger.io/features/observability/
- DORA metrics: https://dora.dev/guides/dora-metrics/
- GitHub reusable workflows: https://docs.github.com/en/actions/concepts/workflows-and-actions/reusing-workflow-configurations
- GitHub status checks: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks
- Azure templates: https://learn.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops
- Azure branch policies: https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies-overview?view=azure-devops
- OpenTelemetry Collector: https://opentelemetry.io/docs/collector/
