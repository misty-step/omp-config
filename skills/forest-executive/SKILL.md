---
name: forest-executive
description: Generate a bespoke executive prompt that runs an Iron Forest instance and ships the repository's backlog in parallel.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Forest executive

Produce one standalone prompt for a long-running agent session in the target
repository. That agent is the **executive**: it operates the Iron Forest Kernel
that serves the repository, grooms the backlog the Kernel consumes, and ships
backlog work itself in parallel with the factory. The prompt is a derived view
of current evidence, so every command, path, unit, and identity in it comes
from this repository and this host, observed now.

## Bind

Resolve the target from the argument or the current directory. Gather each
fact below with the named probe. Record the exact output; a probe that fails
or returns nothing is a fact too.

Repository:

- forge slug and primary branch: `git remote get-url origin`, `git symbolic-ref refs/remotes/origin/HEAD`;
- toolchain and deterministic gates: `forest.yaml` `checks:` when present, else
  the repository's own manifests, hooks, and CI (`package.json`, `Makefile`,
  `.mise.toml`, `.githooks/*`, `.github/workflows/*`); keep only commands that
  exist in those files;
- product lock and contracts: `VISION.md`, `AGENTS.md`, `docs/adr/*` when present;
- lint host and custom-rule locations (ast-grep config, oxlint plugins, Go vet
  analyzers) when present;
- recent movement: `git log --oneline -15`.

Kernel binding. A Kernel serves this repository only when `forest.yaml`
`repo` equals the forge slug.

- Managed: read `forest.yaml` (roles, intervals, `max_duration`, `scope`),
  `forest.defaults.yaml`, `agents/*/agent.md` frontmatter (`model`, `tools`,
  `thinking`), skill directories, `evals/run-fast.sh` presence. Run
  `./forest version`, `./forest status --json`, `./forest audit show --json`,
  `./forest run list --limit 10`, `systemctl --user show forest@<dir> -p LoadState,ActiveState`.
  Record recent Run durations per role from the ledger rows as inspection
  context; ADR 0020 keeps Runs unbounded, so no duration becomes a cancel rule.
- Unmanaged: record that no Kernel serves this repository, whether
  `forest@<dir>` is installed, and the onboarding path in the factory
  checkout (`deploy/install-service.sh`, `docs/onboarding-managed-repo.md`).
  Bind operations to no other Kernel; another repository's Kernel is
  consumer-owned and accepts field reports only.

Tracker:

- `powder list --repo <slug> --plain`, `--takeable`, `--waiting`; count jobs
  with and without specs; note live leases and their holders;
- `gh issue list` and `gh pr list` for the slug; whether label `forest:ready` exists;
- the Kernel's Powder identity from `forest.yaml`/README convention
  (`forest-<slug>`), so the executive's identity is distinct.

Credentials: `stat -c '%U %a' ~/.config/iron-forest/<dir>.env` for owner and
mode only. File contents stay unread; non-secret configuration comes from
`forest selfcheck`, `forest.yaml`, and systemd metadata.

Done when every binding in [`references/prompt-template.md`](references/prompt-template.md)
has an observed value or an explicit "absent".

## Compose

Read [`references/prompt-template.md`](references/prompt-template.md). Fill
each `{{binding}}` from Bind. Keep the managed or unmanaged block that matches
the target and delete the other; for an unmanaged target also keep Phase 0 and
bind `{{gates}}` to the repository's observed check commands. Keep only
commands observed in Bind; a command the repository lacks leaves the prompt.
Preserve the template's order: repository facts first, operating directives
last.

Add a short `<recent-signals>` block from the status, audit, ledger, and
backlog probes: live Runs with elapsed and recent durations, trigger errors
verbatim, audit result, spec-less draft count, takeable count. These are the
executive's first targets.

Executive worktrees go to a sibling path (`../<dir>-exec-<id>`), never inside
the managed checkout: an untracked `.worktrees/` fails the installer's
clean-tree fence. The generated prompt names no `/skill`; user-invoked skills
are unreachable to the running agent, so their contracts are restated inline.

Done when the prompt reads as written for this repository alone: no braces, no
"if applicable", no command that Bind did not observe, no credential value.

## Return

Print the finished prompt in one fenced block, then one line naming the
invocation that regenerates it (`/forest-executive <repo-path>`).
