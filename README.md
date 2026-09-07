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
| `global/AGENTS.md` | Collaboration, task boundaries, communication, privilege/approval routing, and inspectable verification evidence |
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

For an instruction-only change, deploy just the four `global/` guidance files:

```sh
OMP_INSTALL_GUIDANCE_ONLY=1 ./install
```

This leaves models, configuration, MCP credentials, skills, agents, themes,
extensions, and hooks unchanged. It also avoids replacing live skills installed
by another owner. The same environment flag can prefix `git push` when its
pre-push hook should deploy guidance only; secret scans still run. The default
full install behavior is unchanged. Invalid flag values fail without deploying.

## Privilege and approval

The standing routing policy lives in `global/AGENTS.md`. On a Linux workstation,
use the channel where the operator can approve the actual operation:

| Situation | Route |
| --- | --- |
| Operator can approve on the local desktop; agent has no accessible terminal | `pkexec` for the explicit executable and arguments |
| Operator can authenticate in a real terminal, including an SSH terminal | Normal `sudo` in that terminal |
| Job must run with nobody available to approve | `sudo -n` under an existing explicit host grant; otherwise retain the pending action |

For example, `pkexec /usr/bin/id -u` is a harmless approval-path check; a
successful invocation prints `0`. For real work, request the intended operation
instead of repeatedly probing privileges. Announce why it needs root. In OMP,
supervise an approval-waiting process with `hub`, then check its exit and the
requested system state. Process creation alone is not completion.

`pkexec` uses the registered authentication agent. Without one it can fall back
to a text agent; `--disable-internal-agent` disables that fallback when no text
prompt is usable. It does not make authentication unnecessary. Do not redirect
an SSH user's request into a desktop dialog they cannot see. Its environment is
sanitized, so use absolute paths and explicit inputs rather than relying on
shell exports or launching graphical applications as root. See the
[pkexec manual](https://www.freedesktop.org/software/polkit/docs/latest/pkexec.1.html).

Being physically away is not the same as being unattended: an operator can
approve through an SSH terminal. However, `sudo -v` in that terminal does not
necessarily authorize an agent's separate PTY or background process. Do not
copy passwords into chat, `sudo -S` payloads, environment variables, or files.

Genuinely unattended administration needs an explicit OS policy, not another
prompt wrapper. Account-wide `NOPASSWD` provides full administration to every
process under that account, not only a trusted agent. A narrower policy needs
root-owned helpers with constrained actions and arguments; allowlisting a
general shell or arbitrary package installation is not narrow privilege.
This repository documents routing, but does not install sudoers or polkit
grants. Such a change needs a separate decision, syntax validation, an
independent execution check, and a rollback path.

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
