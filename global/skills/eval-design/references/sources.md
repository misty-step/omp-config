# Eval-design source canon

This file annotates the primary sources behind this skill.
It ranks them by fit for agentic software-engineering workflows,
model+harness comparison under budget, and Crucible as the enforcement engine.
Load it to justify a methodology choice or go deeper than the skill's distillation.
Research date: 2026-07-07. Re-verify each load-bearing entry that has aged.

## The three to read first

### Anthropic — "Demystifying evals for AI agents" (2026-01-09)
anthropic.com/engineering/demystifying-evals-for-ai-agents

The agentic design front end. Take these points:
- Grade **outcomes + transcripts, not trajectories**.
  Verify the final environment state, such as the reservation in the DB or the
  patch that fixes the bug. Do not prescribe a step sequence.
  "Agents regularly find valid approaches."
- Treat **`pass@k` vs `pass^k`** as a product decision.
  Any-of-k succeeds in coding; all-k succeeds for customer-facing consistency.
  At k=10, the measures tell opposite stories.
- Start with **20–50 tasks from real failures** in the bug tracker or support queue.
  A good task lets **two domain experts independently reach the same pass/fail verdict**.
- Attach a **reference solution** to each task.
  It proves solvability and verifies the grader.
  "A 0% pass rate… is most often a signal of a broken task."
- **Class-balance** the corpus.
  Test where behavior should occur and where it should not.
  Give the judge an "Unknown" exit, isolate trials in clean environments, and
  read transcripts.

### Hamel Husain — "Your AI Product Needs Evals" (2024-03-29)
hamel.dev/blog/posts/evals/

The eval-driven-development frame. Take these points:
- Use three levels: L1 unit-test assertions (cheap, CI), L2 human and model eval,
  and L3 A/B. Climb only as needed.
- **"You are doing it wrong if you aren't looking at lots of data."**
  Read traces until you stop learning. Grader bugs and broken tasks surface there.
- Use the **critique-align judge loop**.
  Have a powerful model emit pass/fail plus critique.
  Have a human label the same items, measure agreement, and iterate the judge prompt.
  Use **precision/recall, not raw agreement, on imbalanced data**.
- The data flywheel turns a demo into a product through eval infrastructure.

### Evan Miller — "Adding Error Bars to Evals" (arXiv:2411.00640, 2024-11)
Also: aievals.co/cookbook/adding-error-bars

The statistics behind Crucible's thesis. Apply these five recommendations:
1. Report SE of the mean and CIs. Treat questions as an i.i.d. sample from a
   super-population. Use binary `SE = sqrt(p(1-p)/n)`.
2. **Cluster standard errors for grouped questions.** They can exceed naive
   errors by >3×. Crucible does not compute them yet, so flag grouped corpora.
3. Reduce variance through resampling or next-token probabilities.
   **Do not tune temperature for variance.**
4. **Use paired analysis when comparing two models.**
   This gives "a free reduction in estimator variance":
   `Var(paired) = Var(unpaired) − 2·Cov(A,B)/n`.
5. Power-analyze n. "New evals should contain at least 1,000 questions" to
   detect 3% at 80% power. Most bespoke evals resolve only larger effects.
   Declare the resolvable effect.

## Judge-bias literature

### MT-Bench — Zheng et al. (arXiv:2306.05685, 2023-06)
Canonical judge biases include **position, verbosity,
self-enhancement/self-preference, and limited reasoning**.
Mitigate them by swapping answer positions and requiring both-order agreement.
A strong judge reaches >80% agreement with humans (≈ inter-human agreement).
Use pairwise, single-answer, or reference-guided judging modes.

### G-Eval — Liu et al. (arXiv:2303.16634, 2023)
Use a chain-of-thought and form-filling judge, now standard (promptfoo `g-eval`).
Watch the known **bias toward fluent LLM-generated text** when candidates mix
human and model authorship.

### Braintrust — "What is an LLM-as-a-judge?" (braintrust.dev)
Use deterministic checks for format and schema.
Use judges only for subjective dimensions.
Randomize order in both directions, run multiple times, and average.
Calibrate against a **100–200-example human-labeled set** and report correlation.
Across promptfoo, Databricks, and Anthropic examples, **binary or ≤5-point scales
beat 1–10**.

## Reference architectures & tools (borrow, don't rebuild)

### UK AISI Inspect — inspect.aisi.org.uk
Inspect has the highest architectural fit.
`Task` · `Dataset/Sample` · `Solver` · `Scorer` mirror Crucible's EvalSpec,
runner, and grader.
**Epochs + reducers** implement repeated trials for `pass@k`, `pass^k`, and
variance reduction. Borrow this model.
Inspect supports agentic tools, sandboxing, and 200+ pre-built evals.

### promptfoo — promptfoo.dev
promptfoo provides providers × prompts × tests × assertions.
It supports deterministic (`equals`/`contains`/`is-json`/regex) and
model-graded (`llm-rubric`/`g-eval`/`factuality`) checks.
It also supports trajectory assertions for agents.
Crucible already uses it as the first import adapter.

### OpenAI Evals — github.com/openai/evals
JSONL + YAML support no-code basic and model-graded template families.
**Grade with a different model than completed.**
OpenAI Evals is a good second import-adapter candidate.

### Also scanned
Braintrust `Eval()` + autoevals have weak published significance math;
Crucible is ahead.
LangSmith evals are commodity.
Ragas provides RAG metric decomposition, not an agentic-SWE fit.
Anthropic platform docs, "Define success criteria and build evaluations,"
cover SMART criteria, the grader ladder, and reasoning-first judging.
They validate Crucible's tail-anchored verdict parsing.
Also scanned: Anthropic cookbook `misc/building_evals.ipynb`, Matt Pocock's
Evalite, and aihero.dev. They use the same dataset+task+scorers frame with a
TS/Vitest runner.
Skill registries (skills.sh, Anthropic, Pocock's 50) show **no eval-design skill
exists anywhere**. This skill was authored fresh from the sources above.
