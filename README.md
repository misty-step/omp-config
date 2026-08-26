# omp-config

Omp harness configuration for Phaedrus / Misty Step. Source of truth for how
agents run on this machine: model roles, global policy, skills, themes.
`./install` deploys everything.

## Layout

| Path | Purpose |
| --- | --- |
| `install` | Deployment script. Validates sources, copies the allowlist into `$(omp config path)`, deploys agents, skills, and shared review references atomically, merges live MCP auth, and self-installs the pre-push hook |
| `bin/omp-grievances.ts` | Manual grievance inbox CLI; reads OMP intake without mutation and stores private acknowledgements under XDG state |
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
| `extensions/loc/` | Session-resident LOC status and commands; deployed by `install` |
| `CANON.md` | Operating philosophy: principles with stable IDs plus synthesis and deviation ledgers. Reference only — never deployed, never auto-loaded |

## Install

```sh
./install   # requires jq
```

Checks every allowlisted source exists and parses, deploys config files with
mode 600, folds live MCP credentials into declared servers, swaps `skills/`
atomically, and installs the git hook. Run after every change; sessions pick
up deployed state on their next start.

## LOC extension

The globally deployed LOC extension provides `/loc`, `/loc-trend`, and a
committed-`HEAD` status row. Session and turn hooks read `.git/loc_cache` only;
a missing or stale cache hides the row rather than calculating during
interactive work. Explicit LOC commands may calculate on demand.

Disable only LOC for a large repository with project-local configuration:

```yaml
# .omp/config.yml
disabledExtensions:
  - extension-module:loc
```

## Grievance inbox

`omp-grievances` treats OMP's grievance database as a read-only inbox. Its
acknowledgement ledger defaults to
`$XDG_STATE_HOME/omp-config/grievances.sqlite3` or
`~/.local/state/omp-config/grievances.sqlite3`.

```sh
omp-grievances status
omp-grievances inbox --limit 20
omp-grievances show 294
omp-grievances ack 294 --outcome ticketed --ref POW-123
omp-grievances ack --through 250 --outcome historic --note "pre-ledger backlog"
omp-grievances unack 294
```

Outcomes are `ticketed`, `no-action`, and `historic`. `ticketed` requires an
opaque external reference such as a Powder or Habitat item. The ledger stores
grievance IDs, outcomes, references, and notes; raw reports remain owned by
`~/.omp/autoqa.db`. A salted source fingerprint prevents acknowledgements from
silently attaching to a replaced or rewritten grievance history.

## Skills

Two invocation classes:

Operator-invoked (`disable-model-invocation: true`) — human-directed flows
that run only on explicit request:
`audit-choices`, `audit-observability`, `audit-simplifications`, `backlog`,
`brief`, `brief-complete`, `brief-decision-ready`, `brief-editor`,
`brief-editorial`, `brief-reader-test`, `capture`, `code-review`, `deliver`,
`diagnose`, `explore-design`, `extract-module`, `foundation`, `groom`,
`install-anti-slop`, `polish`, `product-description`, `pulse`, `refactor`,
`release`, `security-review`, `shape`, `tidy`, `torvalds-design-review`.

Model-invocable — unambiguous triggers, bounded cost, cheap wrong-fire:
`ast-grep`, `dispatch`, `evidence-packet`, `exocortex`, `frontend-design`,
`herdr`, `research`.

The split criterion lives in `CANON.md`, Synthesis policy.

The `exocortex` skill is generated from `misty-step/exocortex`
`skills/exocortex/SKILL.md`. Do not hand-edit `skills/exocortex/SKILL.md`.
Regenerate with that repo's `scripts/install-skill.sh` and prove with
`skills/exocortex/check-source.sh`.

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
