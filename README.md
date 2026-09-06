# omp-config

Omp harness configuration for Phaedrus / Misty Step. Source of truth for how
agents run on this machine: model roles, global policy, skills, themes.
`./install` deploys everything.

Shared prompting follows the [GPT-6 Astra prompting guide](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md#prompting-best-practices):
complete intended work, ask focused questions, delegate useful independent work,
write plainly, and stop verification when the relevant checks pass.

## Layout

| Path | Purpose |
| --- | --- |
| `install` | Deployment script. Validates sources, copies the allowlist into `$(omp config path)`, deploys agents and skills atomically, merges live MCP auth, and self-installs the pre-push hook |
| `bin/omp-grievances.ts` | Manual grievance inbox CLI; reads OMP intake without mutation and stores private acknowledgements under XDG state |
| `config.yml` | Model roles and fallback chains, theme/statusline/TUI display, providers (web search routed through exa), task/LSP settings |
| `models.yml` | Local Ollama provider discovery; cloud models come from omp's bundled catalog |
| `mcp.json` | Declared MCP servers; `install` merges per-server auth/oauth from the live copy |
| `global/AGENTS.md` | Astra-guided follow-through, communication, delegation, verification, and local operational boundaries |
| `agents/` | Read-only specialist agents; installed globally and routed by each agent's model role |
| `global/WATCHDOG.md`, `WATCHDOG.yml` | Continuous Steward advisor: a high-reasoning model reviews intent, design, correctness, proof, and operations; roster configured in YAML |
| `themes/` | TUI themes (`tokyonight`, `everforest`, `everforest-light`) |
| `skills/` | Skill packages, copied wholesale on install — see below |
| `.githooks/pre-push` | Hook source installed into this repo's git dir by `./install` |
| `.agents/skills/writing-for-agents/` | Agent-writing guidance served via `skill://writing-for-agents`; not deployed by `install` |
| `extensions/loc/` | Session-resident LOC status and commands; deployed by `install` |
| `CANON.md` | Concise, implementation-independent operating philosophy. Reference only — never deployed or auto-loaded |

## Install

```sh
./install   # requires jq, bun, and omp
```

Checks every allowlisted source exists and parses, deploys config files with
mode 600, folds live MCP credentials into declared servers, swaps `skills/`
atomically, and installs the git hook. Run after every change; sessions pick
up deployed state on their next start.

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

## Skills

Skill frontmatter declares whether a skill is operator-invoked
(`disable-model-invocation: true`) or available to the model. The packages in
`skills/` are the current inventory.

### Provenance: External vs Homebrew

- **External skills** (`frontend-design` from Anthropic, `show-me` from HumanLayer, `audit-choices` and `eli5` from `dzhng/skills`, `wrangler` from Cloudflare, `find-bugs` from Sentry, `herdr` from `herdr.dev`, `ast-grep` from `ast-grep`): keep upstream contents verbatim.
- **Homebrew skills** (`custom-linters`, `dispatch`, `evidence-packet`, `research`, etc.): Misty Step native, actively maintained and kept lean.

When evaluating an external skill, pull it completely or write a distinct homebrew skill. Do not pull a popular external skill and then rewrite it into local dialect.

`eli5` supplies the dependency referenced by `audit-choices`; its source is
[`dzhng/skills` at `3631529b7305eec8dd08b3a827f4d8c16342a29a`](https://github.com/dzhng/skills/blob/3631529b7305eec8dd08b3a827f4d8c16342a29a/skills/engineering/eli5/SKILL.md).

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
