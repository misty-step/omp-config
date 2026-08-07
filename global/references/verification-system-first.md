# Verification System First

A verification system is a repeatable loop that can prove work wrong. It is not a confidence phrase, checklist, or passing command alone.
Use this reference when shaping, delivering, refactoring, performing QA, designing evals, writing benchmarks, or changing harness primitives.
## Quality Contract
Before implementation, name the smallest credible system that decides whether work works:
1. **Claim:** behavior, quality, or operator outcome that must be true.
2. **Standards:** local project properties that define good work here.
3. **Falsifier:** concrete failure the system would catch.
4. **Driver:** command, route, browser walk, request replay, fixture runner, benchmark, eval, migration dry run, consumer build, or production probe.
5. **Grader:** exact assertion, rubric, golden, threshold, human calibration note, or observed artifact that makes pass/fail evidence.
6. **Evidence packet:** screenshots, transcripts, logs, request/response pairs, benchmark output, eval report, verdict, or receipt path another agent can inspect.
7. **Cadence:** when it runs: before edits, after milestones, pre-merge, post-ship, or recurring Mode B loop.
8. **Critic topology:** artifact, lens, risk tier, and reviewer separation.
9. **Stop rules:** conditions that halt execution instead of improvisation.
Make good enough visible before execution. Keep proof independent of the author's confidence. Use artifacts, not bullets without evidence.
If the repo has no system for the changed surface, build or name it first. Shipping before its proof loop ships an unverified guess.
For non-trivial work, show the system in the plan's first viewport without chat context: target outcome/design, standards, proof methods/evidence surfaces, and stop rules/review focus.
Put alternatives, acceptance, verification detail, cadence, risks, and reviewer instructions in support sections.
## Proof Families
Prefer independent proof families for substantive work:
| proof | answers | examples |
|---|---|---|
| Live oracle | Does changed behavior work in reality? | browser walk, CLI run, request replay, migration dry run, consumer build |
| Structural gate | Did repo automation catch regressions? | tests, lint, typecheck, harness gate, generated-doc drift |
| Eval / benchmark | Does agent, model, or performance claim survive held-out tasks or workload pressure? | skill eval, raw-vs-harness comparison, latency/throughput benchmark |
| Process campaign | Does a multi-agent protocol hold under fault and illegal order? | FSM transition tests, multi-seed gate runs, Iron Forest `forest sim` |
| Fresh critic | Did a fresh reviewer refute the claim? | diff + oracle review, design, security, or architecture lens |

Independence matters. Three commands at one unit boundary form one proof method; a critic inheriting the author's reasoning is not fresh. Use multiple systems when one boundary cannot see the failure.
Unit tests, typechecks, and lint catch structural regressions; QA, evals, benchmarks, process campaigns, and probes catch runtime, judgment, scale, integration, or protocol failures.

| surface | verification system |
|---|---|
| Web UI | dev/preview URL, scripted or manual browser path, console/network check, screenshots or video |
| API/service | representative request replay, contract assertions, local third-party API emulation when supported, error paths, logs |
| CLI | documented happy path, malformed-input path, exit codes, stderr/stdout checks |
| Library/SDK | consumer build or throwaway install exercising the public API |
| MCP/agent tool | harness registration plus replayed tool calls and structured-error checks |
| Model/agent behavior | held-out task, transcript, grader, rubric calibration, and outcome artifact |
| Performance | workload benchmark, baseline, threshold, variance note, and raw output |
| Migration/data | dry run, fixture snapshot, rollback path, and invariant checks |
| Ops/monitoring | health/readiness/log/metric/alert probe tied to changed behavior |
## Live-Diff for Behavior-Preserving Refactors
When the oracle is identical-to-before and no characterization tests exist, unit tests miss seams that mocks hide.
Exercise representative inputs against the local refactor and deployed or pre-refactor build, using the same backing store.
Diff responses byte-for-byte, including error and not-found paths, not only the happy path. Any divergence identifies the bug.
The pre-refactor behavior must run against the same data through deployed prod, a pinned build, or git stash plus local rerun.
If output must change, pin a golden instead. For write side effects, use post-state reads or a transaction-scoped probe.
Pair live diff with repository and unit tests: live diff checks integration, while tests check structure.
## Design Rules and Critic Topology
- **Falsifiability first:** mutate a fixture, route, expected value, or threshold when cheap to prove the check can fail.
- **Live before decorative:** run the driver before formatting the report; a report without driver evidence is not proof.
- **Repo-shaped:** use browser for UI, shell for CLI, HTTP for API/service, eval for model behavior, benchmark for performance, and monitor for operations.
- **Third-party APIs:** when `emulate.dev` covers the provider, use its emulator and representative replay; record services, ports, seed, reset/teardown, and docs (https://emulate.dev/docs).
- **Leave receipts:** the evidence packet is part of the deliverable; future agents must judge the claim without chat context.
- **Escalate recurring checks:** turn repeated manual QA into a repo skill, script, gate, benchmark, or Mode B loop.
- **Do not weaken gates:** split fast and heavyweight lanes if slow; keep the only proof that catches the failure.
Separate execution from critique; do not perform independent review in one context. Give critics only the artifact: diff, plan, oracle, screenshots, logs, or rendered surface, not the author's reasoning trail.
Use one lens per critic and `global/references/lenses.md` for compact rubrics. Use a different model family when adversarial review matters.
The lead owns synthesis. Reviewer output is evidence, not authority; the lead fixes, rejects with reason, tickets, or escalates.
## Risk Tiers
| tier | when | minimum quality system |
|---|---|---|
| Tiny | mechanical, single-file, low-blast-radius change | structural gate or exact inspection; name why no fresh critic is needed |
| Substantive | product behavior, shared code, harness primitive, generated output, or multi-file diff | live oracle + structural gate + one fresh-context critic aimed at likely production failure |
| High-stakes | security, data loss, auth, migrations, architecture boundary, public launch, or hard-to-rollback infra | live oracle + structural gate + multiple distinct critic lenses or model families; re-review blocker fixes |
| Event-driven | PR-ready review, incident response, scheduled audit, or recurring production check | Mode B is unavailable; keep Mode A until a future event-plane product is explicitly named |
Scale down for small work. Scale up only when failure is expensive, public, irreversible, or hard to observe.
Examples: Tiny = wording/copy or dependency metadata without behavior; Substantive = skill/shared-helper/UI/generated-artifact change; High-stakes = auth, secrets, migrations, destructive files, release automation, or public claims; Event-driven = recurring review, audit, incident, or monitor.
## Eval and Benchmark Rigor
The grader and numbers both affect the system. Inspect both honestly; a 3.8-to-4.1 gain after twelve samples is not enough.
- **Statistical honesty:** report rate confidence intervals: `SE = sqrt(p*(1-p)/n)`, 95% CI `±1.96*SE`; a paired delta whose CI includes 0 is noise, not a result (Miller, “Adding Error Bars to Evals,” arXiv 2411.00640).
- **Right-size n:** detecting a ~3% absolute change at 80% power needs ~1000 items; ~12 items catch only large regressions; call small deltas noise (Miller).
- **Pair versions:** compare identical items with McNemar or paired bootstrap, not independent rates; pairing reduces variance without extra items (Miller).
- **Cluster uncertainty:** cluster SE by source when graded items share one document; naive independence understated uncertainty by >3x on real benchmarks.
- **Sample nondeterminism:** average K samples per item; K=2 cuts variance by ~1/3. Do not lower temperature to create false stability; it trades variance for bias (Miller).
- **Validate judges:** compare model graders with human labels; target Cohen's κ ≈ 0.80; report TPR/TNR, not raw agreement under imbalance; bias-correct the rate (Hamel Husain, evals-faq; “Judge's Verdict,” arXiv 2510.09738).
- **Grade atomically:** use binary pass/fail per criterion, not 1–5 Likert; Likert misses expert judgment and is not actionable; require rationale before verdict (Hamel Husain, llm-judge; G-Eval, arXiv 2303.16634).
- **Separate families:** judge model must differ from generator family; self-enhancement raises win rate 10–25%; use reference-guide objective items, one judge per dimension, and an “insufficient info” result (Zheng et al., MT-Bench, arXiv 2306.05685; Anthropic, Demystifying Evals).
- **Challenge easy scores:** ~100% pass means the eval is too weak; aim for ~70%.
- **Anti-Goodhart:** keep a hidden held-out split (~60/40), diversify and rotate sources, n-gram-screen new fixtures, and turn every shipped defect into a permanent fixture-backed case.
## Evidence Capture

Every claim needs a durable evidence packet. A reviewer must judge the claim
without chat context. Capture the evidence with the cheapest honest method
for the surface.

- Rendered behavior: capture a screenshot or a short video. A still proves a
  state. It never proves motion.
- Behavior over time: record a video. For an interactive issue, record the
  steps and one frame per step.
- API and CLI: capture the request, the response, and the exit code.
- Logs and sinks: capture the exact lines that show the result.
- Packets: list every artifact with its size and hash. A reviewer can then
  confirm that nothing changed after capture.

State the surface you captured. Name the gap when you could not capture
something. Delete captured operator content after you verify it. Prefer
numeric checks, such as hashes and frame differences, over viewing personal
content.

The machine-specific capture tooling lives in
`global/skills/verify-live/references/evidence-capture-tooling.md`.

## Minimum Artifact
Every substantial plan or closeout includes: `Claim`, `Standards`, `Falsifier`, `Driver`, `Grader`, `Evidence packet`, `Cadence`, `Critic topology`, `Stop rules`, and `Gaps / waiver`.
For tiny mechanical changes, use a focused structural gate or exact inspection and name why the closeout needed no live loop.
## Failure Modes
- **Checklist without live path:** fields look complete, but no live path runs.
- **Same-context review:** several reviewers in one context agree with the author.
- **Over-review:** wide reviewer sets for tiny diffs waste tokens and attention.
- **Late review:** foundational mistakes appear only after a large build.
- **Vendor branding:** encode a model brand instead of the needed capability.
- **Passing aggregate without evidence:** “tests passed” names no route, command, artifact, or changed surface.
- **Eval without grader:** eval folders and prompts have no grader or held-out task.
- **Benchmark without baseline:** one run has no baseline, variance note, or threshold.
- **QA without evidence:** “looked good” has no screenshot, transcript, or path.
- **Missing instrumentation:** no post-ship signal reveals behavior breaking.
- **Author-only judgment:** the builder grades an open-ended outcome without held-out artifacts or fresh critique.
- **Review-free ship:** a completion claim carries no verified review receipt, or cites one frozen against a superseded range.
