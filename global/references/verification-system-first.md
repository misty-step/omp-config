# Verification System First

A verification system is a repeatable loop that can prove work wrong.
It is not a confidence phrase, checklist, or passing command alone.

Use this reference when shaping, delivering, refactoring, performing QA, designing evals, writing benchmarks, or changing harness primitives.

## Contract

Before implementation, name the smallest credible system that decides whether the work actually works:

1. **Claim:** the behavior, quality, or operator outcome that must be true.
2. **Falsifier:** the concrete failure the system would catch.
3. **Driver:** command, route, browser walk, request replay, fixture runner,
   benchmark, eval, migration dry run, consumer build, or production probe.
4. **Grader:** exact assertion, rubric, golden, threshold, human calibration
   note, or observed artifact that turns the driver into pass/fail evidence.
5. **Evidence packet:** screenshots, transcripts, logs, request/response pairs,
   benchmark output, eval report, verdict, or receipt path another agent can
   inspect later.
6. **Cadence:** when it runs: before edits, after each milestone, pre-merge,
   post-ship, or on a recurring Mode B loop.

If the repo has no system for the changed surface, build or name that system first.
A team that ships a feature before its proof loop ships an unverified guess.

## What Counts

| surface | verification system |
|---|---|
| Web UI | dev/preview URL, scripted or manual browser path, console/network check, screenshots or video |
| API/service | representative request replay, contract assertions, local third-party API emulation when supported, error-path cases, logs |
| CLI | documented happy path, malformed-input path, exit codes, stderr/stdout checks |
| Library/SDK | consumer build or throwaway install that exercises the public API |
| MCP/agent tool | harness registration plus replayed tool calls and structured-error checks |
| Model/agent behavior | held-out task, transcript, grader, rubric calibration, and outcome artifact |
| Performance | benchmark with workload, baseline, threshold, variance note, and raw output |
| Migration/data | dry run, fixture snapshot, rollback path, and invariant checks |
| Ops/monitoring | health/readiness/log/metric/alert probe tied to the changed behavior |

Use multiple systems when one boundary cannot see the failure.
Unit tests, typechecks, and lint catch structural regressions.
QA, evals, benchmarks, and probes catch failures at runtime, judgment, scale, or integration boundaries.

## Live-Diff For Behavior-Preserving Refactors

When the oracle is "identical to before" and the target has no characterization tests, unit tests cannot detect the seam that a lift often breaks.
The seam is the integration between the refactored layer and its real dependencies, which unit tests mock away.
**Technique:** Exercise the same representative inputs against (a) the local refactor branch and (b) the deployed or pre-refactor build.
Point both builds at the same backing store.
Diff responses byte-for-byte, including error and not-found paths, not only the happy path.
Identical responses across the set mean behavior is preserved.
Any divergence is the bug, located at the differing input.
In verification-system terms, the deployed or pre-refactor build is the grader's reference oracle, and the diff is the falsifier.

**Precondition:** The pre-refactor behavior must run against the same data.
Use a deployed prod instance, a pinned build, or `git stash` plus a local rerun.

**Does not apply when:** The refactor must change output; pin a golden instead.
It also does not apply to write-path side effects.
Use post-state reads or a transaction-scoped probe for those effects.

**Pair, do not replace.** Live-diff checks integration. Repository and unit tests check structure underneath it.

Proven live 2026-06-17/18 on a 6-route rewrite with zero route-level tests.
Repository unit tests plus a before/after live diff proved behavior preservation.
The local branch and deployed prod used the same backing store.
Representative list, detail, and 404 responses were byte-identical.
This combination was the only proof that preserved the rewrite.

## Design Rules

- **Falsifiability first.** A system that passes when values are wrong does not verify behavior.
  Mutate a fixture, route, expected value, or threshold when cheap to prove the check can fail.
- **Live before decorative.** Run the driver before formatting the report.
  A report without driver evidence is not proof.
- **Repo-shaped, not tool-shaped.** Choose tools from the app shape and operator workflow.
  Select browser for web UI, shell for CLI, HTTP for API or service, eval for model behavior, benchmark for performance, and monitor for operations.
- **Emulate supported third-party APIs locally.** When `emulate.dev` covers the provider, use an emulator plus representative request replay.
  Record services, ports, seed file, reset/teardown, and the docs used (https://emulate.dev/docs).
- **Leave receipts.** The evidence packet is part of the deliverable.
  Future agents should not need chat context to judge the claim.
- **Escalate recurring checks.** Turn a repeated manual QA path into a repo-local verification skill, script, gate, benchmark, or Mode B loop.
- **Do not weaken gates.** If the current system is too slow, split fast and heavyweight lanes.
  Keep the only proof that catches the failure.

## Eval & Benchmark Rigor

The grader and numbers both affect the system. Size and read them honestly.
A strong model may report "3.8 → 4.1, improved" after twelve samples.
Do not accept that claim alone.

**Statistical honesty.**
- No score without a confidence interval. For a rate, `SE = sqrt(p*(1-p)/n)`,
  95% CI `±1.96*SE`. A paired delta whose CI includes 0 is noise, not a result.
  (Miller, "Adding Error Bars to Evals", arXiv 2411.00640)
- Right-size n. Detecting a ~3% absolute change at 80% power needs ~1000 items.
  A ~12-item suite catches only large regressions.
  Read small deltas as noise and say so. (Miller)
- Compare versions paired on identical items (McNemar / paired bootstrap), not as two independent rates.
  Pairing reduces variance without extra items. (Miller)
- Cluster the SE by source when many graded items share one document — naive
  independence understated uncertainty >3x on real benchmarks. (Miller)
- Average K samples per item for nondeterministic graders (K=2 cuts variance ~1/3).
  Do not lower temperature to create false stability.
  Lower temperature trades variance for bias. (Miller)

**Judge validity (model graders).**
- Validate the judge against human labels before trusting it.
  Target Cohen's κ ≈ 0.80; report TPR/TNR (not raw % agreement) under class imbalance.
  Then bias-correct the rate. (Hamel Husain, evals-faq; "Judge's Verdict", arXiv 2510.09738)
- Use binary pass/fail per atomic criterion, not a 1–5 Likert.
  Likert does not track expert judgment and is not actionable.
  Have the judge write its rationale before the verdict. (Hamel Husain, llm-judge; G-Eval, arXiv 2303.16634)
- Judge model ≠ generator family (self-enhancement is +10–25% win rate).
  Reference-guide objective items. Use one judge per dimension.
  Allow an "insufficient info" result. (Zheng et al., MT-Bench, arXiv 2306.05685; Anthropic, Demystifying Evals)
- A ~100% pass rate means the eval is too weak. Aim for ~70%.

**Anti-Goodhart.** A judge or threshold can stop measuring once optimized against.
Keep a hidden held-out split and select by it (≈60/40).
Diversify and rotate sources. n-gram-screen new fixtures for contamination.
Turn every shipped defect into a permanent fixture-backed case so it cannot regress silently.

## Minimum Artifact

Every substantial plan or closeout should include:

```markdown
Verification system:
- Claim:
- Falsifier:
- Driver:
- Grader:
- Evidence packet:
- Cadence:
- Gaps / waiver:
```

For tiny mechanical changes, use a focused structural gate or exact inspection.
Name why the closeout needed no live loop.

## Failure Modes

- **Passing aggregate without evidence:** "tests passed" with no route, command, artifact, or changed surface named.
- **Eval directory without grader:** folders and prompts with no grader or held-out task.
- **Benchmark without baseline:** one run, no baseline, no variance note, no threshold.
- **QA statement without evidence:** "looked good" with no screenshot, transcript, or path.
- **Missing instrumentation:** no post-ship signal would reveal the behavior breaking.
- **Author-only judgment:** the same context that built the work also grades the open-ended outcome without held-out artifacts or fresh critique.
