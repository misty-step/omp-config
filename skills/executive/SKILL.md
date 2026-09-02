---
name: executive
description: Generate a bespoke executive prompt that runs an autonomous engineering loop over a repository's backlog, CI/CD, and production health.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Executive

Produce one standalone prompt for a long-running agent session in the target
repository. That agent is the **executive**: it runs a continuous autonomous
engineering loop over the repository. It grooms and works through the backlog,
opens and reviews PRs, hardens the system through aggressive simplification and
code deletion, locks in CI/CD pipelines, verifies production health, maximizes
observability, and eliminates human operational friction so the system is fully
manageable by agents.

The prompt is a derived view of current evidence, so every command, path,
workflow, and identity in it comes from this repository and this host, observed
now.

## Bind

Resolve the target from the argument or the current directory. Gather each
fact below with the named probe. Record the exact output; a probe that fails
or returns nothing is a fact too.

Repository:

- forge slug and primary branch: `git remote get-url origin`, `git symbolic-ref refs/remotes/origin/HEAD`;
- pre-merge read-only verification gates: repository test, lint, typecheck, and
  compilation commands (`bun test`, `cargo test`, `go test ./...`, `oxlint`, `cargo clippy`);
  keep only commands that exist in manifests and hooks; never include deployment or installation scripts;
- product lock and architecture contracts: `VISION.md`, `AGENTS.md`, `CANON.md`,
  `README.md`, `docs/adr/*` when present;
- lint host and custom-rule locations (ast-grep config, oxlint plugins, ESLint,
  golangci-lint, cargo clippy) when present;
- recent movement: `git log --oneline -15`.

CI/CD and deployment infrastructure:

- workflow definitions: `ls .github/workflows/*.yml` or CI configs;
- post-merge deployment & installation commands: commands that deploy to production,
  mutate local harnesses, or install binaries (e.g. `./install`, `fly deploy`);
- operation authority: read `AGENTS.md` / `CANON.md` / policy for deployment and merge
  rules (whether post-merge deploy is autonomous or requires live operator authorization);
- release automation: release workflows, semantic-release, tag triggers;
- agent ergonomics & operational tooling: verify whether all deployment, migration,
  and recovery paths have automated CLI entrypoints.
Observability and production health:

- health check endpoints, probes, and status commands;
- monitoring, telemetry, error tracking (e.g. Sentry, Prometheus, OpenTelemetry,
  structured log formats);
- alert surfaces and production verification commands.

Tracker:

- Detect tracker mode:
  - **Powder mode:** only when a Powder origin (`POWDER_URL` or
    `POWDER_API_BASE_URL`) is configured and either `POWDER_AGENT` is set or
    the organization/repository contract explicitly selects Powder. An origin
    alone does not choose a tracker, and an agent name alone cannot reach one.
    Probe with `powder list --repo <slug> --plain`, `--takeable`, `--waiting`;
    count jobs with and without specs; note live leases and holders; derive:
    reacquire (`powder list --mine exec-<dir> --plain`), claim
    (`powder take <id> --agent exec-<dir>`), renew
    (`powder renew <id> --agent exec-<dir>`), release
    (`POWDER_AGENT=exec-<dir> powder release <id>`), done
    (`powder done <id> --proof <sha> --agent exec-<dir>`).
  - **Forge-only mode:** otherwise. Record:
    open issues and PRs via `gh issue list -R <slug>`, `gh pr list -R <slug>`;
    derive: reacquire (`gh issue list -R <slug> --assignee @me`), claim (assign issue `@me` or create topic branch),
    done (close issue with commit SHA / link in PR body `Fixes #<id>`).
Credentials and environment:

- First bind approved credential sources and ownership from the organization
  and repository contracts. Default probes report only path, owner, mode,
  variable names, and presence. For an operator-authorized service setup, read
  only named organization-owned variables into process memory and copy them
  without printing values. Never search another organization, dump a
  credential file, or put a value in prompts, notes, commits, logs, or command
  output. Reusing an approved authentication secret does not create a new
  workload identity; new keys, identities, or spend remain human-owned until
  explicitly authorized.

Done when every binding in [`references/prompt-template.md`](references/prompt-template.md)
has an observed value or an explicit "absent".

## Compose

Read [`references/prompt-template.md`](references/prompt-template.md). Fill
each `{{binding}}` from Bind. Keep the tracker block matching the target mode
(Powder or Forge-only) and delete the other. Keep only commands observed in
Bind; a command the repository lacks leaves the prompt. Preserve the template's
order: repository facts first, operating directives last.

Add a short `<recent-signals>` block from the gathered probes: active PRs,
open issues / takeable jobs, recent commit cadence, CI/CD health, production
status, and any missing observability or automation gaps. These are the
executive's first targets.

Done when the prompt reads as written for this repository alone: no braces, no
"if applicable", no command that Bind did not observe, no credential value.

## Return

Print the finished prompt in one fenced block, then one line naming the
invocation that regenerates it (`/executive <repo-path>`).
