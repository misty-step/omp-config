# Eval-design source canon

Annotated primary sources behind this skill, ranked by fit for our context
(agentic software-engineering workflows, model+harness comparison under budget,
Crucible as the enforcement engine). Load this file when you need to justify a
methodology choice or go deeper than the skill's distillation. Research date
2026-07-07; every entry carries its own date — re-verify anything load-bearing
that has aged.

## The three to read first

### Anthropic — "Demystifying evals for AI agents" (2026-01-09)
anthropic.com/engineering/demystifying-evals-for-ai-agents

The agentic design front-end. What to take:
- Grade **outcomes + transcripts, not trajectories**: verify the final
  environment state (the reservation exists in the DB; the patch fixes the bug),
  never a prescribed step sequence — "agents regularly find valid approaches."
- **`pass@k` vs `pass^k`** is a product decision: any-of-k succeeds (coding) vs
  all-k succeed (customer-facing). At k=10 they tell opposite stories.
- **20–50 tasks from real failures** (bug tracker, support queue) is a strong
  start; a good task is one where **two domain experts independently reach the
  same pass/fail verdict**.
- Attach a **reference solution** per task — proves solvability and verifies the
  grader. "A 0% pass rate… is most often a signal of a broken task."
- **Class-balance** ("test where a behavior should occur and where it
  shouldn't"); give the judge an "Unknown" exit; isolate trials in clean
  environments; read transcripts.

### Hamel Husain — "Your AI Product Needs Evals" (2024-03-29)
hamel.dev/blog/posts/evals/

The eval-driven-development frame. What to take:
- Three levels: L1 unit-test assertions (cheap, CI), L2 human & model eval,
  L3 A/B. Climb only as needed.
- **"You are doing it wrong if you aren't looking at lots of data"** — read
  traces until you stop learning; grader bugs and broken tasks only surface
  there.
- The **critique-align judge loop**: powerful model emits pass/fail + critique,
  human labels the same items, measure agreement, iterate the judge prompt.
  Use **precision/recall, not raw agreement, on imbalanced data**.
- The data flywheel: eval infra is what turns a demo into a product.

### Evan Miller — "Adding Error Bars to Evals" (arXiv:2411.00640, 2024-11)
Also: aievals.co/cookbook/adding-error-bars

The statistics behind Crucible's whole thesis. Five recommendations:
1. Report SE of the mean + CIs; treat questions as an i.i.d. sample from a
   super-population; binary `SE = sqrt(p(1-p)/n)`.
2. **Clustered standard errors for grouped questions — can be >3× naive.**
   (Crucible does not yet compute these; flag grouped corpora.)
3. Reduce variance by resampling / next-token probs; **don't tune temperature
   for variance**.
4. **Paired analysis when comparing two models** — "a free reduction in
   estimator variance": `Var(paired) = Var(unpaired) − 2·Cov(A,B)/n`.
5. Power-analyze n; "new evals should contain at least 1,000 questions" to
   detect 3% at 80% power — most bespoke evals resolve only larger effects, so
   declare the resolvable effect.

## Judge-bias literature

### MT-Bench — Zheng et al. (arXiv:2306.05685, 2023-06)
Canonical judge biases: **position, verbosity, self-enhancement/self-preference,
limited reasoning**. Mitigations: swap answer positions and require both-order
agreement; a strong judge reaches >80% agreement with humans (≈ inter-human
agreement). Pairwise / single-answer / reference-guided judging modes.

### G-Eval — Liu et al. (arXiv:2303.16634, 2023)
Chain-of-thought + form-filling judge, now standard (promptfoo `g-eval`).
Known **bias toward fluent LLM-generated text** — watch it when candidates mix
human and model authorship.

### Braintrust — "What is an LLM-as-a-judge?" (braintrust.dev)
Practitioner consolidation: deterministic checks own format/schema, judges own
only subjective dimensions; randomize order both directions; run multiple times
and average; calibrate against a **100–200-example human-labeled set** and
report the correlation. Convergent finding across promptfoo/Databricks/
Anthropic examples: **binary or ≤5-point scales beat 1–10**.

## Reference architectures & tools (borrow, don't rebuild)

### UK AISI Inspect — inspect.aisi.org.uk
Highest architectural fit. `Task` · `Dataset/Sample` · `Solver` · `Scorer`
mirrors Crucible's EvalSpec + runner + grader. **Epochs + reducers** are the
repeated-trials mechanism that makes `pass@k`/`pass^k` and variance reduction
computable — the model to borrow. First-class agentic: tools, sandboxing,
200+ pre-built evals.

### promptfoo — promptfoo.dev
providers × prompts × tests × assertions; deterministic (`equals`/`contains`/
`is-json`/regex) vs model-graded (`llm-rubric`/`g-eval`/`factuality`);
trajectory assertions for agents. Already Crucible's first import adapter.

### OpenAI Evals — github.com/openai/evals
JSONL + YAML, no-code for basic/model-graded template families; **grade with a
different model than completed**. Good second import-adapter candidate.

### Also scanned
Braintrust `Eval()` + autoevals (weak on published significance math — Crucible
is ahead); LangSmith evals (commodity); Ragas (RAG metric decomposition, not an
agentic-SWE fit); Anthropic platform docs "Define success criteria and build
evaluations" (SMART criteria, grader ladder, reasoning-first judging — validates
Crucible's tail-anchored verdict parsing); Anthropic cookbook
`misc/building_evals.ipynb`; Matt Pocock's Evalite + aihero.dev (same
dataset+task+scorers frame, TS/Vitest runner). Skill registries (skills.sh,
Anthropic, Pocock's 50): **no eval-design skill exists anywhere** — this skill
was authored fresh from the sources above.
