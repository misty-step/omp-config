# Model, effort, and harness gauntlet brain dump

Status: design draft, 2026-08-08.

Review `../global/skills/eval-design/references/harness-gauntlet-failure-modes.md` before changing this design.
This brain dump owns rationale, the requested roster, corpus evidence, and later experiment ideas. `model-harness-census-v0.md` owns mutable counts, tasks, fields, and gates.



## Decision

Select model, native reasoning effort, harness, and harness composition for recurring engineering work.

Keep quality, cost, latency, and reliability as separate decision vectors. Do not create one weighted leaderboard.

The first decision is only which cells receive more evaluation. Deployment requires a later representative confirmation set.

## Claims

Test one axis at a time:

1. Holding model, native effort, and harness fixed, does the portable primitive pack change outcomes?
2. Holding harness composition fixed, which model-effort routes produce better outcomes?
3. Holding model, effort, and composition fixed, which complete harness product performs better?
4. On selected cells, can a lean primitive pack retain quality while reducing cost or latency?

Prime, OMP, and Pi expose different native tools and orchestration. Cross-harness results are whole-product `config_delta` comparisons, not pure tool-neutral harness effects.

## Requested model census

The local `omp models --json --no-extensions` catalog was read on 2026-08-08. Prices are catalog USD per one million tokens. They are not invoices.

Reasoning labels are ordinal only within one route. `high` does not imply equal computation across models or harness adapters.

| Requested route | OMP catalog resolution | Native efforts | Input / output $/M |
|---|---|---|---:|
| `openai-codex/gpt-5.6-sol` | exact | low, medium, high, xhigh, max | 5.00 / 30.00 |
| `openai-codex/gpt-5.6-terra` | exact | low, medium, high, xhigh, max | 2.00 / 12.00 |
| `openai-codex/gpt-5.6-luna` | exact | low, medium, high, xhigh, max | 0.20 / 1.20 |
| `openrouter/deepseek-v4-flash-0731` | `openrouter/deepseek/deepseek-v4-flash-0731` | low, high, max | 0.09 / 0.18 |
| `google-antigravity/gemini-3.6-flash` | exact | minimal, low, medium, high | 1.50 / 7.50 |
| `google-antigravity/gemini-3.5-flash-lite` | blocked: no local Antigravity route | unknown | unknown |
| `xai-oauth/grok-4.5` | exact | minimal, low, medium, high, xhigh | subscription catalog reports 0 |
| `openrouter/zai/glm-5.2` | `openrouter/z-ai/glm-5.2` | minimal, low, medium, high, xhigh | 0.2058 / 0.6468 |
| `kimi-code/k3` | exact | low, high, max | subscription catalog reports 0 |
| `anthropic/claude-fable-5` | exact | low, medium, high, xhigh, max | 10.00 / 50.00 |
| `anthropic/claude-opus-5` | exact | low, medium, high, xhigh, max | 5.00 / 25.00 |
| `openrouter/meta/muse-spark-1.2` | exact | minimal, low, medium, high, xhigh | 1.25 / 4.25 |
| `openrouter/qwen/qwen3.8-max` | exact | minimal, low, medium, high, xhigh | 2.00 / 6.00 |
| `openrouter/poolside/laguna-s-2.1` | exact | minimal, low, medium, high | 0.09 / 0.18 |
| `openrouter/thinkingmachines/inkling` | exact | minimal, low, medium, high, max | 0.95 / 4.05 |
| `openrouter/sakana/fugu-ultra` | exact | high, xhigh, max | 5.00 / 30.00 |
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b` | exact | medium, high | 0.60 / 3.60 |
| `openrouter/minimax/minimax-m3` | exact | minimal, low, medium, high | 0.30 / 1.20 |

The OMP catalog confirms 73 requested model-effort routes. The missing Gemini route has an unknown effort set.

Prime's inspected DeepSeek mapping does not preserve every OMP label. Pi's current catalog lacks several exact routes. The canonical census specification keeps unresolved requests visible and blocks unsupported comparisons.


## Third harness

The operator confirmed that the third coding harness is Pi. Local `/usr/bin/pipewire` is an unrelated Linux multimedia service.

The installed Pi 0.83.0 CLI has the expected model, effort, context, skill, MCP, and JSON controls.

Observed versions:

- Prime Agent 0.7.0;
- OMP 17.2.11;
- Pi 0.83.0.

## Pilot rationale

The canonical design specification is `../global/skills/eval-design/evals/model-harness-census-v0.md`.

The known roster produces 1,314 controlled trials plus nine native-default trials. The unresolved Gemini sentinel adds no runnable trial.

The pilot spans a generic boundary repair, a security-context repair, and a product-state repair. This diversity probes harness sensitivity without claiming deployment rank.

## Corpus evidence

Eight Luna-head architect lanes examined Iron Forest, Cantrip, Powder, Mint, Crucible, Linejam, Sploot, Misty Step, Vox, Kelpie, Overmind, OMP, Pi, Estate, Sanctum, Finances, Canary, Bench, and harness parity.

The lanes found bounded historical tasks covering parsers, state machines, lifecycle, security, UI state, accessibility, configuration, and review gates. Each candidate needs independent fixture and mutant qualification before promotion.

Bench already has seven Seam Agency Harbor tasks with reference solutions, alternate solutions, and mutants. These are useful for later clean-room confirmation, not as substitutes for real historical failures.

Later stages need independent frozen manifests with disjoint task clusters and complete fixture, reference, grader, mutant, and scope evidence.

## Later experiment ideas

Use a separate representative screen after the census, then confirm selected cells on a larger held-out corpus with replication.

A later lean-pack eval can compare raw, rules-only, implementation-core, task-matched, portable-full, and full-without-MCP packs. Use `skill://skill-eval` for unresolved individual skills.

Put OMP agents, extensions, hooks, presets, runtime libraries, and delegation topology in a separate native-full `config_delta` study.

## Measurement rationale

Keep quality, cost, latency, and reliability separate. The canonical specification owns every metric, field, and gate.

## Existing infrastructure and missing seam

Repository `misty-step/crucible` commit `72ccda8c4ffa884b70d67fa9216fed73cfa0f2b0` supplies Runner Exchange under `src/`. Repository `misty-step/bench` commit `aad2f8b47570dd9544c38cf2208e5b456ff0e455` supplies the pattern under `benchmarks/seam-agency-v0/`. The canonical stage manifest binds both identities and commits.

Runner Exchange records are not yet normal EvalSpec task rows and do not feed compare, history, or pivot. The minimum change is one deep interface:

```text
run(
  cell: frozen confirmed availability row,
  task: qualified image, prompt, limits, and digests
) -> crucible.runner_exchange_result.v1
```

The runner converts those inputs into `crucible.runner_exchange_request.v1`. It rejects identity mismatches before successful-result persistence and writes a typed failure receipt. One Crucible agent runner owns this interface. Three private adapters translate Prime, OMP, and Pi into normalized results. Add no service, scheduler, statistics package, or dashboard.

## Open facts

- Resolve `google-antigravity/gemini-3.5-flash-lite` without changing provider.

The canonical census specification owns every other blocker and the runnable proof gate.
