# Orchestration — the multi-agent loop

The loop uses a team of subagents that converge on the oracles. It is not a
fixed pipeline. Use the lane cards below. Compose `/groom`'s
`references/investigation-bench.md` for recon work.

## Build-order discipline (read first)

Use model-driven, ad-hoc fan-out first. Under the harness-engineering contract, do not write a deterministic orchestration-workflow template before telemetry shows a recurring pattern. "Build one only after telemetry shows the pattern recurring; never pre-author." Building the large deterministic harness on day one creates the deterministic-scaffold failure mode. This repo repeats that failure mode.

Name the orchestration substrate by **capability**. This lets the skill work across harnesses:

- Harness with a large-scale background-orchestration feature (for example, a Workflow tool with `pipeline`/`parallel`/loop-until-dry): use it for the verify loop after the pattern recurs. It fits generate→verify→iterate across many pages.
- No such feature: use parallel native subagents or a `/sprites` fleet for heavy runs. A harness without the accelerator loses nothing it cannot do by hand.

Set agent count to repo size and ambition. `log` any coverage cap (top-N modules, sampled history) so an unreported limit cannot look complete.

## Lanes

Each lane is outcome-shaped. The lane agent owns its decomposition. Give it an end state, scope boundary, and output shape, not atomized steps.

### Recon swarm (parallel, lens-blind)

The chief dispatches one `researcher` lane per lens. Each lens stays independent, so one search angle cannot imply full coverage:

- **entry-points** — main/handlers/CLI/jobs/cron; where execution begins.
- **data-flow** — how data moves and persists.
- **dependency-graph** — module/package coupling and boundaries.
- **config + infra** — env, flags, deploy topology, CI.
- **tests-as-spec** — what tests assert the system *should* do.
- **git-why** — history, ADRs, and comments for non-obvious decisions and lore.

Output: a structured repo map per lens. Merge the maps into one map for planning.

### IA planner (single synthesizer)

Input: the merged repo map. Output: the page tree and diagram set, chosen from
`references/information-architecture.md` types and adapted to the system shape.
Decide which subsystems need a deep page or a stub. The coverage oracle checks
this plan against the real surface before generation.

### Page generators (pipeline, facet-scoped)

One agent writes each page. Give it only the context it needs. Work in
dependency order (overview before deep-dives so deep pages can cross-link up).
Use a pipeline, not a barrier: page B can draft while page A is verified. Each
generator stamps provenance (`templates/page.md`).

### Verifiers (adversarial, per oracle)

- **Accuracy skeptics** — fresh-context agents from a decorrelated model family refute each claim against source. Give them only the page and repo, never the author's reasoning trail.
- **Cold-reader navigator** — sees only the docs and real tasks. It names the files it would open. Misses are IA bugs.

Findings feed back to generation. Iterate until the loop-until-dry stop rule in `references/oracles.md` is met.

### Render + stamp (final)

One generation produces md source, HTML, and mermaid (`references/render-contract.md`). Run the render oracle, refresh provenance and `verified` stamps, then commit.

## Canonical shape (when the Workflow asset is eventually built)

Pipeline by default — each page verifies as soon as it is generated, so accuracy
checks on early pages overlap generation of later ones. Barrier only where a
stage genuinely needs all prior results: dedup the merged repo map before
planning; early-exit if recon found nothing to document. Keep this as guidance
for the future asset, not a script committed now.
