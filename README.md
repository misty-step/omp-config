# omp-config

Omp harness configuration for Phaedrus / Misty Step. Source of truth for how
agents run on this machine: model roles, global policy, skills, themes.
`./install` deploys owned components. Publishing checks do not install.

Standing guidance lives in `global/AGENTS.md`. It is philosophy, authority,
and evidence calibration—not a SYSTEM override, sticky RULES file, or second
canon. Local repository conventions and explicit requests outrank it.

## Layout

| Path | Purpose |
| --- | --- |
| `install` | Ownership-aware deployment into `$(omp config path)` |
| `bin/omp-merge-config.ts` | Overlay source-owned YAML keys onto live config |
| `bin/omp-grievances.ts` | Manual grievance inbox CLI |
| `config.yml` | Model roles, fallbacks, theme/TUI, providers, task/LSP settings |
| `models.yml` | Local Ollama discovery; cloud models come from omp's bundled catalog |
| `mcp.json` | Global MCP inventory; Linear is deliberately absent |
| `workspace-mcp.json`, `bin/omp-install-scopes.ts` | Linear directory scopes, native project-local imports, owned skill retirement |
| `global/AGENTS.md` | Collaboration, verification, Linear/Habitat routing, privilege boundaries |
| `agents/executive.md` | Caller-bounded sustained execution through `@task` |
| `global/WATCHDOG.md`, `global/WATCHDOG.yml` | One read-only Steward advisor |
| `themes/` | TUI themes (`tokyonight`, `everforest`, `everforest-light`) |
| `skills/` | Owned skill packages, clean-replaced when selected |
| `.githooks/pre-push` | Secret scanners only; installed into this repo's git dir by `./install` |
| `extensions/loc/` | Session-resident LOC status and commands |

## Install

```sh
./install   # requires jq, bun, and omp
```

Preflight validates every selected input, then writes. Unset selection means
`all`: owned config overlay, guidance, MCP, scopes, agents, skills, themes,
extensions, this repo's git hook, and `omp-grievances`. It does not delete
foreign skills or agents, and it does not import live secrets into this
checkout.

```sh
OMP_INSTALL_COMPONENTS=guidance ./install
OMP_INSTALL_COMPONENTS=config ./install
OMP_INSTALL_COMPONENTS=agents ./install
OMP_INSTALL_COMPONENTS=mcp ./install
OMP_INSTALL_COMPONENTS="guidance mcp scopes skill:capture" ./install
```

Supported components are `guidance`, `config`, `mcp`, `scopes`, `agents`, and
`skill:<source-directory-name>`. `all` cannot be combined with another
component. Empty, unknown, missing-skill, invalid-name, and invalid YAML
selections fail before any writes. The retired `OMP_INSTALL_GUIDANCE_ONLY`
variable fails with migration instructions rather than silently triggering a
full install.

Owned skill packages are replaced, not overlaid, so obsolete files cannot
survive inside a selected package. Foreign packages in the live skills or
agents directories are left in place. `guidance` copies AGENTS and WATCHDOG
and deletes the retired live `RULES.md`. `config` overlays keys present in
source `config.yml` / `models.yml` and preserves undeclared live keys such as
runtime consent; it does not copy auth stores. MCP deployment still uses the
declared server inventory and preserves live `auth`/`oauth` metadata for those
servers only. OMP's managed OAuth tokens remain in its auth storage, never in
this repository.

`scopes` installs Linear only under `~/development/misty-step` and
`~/development/moomooskycow`, retires the owned global `parlor`, `ast-grep`,
and `now-next` packages, and retires global `todoist-cli` only after
`$OMP_DEVELOPMENT_ROOT/moomooskycow/daybook/.agents/skills/todoist-cli/SKILL.md`
exists (override with `OMP_TODOIST_OWNER`). It does not mutate `~/.claude` or
`~/.codex`; those live aliases are Main-owned. Redirecting
`PI_CODING_AGENT_DIR` does not isolate hook, scope, or `~/.local/bin` writes.
Use a disposable HOME, development root, and checkout copy for installer
checks.

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
[Misty Step work tracking guide](https://linear.app/misty-step/document/misty-step-work-tracking-guide-d3a627ae6395),
[Misty Step Issue Templates and Work Conventions](https://linear.app/misty-step/document/misty-step-issue-templates-and-work-conventions-d976aa9e94e8),
and [omp-config project](https://linear.app/misty-step/project/omp-config-47a74679f980).
Keep procedures and version-bound knowledge here; link them from work records.
Check [current plan limits](https://linear.app/pricing) before changing a plan or
inviting collaborators. No paid plan or GitHub integration is enabled here.

## Review explanations and ASCII assets

Maintained engineering and visual preferences live in `global/AGENTS.md`. Vision
documents are optional context, not a mandatory first read or a higher authority
than current requests. The unchanged `show-me` skill provides diagrams and
code-shape explanations; choose evidence for the actual change rather than
requiring a fixed artifact packet.

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

Two homebrew skills remain, both explicitly requested:

| Command | Outcome |
| --- | --- |
| `/skill:foundation` | Reassess product purpose, backlog, architecture, and development and operational foundations; recommend a coherent direction without making changes |
| `/skill:capture` | Save durable findings to project notes, or the required tracker, without duplicating or claiming work |

`disable-model-invocation: true` hides these descriptions from the automatic
skill index. It does not prevent an explicit `skill://` read or grant authority
to act. Read-only requests remain read-only.

`foundation` is an investigation and design proposal, not an implementation
pass. It distinguishes an ideal destination from a practical transition.
Invoke `/skill:foundation` with any context or constraints the repository
cannot supply; select the model separately. Backlog changes and implementation
remain separately authorized work.

Four vendored packages remain unchanged except by whole-package refresh:
`frontend-design`, `herdr`, `show-me`, and `wrangler`. Wrangler is refreshed
from [cloudflare/skills](https://github.com/cloudflare/skills) at
`d924cd8f59e75e08fd3dd52843bb2776de35c77e` with its Apache 2.0 license.
Update them from upstream or remove the whole package; use a distinctly named
homebrew skill for different behavior. Omarchy's `omarchy` and
`diagnose-crash` retain their own owners and discovery paths; this installer
does not replace them. Todoist is owned by Daybook and is not shipped here.

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
Exa remains the configured web-search provider. Approval mode and title-model
names are unchanged.

Security scanning, release automation, and recurring repository work belong to
separately configured systems with their own triggers, scope, credentials, and
evidence. PR explanation and evidence remain part of ordinary interactive work;
there are no review or delivery skill entry points here. The bundled OMP
reviewers remain available for explicitly requested work. Linear is an interactive
provider integration, not a scheduler or an autonomous delivery service.

`Steward` remains a read-only observer, not a release gate. Its native
`advisor.syncBacklog: "off"` setting avoids waiting for catch-up while preserving
background review and ordinary advice delivery. Print-mode can still drain a
final review. Subagents are unadvised unless they opt in.

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

## Isolated installer checks

Run these once after integration against a disposable HOME, agent directory,
development root, and checkout copy. Do not point `PI_CODING_AGENT_DIR` at the
live agent tree. Compare path hashes before and after each case.

1. **Foreign package preservation.** Seed `$agent/skills/foreign-cli/SKILL.md`
   and `$agent/agents/foreign.md`. `./install` must keep both and replace only
   owned packages.
2. **Runtime config preservation.** Seed `$agent/config.yml` with source keys
   plus `dev.autoqaConsent: granted`. `OMP_INSTALL_COMPONENTS=config ./install`
   must keep that key, apply source-owned keys, and leave auth stores untouched.
3. **MCP auth vs inventory.** Seed a live `mcp.json` with matching `auth` on
   `openrouter` and an extra undeclared server. MCP install must keep matching
   `auth`/`oauth` for declared servers and drop the extra server. Do not print
   secrets.
4. **Invalid preflight writes nothing.** Record hashes, then try a missing
   guidance file, `OMP_INSTALL_COMPONENTS=skill:not-a-skill`, invalid live YAML,
   and a conflicting `.omp/.mcp.json`. Each must fail before creating or
   changing destinations.
5. **Scope boundaries.** Under a fake `OMP_DEVELOPMENT_ROOT`, only
   `misty-step` and `moomooskycow` receive Linear definitions and relative
   `.mcp.json` imports. An `r90` tree stays untouched. Symlinked `.omp`
   directories and conflicting fallback files are refused with no writes.
6. **Owned retirement.** Live `RULES.md`, `skills/ast-grep`, and
   `skills/now-next` disappear on `guidance`/`scopes`/`all`. `wrangler`
   matches this source package. Global `todoist-cli` remains while
   `OMP_TODOIST_OWNER` lacks `SKILL.md`, and is removed only after that
   owner file exists. Do not delete `~/.claude` or `~/.codex` copies from
   this installer.

Rollback is component-scoped: restore prior owned bytes and modes. Do not use a
historical full-directory skills replacement as rollback.

## Ecosystem

- Non-R90 work uses Linear for durable tracking and project notes for design
  knowledge. Current operator requests remain authority; R90 stays in Habitat.
- **Iron Forest** — headless Builder/Verifier/Fixer factory. Mechanical
  enforcement belongs there and in CI, not in prose.
- **Landmark** — release pipeline: conventional commits become semantic
  versions, technical changelogs, synthesized user-facing notes, and
  machine-readable evidence.
