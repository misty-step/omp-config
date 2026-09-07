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
| `install` | Deployment script. Deploys all components or an explicit selection into `$(omp config path)`, merges live MCP auth, and preserves unselected components |
| `bin/omp-grievances.ts` | Manual grievance inbox CLI; reads OMP intake without mutation and stores private acknowledgements under XDG state |
| `config.yml` | Model roles and fallback chains, theme/statusline/TUI display, providers (web search routed through exa), task/LSP settings |
| `models.yml` | Local Ollama provider discovery; cloud models come from omp's bundled catalog |
| `mcp.json` | Global MCP inventory; Linear is deliberately absent |
| `workspace-mcp.json`, `bin/omp-install-scopes.ts` | Linear's approved directory scopes and native project-local imports; retires the global Parlor skill |
| `global/AGENTS.md` | Collaboration, bounded judgment, PR evidence, Linear/Habitat routing, and privilege/approval boundaries |
| `global/RULES.md` | Engineering taste, professional naming, operational preferences, and functional visual design |
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

For a focused update, select only the components that changed:

```sh
OMP_INSTALL_COMPONENTS=guidance ./install
OMP_INSTALL_COMPONENTS=mcp ./install
OMP_INSTALL_COMPONENTS="guidance mcp scopes skill:capture" ./install
```

Supported components are `guidance`, `mcp`, `scopes`, and
`skill:<source-directory-name>`. Unset selection means `all`, which retains
the full replacement behavior above and installs the approved directory scopes.
`all` cannot be combined with another component. Empty, unknown, missing-skill,
and invalid-name selections fail before deployment. The retired
`OMP_INSTALL_GUIDANCE_ONLY` variable fails with migration instructions rather
than silently triggering a full install.

Scoped deployment preserves unselected skills and other components. A selected
skill package is replaced, not overlaid, so obsolete files cannot survive inside
it. MCP deployment still uses the declared server inventory and preserves live
`auth`/`oauth` metadata for those servers; it is not a merge of undeclared servers.
OMP's managed OAuth tokens remain in its auth storage, never in this repository.

The same `OMP_INSTALL_COMPONENTS` environment variable can prefix `git push`
when its pre-push hook should deploy selectively; secret scans still run.
Use scoped deployment when live skills have another owner, such as `todoist-cli`,
rather than replacing their packages with a full install. The `scopes` component
explicitly removes the retired global Parlor copy; its owner now imports it into
consuming repositories instead.

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
opaque external reference such as a Linear or Habitat item. The ledger stores
grievance IDs, outcomes, references, and notes; raw reports remain owned by
`~/.omp/autoqa.db`. A salted source fingerprint prevents acknowledgements from
silently attaching to a replaced or rewritten grievance history.

## Linear

Use the [official Linear MCP server](https://linear.app/docs/mcp) for access and
the existing `/skill:capture` for capture judgment. The connector is not a
scheduler, authorization to start work, or a second system-documentation store.

`workspace-mcp.json` owns `https://mcp.linear.app/mcp`. `install` deploys it only
under `~/development/misty-step/.omp/mcp.json` and
`~/development/moomooskycow/.omp/mcp.json`; global `mcp.json` does not declare it.
The existing Misty Step workspace/team is the initial destination. Resolve actual
work records from Linear before writing; a separate Personal team remains deferred.

OMP's native MCP discovery is cwd-local, not ancestor-inherited. The `scopes`
installer adds a relative `.omp/.mcp.json` import in each existing direct-child
Git checkout under those two roots. It leaves a primary `.omp/mcp.json` untouched,
refuses conflicting fallback files or symlinked configuration directories, and
adds its local import to Git's `info/exclude`. R90 and other development trees
receive no definition or import. Re-run `OMP_INSTALL_COMPONENTS=scopes ./install`
after adding a checkout. Launch OMP from the repository root; an arbitrary nested
working directory does not inherit its MCP definition. `OMP_DEVELOPMENT_ROOT`
exists for alternate local layouts and isolated installer checks.

After deployment, run these **inside OMP**, not in the shell:

```text
/mcp reload
/mcp test linear
```

New sessions discover the local definition. Already-running sessions retain their
loaded tools until reloaded or restarted. Authorize only from an approved scope:

```text
/mcp reauth linear
```

Select the intended workspace. OAuth credentials remain in OMP's managed auth
storage, not in this repo. Directory scoping prevents normal connector discovery;
it is not a credential sandbox against another process under the same account.
Use separate OMP profiles when credential isolation is required.

### Authentication recovery

`/mcp reload` rediscovers configuration; `/mcp reconnect linear` reconnects an
existing binding. If an existing session reports `HTTP 401 invalid_token` after
authorization completed in another OMP process, use `/mcp reauth linear` in the
failing session. That recovery was observed during setup; the underlying runtime
cause is unconfirmed. Do not repeat a reported failure merely to confirm it or
add a hard-coded token-header workaround. Team creation is not exposed by the
current server; use Linear's settings for that administration.

Work conventions and project navigation live in the
[Misty Step work tracking guide](https://linear.app/misty-step/document/misty-step-work-tracking-guide-d3a627ae6395)
and [omp-config project](https://linear.app/misty-step/project/omp-config-47a74679f980).
Keep procedures and version-bound knowledge here; link them from work records.
Check [current plan limits](https://linear.app/pricing) before changing a plan or
inviting collaborators. No paid plan or GitHub integration is enabled here.

## Review explanations and ASCII assets

Maintained engineering and visual preferences live in `global/AGENTS.md` and
`global/RULES.md`. Vision documents are optional context, not a mandatory first
read or a higher authority than current requests. The unchanged `show-me` skill
provides diagrams and code-shape explanations; choose evidence for the actual
change rather than requiring a fixed artifact packet.

ASCII support is currently **aesthetic guidance and browser-based asset authoring**,
not a dedicated conversion tool, skill, or automatic asset pipeline.
[ASCII Magic](https://www.ascii-magic.com/app) is an optional editor. From the
supplied product context, start with Characters or Block Characters for technical
imagery, or Dither with Atkinson/Bayer for limited-palette artwork. Tune in the
browser, export an asset, and keep the selected source rights, recipe and output
with the consuming project's assets. Its recipe link/code can preserve settings;
there is no documented public automation API, and video exports are silent.

Keep controls and essential text accessible. Referencing
[U.S. Graphics](https://usgraphics.com/) or Berkeley Mono does not grant asset or
font licenses. The external `frontend-design` and `show-me` packages stay verbatim.

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

### Repository-local Parlor

Parlor owns its skill in `parlor/skills/parlor/SKILL.md` and its import command
in `parlor/scripts/import-skill.mjs`. It is not part of this harness's global
skill inventory. From the Parlor checkout:

```sh
node scripts/import-skill.mjs --target ../poppycock
node scripts/import-skill.mjs --target ../linejam --guidance-only
```

Both destinations are `.agents/skills/parlor` in the consuming repository.
Poppycock's reference follows its pinned installed source; Linejam's import is
explicitly guidance-only, not a framework installation or selected migration.
The importer records provenance, leaves identical imports unchanged, and refuses
to overwrite differing copies. Follow the owner procedure when refreshing;
do not maintain another skill copy in omp-config or install it globally.

### Sustained execution

Ask OMP to use the `executive` agent for a supplied direction and stopping
condition when sustained iteration is useful. It uses the existing `@task`
route. OMP's loop or a separately configured scheduler owns cadence and lifetime;
the agent does not install its own loop.

## Interactive and recurring work

The fast default model and native model roles/fallbacks remain in `config.yml`.
Use `omp` for the default or `omp --model @slow` for a deliberate Astra session.
Exa remains the configured web-search provider.

Security scanning, release automation, and recurring repository work belong to
separately configured systems with their own triggers, scope, credentials, and
evidence. PR explanation and evidence remain part of ordinary interactive work;
there are no review or delivery skill entry points here. The bundled OMP
reviewers remain available for explicitly requested work. Linear is an interactive
provider integration, not a scheduler or an autonomous delivery service.

`Steward` remains a read-only observer, not a release gate. Its native
`advisor.syncBacklog: "off"` setting avoids waiting for catch-up while preserving
background review and ordinary advice delivery.

### Evaluations are work records

The bounded Deepsec pilot and its unresolved repository, credential, cost, and
scheduling decisions are tracked in
[MIS-5](https://linear.app/misty-step/issue/MIS-5/evaluate-scheduled-deepsec-security-reviews).
No scan or timer is installed here. A selected service's maintained configuration
and procedure must live with that service, not grow into a proposal manual here.

Memory and shared-component evaluations likewise belong in Linear until a
specific implementation is selected. Memory may be derived retrieval, never a
replacement for source authority. UI source belongs to its owning library and
consumers, not to the harness. Neither evaluation enables a provider, ingests
private data, installs dependencies, or reskins products.

## Canon relationship

`CANON.md` states the implementation-independent operating philosophy.
Configuration, standing policy, and skills are concrete mechanisms that should
express it without turning the canon into an inventory of the current harness.
Implementation details and routing live in this README and the configuration.
Never paste the canon wholesale into agent context; distill only the judgment a
surface needs.

## Ecosystem

- Non-R90 work uses Linear for durable tracking and project notes for design
  knowledge. Current operator requests remain authority; R90 stays in Habitat.
- **Iron Forest** — headless Builder/Verifier/Fixer factory. Mechanical
  enforcement belongs there and in CI, not in prose.
- **Landmark** — release pipeline: conventional commits become semantic
  versions, technical changelogs, synthesized user-facing notes, and
  machine-readable evidence.
