# Model-harness census v0

Status: draft and blocked. Do not run it until the proof gate passes.

Review `../references/harness-gauntlet-failure-modes.md` before running or changing this eval.

## Demarcation

- Decision: choose which confirmed model-effort-harness-composition cells receive representative evaluation.
- Fresh output: each cell runs a fresh agent against three history-free repository tasks.
- Grader: immutable deterministic behavior and scope checks score the final repository state.

This census screens the complete requested roster. It does not authorize deployment or a final rank.

## Capability

The configuration repairs small real defects across generic parsing, security boundaries, and product UI state.

A controlled cell is eligible only when:

1. all three tasks hard-pass;
2. every scope check passes;
3. model and provider-native effort identity match the request;
4. the transcript and trial receipts are valid;
5. no transport, timeout, or fallback failure occurred.

Partial credit cannot make a cell eligible.

## Availability ledger
This ledger covers controlled cells only. Native-default baselines use the receipt branch below.

Read the requested roster in `../../../../docs/harness-gauntlet-brain-dump.md`.

If a requested route has no known native effort set, persist one `blocked_route` sentinel per harness and composition with `effort_requested: null`. Replace the sentinels with effort-specific rows only after exact resolution.

`availability.json` uses `harness_census.availability.v1`. Each row contains:

```text
campaign_id: string
model_requested: string
effort_requested: string|null
provider_route_resolved: string|null
provider_effort_resolved: string|null
harness: prime|omp|pi
composition: controlled_raw|controlled_enriched
status: confirmed|blocked_route|blocked_effort|clamped_effort|blocked_harness|blocked_composition
reason_code: string|null
evidence_ref: content-addressed URI|null
row_id: sha256 string
cohort_id: sha256 string|null
```

A confirmed row requires both resolved identity fields, `reason_code: null`, and a non-null availability `evidence_ref`. A blocked row requires `reason_code` and `evidence_ref`; it never runs. Task qualification is a campaign gate, not a row status.

Each availability `evidence_ref` resolves to `harness_census.availability_evidence.v1` with `campaign_id`, `row_id`, requested and resolved identities, harness and version, adapter digest, catalog digest, probe request digest, probe result digest, and observed status. Recompute `row_id` and require every field to match the row.

Use `sha256:<hex>@<campaign-relative-path>` for every content-addressed URI. Reject paths outside the campaign root.

The campaign-scoped ledger key is the JSON array `[campaign_id, model_requested, effort_requested|null, harness, composition]`. Set `row_id` to SHA-256 of its RFC 8785 encoding and reject duplicates. For confirmed rows, derive `cohort_id` the same way from `[campaign_id, model_requested, effort_requested, provider_route_resolved, provider_effort_resolved]`.

A six-cell paired claim requires one campaign-scoped cohort with the same exact provider route and provider-native effort in all six cells. A harness's accepted CLI label is insufficient when its adapter clamps that label.

## Controlled cells

Each model-effort target requests these six rows:

1. Prime Agent controlled-raw;
2. Prime Agent controlled-enriched;
3. OMP controlled-raw;
4. OMP controlled-enriched;
5. Pi controlled-raw;
6. Pi controlled-enriched.

Run each confirmed row on all three tasks even when a sibling is blocked. Treat an incomplete cohort as product-local evidence only. Make a paired six-arm claim only when all six rows are confirmed.

The third harness is confirmed as Pi 0.83.0.

Cross-harness comparisons are whole-product `config_delta` comparisons. Native tools and orchestration differ.

Every controlled cell receives an explicit exact model and effort.

## Required native-default baseline

Run one separate native-default cell per harness on the same three tasks.

- Use a fresh empty profile.
- Do not pass a model or effort override.
- Preserve the pinned product's native system prompt and built-in tools.
- Disable external operator context and packages that are not part of a fresh install.
- Record the resolved default model, effort, tools, and system identity.

Native-default receipts set `cell_kind` and `composition` to `native_default`; set requested model, effort, `row_id`, and `cohort_id` null; and require non-null `baseline_id`, `profile_digest`, resolved provider route and effort, response attestations, verified identity, system identity, system prompt digest, tool manifest digest, and `default_resolution_source`. Derive `baseline_id` from the RFC 8785 encoding of those identities plus campaign, harness, and harness version. All three task receipts must share it. One failure sets the baseline summary to invalid.

`provider_route_resolved` is the resolved default model identity. The baseline summary recomputes `baseline_id` from each receipt, requires the three identities and `profile_digest` values to match, lists all three task receipt digests, and records `valid` only when all three trials are valid.


## Composition contract
Both controlled arms receive identical task code and prompts. Context files are treatment bytes: the raw worker view omits and denies them; the enriched view mounts frozen pre-fix copies from the pack. Record both view digests.



### Controlled-raw

- fresh profile and session;
- native system prompt and built-in tools;
- no discovered operator AGENTS, CLAUDE, RULES, skills, MCPs, extensions, hooks, templates, caches, or memory;
- runner-supplied provider declarations only;
- no configured default, fallback, role, or model ladder.

### Controlled-enriched

Add one frozen portable pack to controlled-raw:

- shared operator AGENTS text;
- shared sticky rule text;
- all 42 skill entry points plus only runtime references and assets named in the allowlist;
- one shared HTTP MCP identity and tool contract;
- frozen copies of task context files omitted from the controlled-raw worker view;
- an include and holdout manifest with duplicate-key rejection.

The allowlist must exclude `global/skills/**/evals/**`, `global/skills/**/tests/**`, `global/skills/**/fixtures/**`, every `WAIVER.md`, all task grader and task reference artifacts, and all campaign documents. It must explicitly exclude `docs/harness-gauntlet-brain-dump.md`, `global/skills/eval-design/evals/model-harness-census-v0.md`, and `global/skills/eval-design/references/harness-gauntlet-failure-modes.md`.

Generate the manifest with a duplicate-key-rejecting YAML loader before normalization. Convert paths to repository-relative POSIX form, reject root-escaping links and include/holdout overlap, sort entries, and hash canonical JSON.

Each allowlist entry contains `source_repo`, `source_commit`, `source_path`, `target_path`, `kind`, `task_id|null`, and `sha256`. Global entries use one pinned `omp-config` commit. Task context entries use that task's pre-fix commit. The pack digest covers the ordered entry records and bytes.

Before freeze, resolve every manifest entry from `source_repo` at `source_commit`, read only `source_path`, recompute `sha256`, and compare the bytes. Bind the manifest digest to every enriched receipt. Fail if the commit, path, bytes, include set, or holdout set differs.

The stage manifest names one `omp_config_commit`. Every global allowlist entry must use that exact commit, and the pack validator must run before the manifest freezes. No later commit or working-tree byte is eligible.

Hold out OMP-specific settings, defaults, ladders, agents, stdio MCPs, extensions, presets, hooks, runtime libraries, themes, and cotenants.

The runner may allow only the fingerprinted MCP handshake. Any task-time MCP invocation fails the offline scope check. If a harness cannot expose the same MCP identity and contract, its enriched row stays blocked.

The common MCP exists for tool-registration and context parity. These offline tasks do not test MCP capability. A later full-without-MCP arm measures registration cost only.

Scan the pack for each task ID, reference text, changed identifiers, and task-specific answers. Reject a contaminated task or pack.

## Common limits

Adapters must enforce and attest:

- `max_turns`: 12 normalized assistant turns;
- `agent_timeout`: 15 minutes by an external monotonic clock;
- `task_network`: denied except the fingerprinted MCP handshake;
- `model_fallback`: denied;
- `product_retry`: zero;
- `transport_retry`: configured runner policy and recorded;
- `session_state`: clean;
- `task_image`: history-free export at the pre-fix SHA;
- `reference`, hidden grader, future git object, and eval-document access: denied.

Pi and OMP do not expose a common native turn cap. Prime's cap applies only in autonomous mode. The Runner Exchange adapters must count normalized events and stop the process. A cell cannot run before that control is proven.

The same task prompt and acceptance checks go to every controlled cell.

## Corpus

Workers may modify only named source paths. Tests and graders are immutable and outside the worker image.

### C1: generic parser repair

- ID: `iron-forest-go-checkruns-array`
- Repository: `misty-step/iron-forest`
- Pre-fix SHA: `e98569f48664759242b062a5a46910c03375c0ed`
- Reference SHA: `520c629d4987720e9533ae63e4478cd9479c6b78`
- Allowed source: `prs.go`
- Expected pack effect: none or negative.

Checks:

1. The check-run query emits one JSON array.
2. Two completed checks unmarshal as two records.
3. Failed names and conclusions are retained.
4. An empty array returns an empty result without a JSON error.
5. The hidden focused grader passes.

### C2: security boundary repair

- ID: `estate-pagination-origin`
- Repository: `misty-step/estate`
- Pre-fix SHA: `054020ba4929ce8794cbd7524865fdc155cc9ef7`
- Reference SHA: `c6e92b73ee69fb6ef56d349000f85fb8b70843ed`
- Allowed source: `src/collect/digitalocean.rs`
- Expected pack effect: security and scope rules can help.

Checks:

1. A same-origin relative link is accepted.
2. A same-origin absolute link is accepted.
3. A cross-origin absolute link is rejected.
4. A scheme-relative attacker link is rejected.
5. Rejection occurs before any request.
6. The hidden focused grader passes.

### C3: hydration-safe product state

- ID: `sploot-hydration-device-lane`
- Repository: `misty-step/sploot`
- Pre-fix SHA: `4a2a3d29831e4c8d22dc28130a062bda8f51b601`
- Reference source SHA: `1d5b3282a236996dbc4cf79ff4c9c4c5d2cb085c`
- Reference artifact: only the `empty-state.tsx` hunk; exclude the unrelated status-line hunk.
- Allowed source: `apps/web/components/library/empty-state.tsx`
- Expected pack effect: product and UI doctrine can help.

Checks:

1. The server snapshot uses the desktop lane.
2. Hydration produces no server-client markup mismatch.
3. An iPhone user agent selects the iPhone lane after hydration.
4. A desktop user agent keeps the Chrome extension lane.
5. The unrelated status-line source remains unchanged.
6. The hidden focused grader passes.

For each task, extract the reference artifact as the binary diff from pre-fix SHA to reference SHA restricted to `Allowed source`. Reject any other path and store the patch digest in the qualification receipt. Record a per-hunk scope justification that maps each retained hunk to a named check; reject an unmapped hunk. For C3, also restrict extraction to the named `empty-state.tsx` hunk.

## Grader qualification

Bench does not yet contain these three census task packages. Before running, materialize them beside the pinned Bench qualification pattern and add a campaign-owned validator. The validator emits one qualification receipt per task:

1. Apply the reference artifact to the history-free pre-fix image.
2. Confirm every hidden behavior and scope check passes.
3. Confirm the unchanged image fails the intended check.
4. Confirm at least two plausible wrong mutants fail.
5. Record immutable fixture, reference, grader, mutant, prompt, and scope digests.

A task without a clean qualification receipt cannot run. This missing validator is part of the runnable proof gate, not an existing Bench capability.

## Scoring

- `hard_pass`: every behavior, scope, and hidden grader check passes.
- `task_points`: passed checks / total checks for that task.
- `macro_objective_points`: mean of the three task scores.
- `quality_failure`: valid, matching trial with a non-passing outcome.
- `reliability_failure`: route, effort, provider, harness, transcript, timeout, fallback, or receipt failure.

Macro scoring gives each task equal weight despite different check counts. It diagnoses failures and never overrides hard-pass eligibility.

## Cost, latency, and receipt fields

Normalize each Runner Exchange outcome into one canonical normal Crucible task receipt with schema `harness_census.trial_receipt.v1`:

```text
schema_version, crucible_run_id, cell_kind, campaign_id, stage_manifest_digest, trial_id, source_cluster
task_id, task_digest, row_id|null, cohort_id|null, baseline_id|null, profile_digest
model_requested|null, effort_requested|null, provider_route_resolved|null, provider_effort_resolved|null
response_model_attestation|null, response_effort_attestation|null, response_identity_verified|null
default_resolution_source|null
harness, harness_version, composition, composition_digest, adapter_digest
system_identity|null, system_prompt_digest|null, context_digest, skill_digest, mcp_digest, tool_manifest_digest
trial_status, failure_class|null, failure_stage|null, failure_code|null, failure_detail_ref|null
hard_pass|null, task_points|null
input_tokens|null, cache_read_tokens|null, cache_write_tokens|null, output_tokens|null, reasoning_tokens|null
provider_worker_cost_usd|null, catalog_worker_cost_usd|null, grader_cost_usd|null
startup_ms|null, ttft_ms|null, tool_ms|null, worker_wall_ms|null, grader_ms|null, queue_ms|null, retry_ms|null
transport_retry_count, runner_exchange_request_ref|null, runner_exchange_result_ref|null
evidence_refs, transcript_ref|null, grader_receipt_ref|null
```

Materialize this contract as `campaign/schemas/trial-receipt-v1.schema.json` before the smoke. Digests are lowercase SHA-256 strings. Counts and millisecond fields are non-negative integers. USD fields are non-negative decimals. Reference fields use the content-addressed URI grammar above. The schema enforces every conditional rule below.

Keep worker cost, grader cost, latency phases, and reliability separate. Use external monotonic timing. Every attempted cell writes one typed receipt; never drop mismatches.

Controlled receipts require `row_id` and `cohort_id`. Reliability failures keep observed usage and timing fields and leave unavailable fields null.

For every controlled receipt, load its `row_id`, recompute the row and cohort IDs, and require requested identity, resolved identity, harness, composition, and campaign fields to match exactly. The receipt cannot override ledger identity.

Set `trial_status` to `success`, `quality_failure`, or `reliability_failure`. Reliability failures require `failure_class` from `route`, `effort`, `provider`, `harness`, `composition`, `transport`, `timeout`, `fallback`, `transcript`, `scope`, or `receipt`; require `failure_stage` from `launch`, `run`, `collect`, `grade`, or `persist`; and require a stable adapter `failure_code`.

A success requires `hard_pass: true`. A quality failure requires `hard_pass: false` and numeric `task_points`. Both set reliability failure fields null. A reliability failure sets both score fields null.

Controlled success and quality-failure receipts require both response attestations and `response_identity_verified: true`. The adapter proves that the attestations correspond to the resolved provider route and native effort. A failed proof is a reliability failure.

Success and quality-failure receipts require non-null Runner Exchange request, Runner Exchange result, transcript, grader receipt, and evidence references. Every reference is a content-addressed URI under the campaign root, and its digest must match before persistence. Reliability failures require every reference produced before the failure stage.

Every referenced JSON record embeds the same `campaign_id`, `trial_id`, `task_id`, and `row_id` or `baseline_id`. A trial evidence manifest binds non-JSON artifacts to those identities and their digests. Reject a digest-valid reference with mismatched identities.

The normal Crucible task receipt is the source of truth. Raw Runner Exchange request and result files are immutable referenced evidence, not second receipts. Reject duplicate `crucible_run_id` or `trial_id` values.

`hard_pass` and `task_points` derive only from the bound grader receipt. Common-limit and scope checks are grader inputs, not a second pass gate.

## Erasure gate

Preflight excludes blocked rows from execution, rejects duplicate exact aliases within one harness and composition, and rejects contaminated packs or unqualified tasks. These records stay visible in the ledger.

Write `erasure.json` with candidate kind, behavior-preserving oracle, planned trials and stored bytes before and after, erased counts, and reason. Evaluate exact route aliases, blocked inputs, saturated future tasks, redundant grader checks, and duplicate stored artifacts. Before this exhaustive census, the oracle permits only exact alias collapse or non-runnable input removal. The operator requires every unique confirmed row, so result-driven row erasure is forbidden. Later stages can remove ineligible cells through their preregistered rule.

## Run order

1. Pin harness, adapter, Crucible, model catalog, primitive pack, task, and grader digests.
2. Generate the controlled availability ledger and native-default metadata.
3. Qualify the pack, MCP, task references, graders, and mutants.
4. Run the three required native-default baselines.
5. Randomize controlled model-effort blocks.
6. Rotate harness and composition inside each block.
7. Run one isolated trial per confirmed task-cell pair.
8. Grade without model, effort, harness, composition, cost, or latency labels.
9. Persist one normal Crucible task receipt with immutable Runner Exchange request and result references.
10. Compare only shared confirmed task pairs.

## Comparison records

Every `harness_census.comparison.v1` record contains `campaign_id`, `stage_manifest_digest`, `model_requested`, `effort_requested`, `cohort_id`, `claim_scope`, exact task digests, row IDs and digests, trial IDs, receipt digests, harness versions, and composition digests.

A `cross_harness` record is valid only with exactly six unique confirmed rows whose campaign, requested identity, cohort, stage digest, resolved identity, and native effort match the record. It requires three valid task receipts per row with matching task and pack digests. It contains all three harnesses and both compositions. Each composition digest must be identical across its three harness rows. An incomplete or mismatched cohort can produce only a `product_local` record.

## Census decision

The controlled census separates eligible from ineligible or blocked cells.

All eligible cells may enter Stage 2. If the campaign budget cannot cover them, preregister a stratified selection rule before reading results. The rule must preserve models and harness compositions and must not use one-shot cost or latency differences.

Cells without three hard passes do not advance. Keep their partial points for diagnosis or a separately declared remediation run.

Native-default results remain a separate product baseline. Do not place them in controlled Pareto or paired tables.

Do not construct a global Pareto rank from these three one-shot tasks.

## Later-stage gate

Every later stage is a separate eval. Before Stage 2 or Stage 3 runs, publish a frozen manifest with:

- disjoint source-cluster partition;
- task IDs and history-free fixture digests;
- references and clean qualification receipts;
- exact hidden grader and scope digests;
- known-bad mutants;
- the rate, minimum effect of interest, and production retry policy.

Stage 4 also pins the eligible model-harness cells, pack manifests, development and held-out task splits, replications, selection rule, and decision thresholds.

A future model-judge manifest must also pin the judge version, human-labeled calibration set, fail-class precision and recall, position and format probes, and acceptance thresholds.

`stage-manifest.json` uses `harness_census.stage_manifest.v1`. It pins the Crucible and Bench repository commits, roster, catalog, harness, adapter, pack, MCP, task, grader, retry, and decision-policy digests. Every trial and comparison receipt binds its digest.

## Evidence

Store sanitized artifacts under the Crucible run directory:

```text
campaign/
  schemas/{availability-v1,availability-evidence-v1,trial-receipt-v1,baseline-summary-v1,comparison-v1,stage-manifest-v1}.schema.json
  stage-manifest.json
  availability.json
  availability-evidence/<row-id>.json
  erasure.json
  catalog.json
  harnesses.json
  compositions/{raw,enriched,native-default}/manifest.json
  baselines/<baseline-id>/summary.json
  tasks/<task-id>/{prompt,fixture-receipt,qualification-receipt,grader-receipt,mutant-manifest,scope-manifest}
  trials/<trial-id>/{runner-request,runner-result,receipt,evidence-manifest,transcript,artifact,grade}
  comparisons/
```

Every comparison query scopes one `campaign_id` and exact task digests. Never join rows across reruns.

Do not store credentials, environment values, customer data, raw private corpora, or future reference objects in worker images.

## Cadence

- Run this complete census once for one pinned roster, harness set, and primitive pack.
- Run a previously blocked row when its exact route or effort becomes available.
- Re-run affected rows after a model, harness, adapter, pack, task, or grader change.
- Retire saturated tasks and qualify replacements before the next complete census.

## Runnable proof gate

This design becomes runnable only when:

- the unavailable Gemini route is resolved or remains blocked;
- every harness has a content-addressed route-effort availability receipt;
- adapter-level turn, time, fallback, and identity enforcement passes;
- the pack validator proves each source commit, path, byte digest, include, and holdout entry;
- the common HTTP MCP identity and initialization are proven or affected enriched cells remain blocked;
- a Runner Exchange-backed Crucible agent runner writes normal per-task run rows;
- all three Bench qualification receipts are clean;
- `crucible validate` accepts the stage manifest and every machine-readable availability, evidence, trial, baseline, and comparison schema;
- one native-default smoke and one six-cell controlled smoke persist complete receipts.
