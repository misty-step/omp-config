# eval-design: how the design plugs into Crucible

The skill is the design front-end; Crucible is the enforcement + evidence
engine. This skill decides *what* to measure and *how* to grade and align the
judge; Crucible enforces the statistics and persists the evidence. Never
re-implement the statistics in prose; point into Crucible. Read Crucible's
`SKILL.md` for the exact command contract.

| Design step | Crucible surface |
|---|---|
| author the spec from the design | `crucible author` (flags or `--interactive`) |
| import an externally-authored eval | `crucible import <adapter> <source>` (promptfoo today) |
| gate the spec before it runs | `crucible validate` / MCP `crucible_validate` — refuses unsupported aggregation/uncertainty/missing grader; warns when task count can't resolve `min_effect_of_interest` |
| run + compare across model/harness/env | `crucible run <spec> --env A --env B` (first `--env` = baseline) |
| model-judge + calibration | `agentic_judge` runner: live judge, `CalibrationRecord` (fail-class precision/recall, per-family scope, κ), reasoning-first tail-anchored verdict, `format_sensitivity_flip_rate` |
| judge-gaming defense | the canary that hard-refuses a run if the judge rubber-stamps a known-bad candidate |
| trust gate | `run_records.trusted` — a locked/unmeasured judge run can't back a comparison or a Signal finding |
| interval + paired noise-floor + attribution | `crucible runs compare` — `paired`, `resolution` (q + MDE), `diagnosis`, attribution label (`model_delta`/`harness_delta`/`config_delta`), `--strict` |
| durable ledger + trace | `crucible runs list/show/compare/history/pivot`; `trace_path` for judge runs |

The runnable proof of a finished design is the Crucible loop: `crucible
validate` clean → `crucible run` produces persisted records → `crucible runs
compare` returns a paired `resolution` that can actually detect the effect you
care about, or honestly reports it can't.
