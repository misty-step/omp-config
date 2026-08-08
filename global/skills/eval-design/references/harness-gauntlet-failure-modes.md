# Harness gauntlet failure modes

Use this list when designing or reviewing the model, reasoning, and harness gauntlet.

- **Confounded delta:** A comparison changes the model, reasoning effort, harness, prompt, or tool envelope together.
- **Nominal parity:** Two harnesses claim the same skills or MCPs but expose different tools, context, permissions, or invocation semantics.
- **Hidden primitive surface:** The enriched arm silently includes or omits settings, models, agents, extensions, presets, hooks, or runtime libraries.
- **Unverified route:** A model selector or reasoning level enters the matrix without a live catalog and launch probe.
- **Ordinal leakage:** Reasoning labels are compared across providers as if `high` had one shared meaning.
- **Cartesian explosion:** The plan runs every combination before a cheaper screen identifies useful cells.
- **Easy-corpus saturation:** Most arms pass, so the corpus cannot separate configurations.
- **Harness-favoring corpus:** Tasks only reward repository rules, skill recall, or OMP-specific procedure.
- **Bare-favoring corpus:** Tasks only reward unconstrained generation and never require durable repository conventions.
- **Ambiguous task:** Experts cannot agree on the expected outcome or grader result.
- **Missing reference:** A task has no known passing solution that proves the fixture and grader work.
- **Reference leakage:** The worker can inspect future commits, hidden tests, eval documents, or the reference solution.
- **Instrumentation costume:** A static lint, snapshot, dashboard, or past metric is reported as model capability.
- **Trajectory policing:** The grader requires one tool sequence instead of the observable result and transcript safety.
- **Judge leakage:** The judge sees arm identity, the experiment hypothesis, provider names, cost, or latency before quality scoring.
- **Uncalibrated judge:** A model-judge rate is quoted without current human anchors and fail-class precision and recall.
- **Family self-grading:** The worker family judges its own outputs.
- **Correlated trials:** Trials share a worktree, cache, service state, prior transcript, or rate-limit window.
- **Transport-as-quality:** Authentication, quota, provider, or tool failures count as task failures without a separate reliability label.
- **Incomplete cost:** Cost omits cached input, tool calls, retries, grader spend, or subscription accounting.
- **Ambiguous latency:** Reports mix queue time, provider time, tool time, and end-to-end wall time.
- **Adaptive overfit:** Pilot results tune the same tasks later used as held-out proof.
- **Winner's curse:** Many cells are ranked without multiplicity control, replication, or a confirmation set.
- **Model drift:** A provider updates a mutable model route during the campaign without snapshot or date attribution.
- **Unsupported precision:** A small corpus yields a ranked table without intervals, minimum detectable effect, or a noise-floor verdict.
- **Erasure failure:** The matrix keeps cells that cannot change a deployment decision.

Ask during every review: Which configurations, tasks, graders, and stored artifacts can be deleted without changing the decision?
