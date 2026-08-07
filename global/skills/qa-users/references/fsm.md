# qa-users FSM

Fixed protocol for persona QA.
Owner kit: `skill://qa-users`. Agents: `qa-master` → `qa-persona`; chief writes tracker.
Narrative twin: `lifecycle.md`. Tests: `tests/test_protocol_fsms.py` and qa-users integrity scripts.

## States

| State | Owner | Mark |
|---|---|---|
| `explore` | qa-master | product evidence; no frozen input |
| `minted` | qa-master | persona briefs with mission, knowledge, blind_spots |
| `frozen` | qa-master | validated `input.v1` (semantic + fixtures) |
| `dispatching` | qa-master | one browser-only persona task per frozen persona |
| `evidence` | qa-master | persona results in; findings not final |
| `reproducing` | qa-master | smoke/repro browser only for candidate findings |
| `rca_optional` | qa-master | read-only after confirmed reproduction |
| `synthesized` | qa-master | `output.v1` packet validated |
| `chief_write` | chief | tracker/PR/ledger after packet |
| `handoff_optional` | chief | `fix-and-pr` only with explicit auth |
| `halt_dry` | qa-master | stopped after freeze (dry run) |
| `failed` | any | blocked safety or validation error |

## Legal transitions

| From | Event | To |
|---|---|---|
| `explore` | mint personas from evidence | `minted` |
| `minted` | validate and freeze `input.v1` | `frozen` |
| `frozen` | dry run stop | `halt_dry` |
| `frozen` | dispatch personas | `dispatching` |
| `dispatching` | all personas return or fail with reason | `evidence` |
| `evidence` | reproduce candidate friction | `reproducing` |
| `reproducing` | optional RCA | `rca_optional` |
| `reproducing` / `rca_optional` | synthesize packet | `synthesized` |
| `synthesized` | chief tracker write | `chief_write` |
| `chief_write` | authorized fix-and-pr | `handoff_optional` |

## Illegal transitions

- dispatch or persona spawn before `frozen`
- environment `production` or unknown at freeze
- `qa-persona` with tools other than `browser`
- `qa-persona` tracker/issue/PR/source inspection
- full persona mission on `qa-master` browser (smoke/repro only)
- tracker create from master or persona (chief only after packet)
- `fix-and-pr` inside persona session or before read-back
- RCA before confirmed reproduction
- output persona set ≠ frozen selected persona set

## Process proof

Changes to this lifecycle need process-adversarial coverage:
`global/references/process-adversarial-testing.md`.
