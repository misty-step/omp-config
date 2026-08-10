---
name: using-exe-dev
description: |
  Destination routing for exe.dev.
  Use when: a task requests inspection or operation of exe.dev, an exe VM,
  an *.exe.xyz host, or exe.dev infrastructure.
  Do not use when: exe.dev appears only in quoted, historical, or comparison text.
  Trigger: exe.dev, exe VM, *.exe.xyz.
argument-hint: "[inspect|create|connect|transfer|manage] [vm]"
---

# /using-exe-dev

Use exe.dev through its native SSH API. Preserve the repository's authority,
the operator's credential boundary, and the exact remote target.

## Documentation

Start with [the progressive docs index](https://exe.dev/docs.md). Use
`ssh exe.dev help <command>` for the live command contract.

## Choose the destination

The two SSH destinations have different authority:

- `ssh exe.dev <command>` reaches the control-plane lobby. Use `--json` for
  automation. The lobby does not run arbitrary shell commands or support file
  transfer.
- Use the `ssh_dest` returned by `ssh exe.dev ls --json` for a VM shell, `scp`,
  `sftp`, or port forwarding. Do not reconstruct a destination from its display
  name because a routed destination can include a user. Match the authorized VM
  name exactly against `.vms[].vm_name`. Require one match, use only its
  `ssh_dest`, and stop on zero or multiple matches.

Start read-only:

```bash
ssh -o BatchMode=yes exe.dev whoami --json
ssh -o BatchMode=yes exe.dev ls --json
```

Use command exit status and required JSON fields as the oracle. Resolve current
flags with `help` instead of inventing them or parsing decorative terminal text.

## Authority and credentials

Read the active repository instructions before remote work. Account login proves
identity; it does not authorize a repository, VM, deployment, or lifecycle
mutation. Require the exact target, attachment scope, and operation authority
before any control-plane mutation. This includes VM lifecycle, sharing, domains,
integrations, account keys or defaults, support access, and agent management.

For Misty Step infrastructure, compose `/estate-infrastructure`. That skill owns
the typed authorization artifact; this skill only routes the destination.

Use the operator's existing SSH configuration and selected identity. Keep private
keys, bearer tokens, GitHub tokens, `.ssh`, `.env`, Git credential stores, and
local OMP state on their owning host. Transfer only named non-secret files.
Keep host-key verification enabled. On the first lobby connection, verify
`exe.dev` against [the official fingerprint](https://exe.dev/docs/faq/host-key.md).
For a returned VM destination, follow the operator's known-host policy and stop
on a changed key; the lobby fingerprint does not identify VM hosts.

For private repositories, require an attached integration; account linkage alone is insufficient.
Follow [the official GitHub guide](https://exe.dev/docs/integrations-github.md) on the authorized VM.

## Gotchas

- Use `BatchMode=yes` for unattended probes so SSH fails instead of opening registration.
- Select `IdentityFile` with `IdentitiesOnly yes` when more than one local key exists.
- Keep agent forwarding off unless the exact task and repository authority require it.

## Completion Gate

Apply the Shared Operating Spine (`Prove`; Durable State and Closeout) and
`global/references/verification-system-first.md`. Report the authorized VM and
operation, actual destination, command exit status, required JSON or runtime
fields, credential boundary, and any remaining remote state. Claim completion
only after the real SSH surface or requested VM service endpoint proves the outcome.
