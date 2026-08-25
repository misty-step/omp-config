# omp-config

Omp harness configuration for Phaedrus / Misty Step. Source of truth for how
agents run on this machine: model roles, global policy, skills, themes.
`./install` deploys everything.

## Layout

| Path | Purpose |
| --- | --- |
| `install` | Deployment script. Validates sources, copies the allowlist into `$(omp config path)`, deploys agents, skills, and shared review references atomically, merges live MCP auth, and self-installs the pre-push hook |
| `config.yml` | Model roles and fallback chains, theme/statusline/TUI display, providers (web search routed through exa), task/LSP settings |
| `models.yml` | Local Ollama provider discovery; cloud models come from omp's bundled catalog |
| `mcp.json` | Declared MCP servers; `install` merges per-server auth/oauth from the live copy |
| `global/AGENTS.md` | Standing policy loaded into every session: design, communication, delivery, premise gate, knowledge vault |
| `global/RULES.md` | Strict ordering rules; currently the deletion-first ladder |
| `agents/` | Read-only specialist agents; installed globally and routed by each agent's model role |
| `global/WATCHDOG.md`, `WATCHDOG.yml` | Closeout reviewer: a second model audits finished work against accepted intent; advisor roster configured in YAML |
| `themes/` | TUI themes (`tokyonight`, `ember`) |
| `skills/` | Skill packages, copied wholesale on install — see below |
| `references/review/` | Shared council contract and lens references used by operator-invoked delivery and review skills |
| `.githooks/pre-push` | Hook source installed into this repo's git dir by `./install` |
| `.agents/skills/writing-for-agents/` | Agent-writing guidance served via `skill://writing-for-agents`; not deployed by `install` |
| `extensions/`, `.omp/` | Reserved; currently empty |
| `CANON.md` | Operating philosophy: principles with stable IDs plus synthesis and deviation ledgers. Reference only — never deployed, never auto-loaded |

## Install

```sh
./install   # requires jq
```

Checks every allowlisted source exists and parses, deploys config files with
mode 600, folds live MCP credentials into declared servers, swaps `skills/`
atomically, and installs the git hook. Run after every change; sessions pick
up deployed state on their next start.

## Skills

Two invocation classes:

Operator-invoked (`disable-model-invocation: true`) — heavyweight or
attention-consuming flows that fire only on explicit request:
`audit-choices`, `audit-observability`, `audit-simplifications`, `brief`, `brief-complete`,
`brief-decision-ready`, `brief-editor`, `brief-editorial`,
`brief-reader-test`, `capture`, `code-review`, `deliver`, `diagnose`,
`explore-design`, `explore-unknowns`, `extract-module`, `foundation`,
`install-anti-slop`, `polish`, `product-description`, `pulse`, `refactor`,
`release`, `security-review`, `shape`, `tidy`, `torvalds-design-review`.

Model-invocable — unambiguous triggers, bounded cost, cheap wrong-fire:
`ast-grep`, `dispatch`, `evidence-packet`, `exocortex`, `frontend-design`,
`herdr`, `research`, `watch-deploy`.

The split criterion lives in `CANON.md`, Synthesis policy.

## Canon relationship

`CANON.md` states the operating philosophy; `global/` and `skills/` are
deliberate compiled views of it. Harness changes cite canon IDs, the
synthesis ledger records what is embodied where, and the deviation ledger
captures reality beating a rule. Never paste canon wholesale into harness
context — synthesize one principle at a time, trial it, keep or drop.

## Ecosystem

- **Powder** — work ledger for all Misty Step work; skill managed in `misty-step/powder` and scoped to `~/Development/misty-step/` via workspace discovery.
- **Iron Forest** — headless Builder/Verifier/Fixer factory. Mechanical
  enforcement belongs there and in CI, not in prose.
- **Landmark** — release pipeline: conventional commits become semantic
  versions, technical changelogs, synthesized user-facing notes, and
  machine-readable evidence.
- **Estate** — private infrastructure map; consult before any infrastructure
  claim.
