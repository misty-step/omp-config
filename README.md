# omp-config

Omp harness configuration for Phaedrus / Misty Step. Source of truth for how
agents run on this machine: model roles, global policy, skills, themes.
`./install` deploys everything.

The harness favors engineering judgment, first-principles simplification, and
visible proof over workflow recipes. Standing guidance explains our preferences;
skills retain only useful domain knowledge or a distinct requested outcome.

## Layout

| Path | Purpose |
| --- | --- |
| `install` | Deployment script. Checks required sources, copies the allowlist into `$(omp config path)`, replaces deployed agents and skills, merges live MCP auth, and self-installs the pre-push hook |
| `bin/omp-grievances.ts` | Manual grievance inbox CLI; reads OMP intake without mutation and stores private acknowledgements under XDG state |
| `config.yml` | Model roles and fallback chains, theme/statusline/TUI display, providers (web search routed through exa), task/LSP settings |
| `models.yml` | Local Ollama provider discovery; cloud models come from omp's bundled catalog |
| `mcp.json` | Declared MCP servers; `install` merges per-server auth/oauth from the live copy |
| `global/AGENTS.md` | Collaboration, task boundaries, communication, and inspectable verification evidence |
| `global/RULES.md` | Engineering taste, simplification, stack and operational preferences |
| `agents/executive.md` | Sustained operator-directed execution through the native `@task` model route |
| `global/WATCHDOG.md`, `global/WATCHDOG.yml` | One read-only Steward advisor; independent design and evidence judgment without catch-up waits |
| `themes/` | TUI themes (`tokyonight`, `everforest`, `everforest-light`) |
| `skills/` | Skill packages, copied wholesale on install — see below |
| `.githooks/pre-push` | Hook source installed into this repo's git dir by `./install` |
| `extensions/loc/` | Session-resident LOC status and commands; deployed by `install` |
| `CANON.md` | Concise, implementation-independent operating philosophy. Reference only — never deployed or auto-loaded |

## Install

```sh
./install   # requires jq, bun, and omp
```

Checks every allowlisted source exists, validates declared JSON, deploys config
files with mode 600, folds live MCP credentials into declared servers, replaces
the staged skills and agents, and installs the git hook. Run after configuration
changes; new sessions discover the deployed state.

## LOC extension

The globally deployed LOC extension provides `/loc`, `/loc-trend`, and a
committed-`HEAD` status row across repositories. When `.git/loc_cache` is missing
or stale relative to `HEAD`, an in-process async worker populates it in the background
without blocking interactive turns. Explicit LOC commands also populate the cache on demand.

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
omp-grievances ack 294 --outcome ticketed --ref HAB-123
omp-grievances ack --through 250 --outcome historic --note "pre-ledger backlog"
omp-grievances unack 294
```

Outcomes are `ticketed`, `no-action`, and `historic`. `ticketed` requires an
opaque external reference such as a Habitat item. The ledger stores
grievance IDs, outcomes, references, and notes; raw reports remain owned by
`~/.omp/autoqa.db`. A salted source fingerprint prevents acknowledgements from
silently attaching to a replaced or rewritten grievance history.

## Skills and agents

Three homebrew skills remain, all explicitly requested:

| Command | Outcome |
| --- | --- |
| `/skill:foundation` | Reassess product purpose, backlog, architecture, and development and operational foundations; recommend a coherent direction without making changes |
| `/skill:now-next` | Explain current reality, causes, work, health, evidence gaps, and worthwhile next directions |
| `/skill:capture` | Save durable findings to project notes, or the required tracker, without duplicating or claiming work |

`disable-model-invocation: true` hides these descriptions from the automatic
skill index. It does not prevent an explicit `skill://` read or grant authority
to act. Read-only requests remain read-only.

`foundation` is an investigation and design proposal, not an implementation
pass. It distinguishes an ideal destination from a practical transition.
Invoke `/skill:foundation` with any context or constraints the repository
cannot supply; select the model separately. Backlog changes and implementation
remain separately authorized work.

Five vendored packages remain unchanged: `ast-grep`, `frontend-design`, `herdr`,
`show-me`, and `wrangler`. Update them from upstream or remove the whole package;
use a distinctly named homebrew skill for different behavior. Omarchy's
`omarchy` and `diagnose-crash` retain their own owners and discovery paths;
this installer does not replace them.

Ask OMP to use the `executive` agent for a supplied direction and stopping
condition when sustained iteration is useful. It uses the existing `@task`
route. OMP's loop or a separately configured scheduler owns cadence and lifetime;
the agent does not install its own loop.

## Interactive and recurring work

The fast default model and native model roles/fallbacks remain in `config.yml`.
Use `omp` for the default or `omp --model @slow` for a deliberate Astra session.
Exa remains the configured web-search provider.

PR review, security scanning, release automation, and recurring repository
work belong to separately configured systems with their own triggers, scope,
credentials, and evidence. There are no review or delivery skill entry points
here. The bundled OMP reviewers remain available for explicitly requested work;
this configuration installs no review service, cron job, or provider integration.

`Steward` remains a read-only observer, not a release gate. Its native
`advisor.syncBacklog: "off"` setting avoids waiting for catch-up while preserving
background review and ordinary advice delivery.

## Canon relationship

`CANON.md` states the implementation-independent operating philosophy.
Configuration, standing policy, and skills are concrete mechanisms that should
express it without turning the canon into an inventory of the current harness.
Implementation details and routing live in this README and the configuration.
Never paste the canon wholesale into agent context; distill only the judgment a
surface needs.

## Ecosystem

- Personal and Misty Step work proceeds from current operator requests, with
  durable context in project notes. R90 projects continue to use Habitat.
- **Iron Forest** — headless Builder/Verifier/Fixer factory. Mechanical
  enforcement belongs there and in CI, not in prose.
- **Landmark** — release pipeline: conventional commits become semantic
  versions, technical changelogs, synthesized user-facing notes, and
  machine-readable evidence.
