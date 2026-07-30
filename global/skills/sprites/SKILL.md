---
disable-model-invocation: true
name: sprites
description: |
  Prepare credential-free public repository handoffs on dedicated Fly Sprites:
  remote, isolated, scale-to-zero sandboxes for heavy work. A clean owned
  checkpoint makes every handoff reproducible without copying workstation,
  Harness, or Git credentials. Use when: "prepare this on a sprite", "remote
  sandbox", "offload a public checkout", "bake a sprite", or heavy work that
  an external launch owner will supervise. Trigger: /sprites, /sprite-lane.
argument-hint: "[prepare|bake|status|reset] [sprite] [--repo <owner/name>] [--card <file>]"
---

# /sprites

Use `scripts/sprite-lane` to prepare one clean public checkout and write a local
handoff receipt. Do not use it to launch a Harness, handle a model or Git
credential, manage a detached session, or report work it cannot observe.

## Route a lane

| Lane shape | Owner |
|---|---|
| Quick exploration, repository Q&A, or a small review | Local agent |
| Clean public checkout for heavy isolated work | `sprite-lane prepare` |
| Harness launch, short-lived credential injection, signals, logs, and completion | External infrastructure owner |
| Private repository authorization | External infrastructure owner |

Network and setup overhead make Sprites a poor fit for sub-minute work.

## Commands

```bash
scripts/sprite-lane bake <sprite>
scripts/sprite-lane prepare <sprite> \
  --repo <owner/name|https://github.com/owner/name.git> --card <file> \
  [--branch <branch>]
scripts/sprite-lane status <sprite>
scripts/sprite-lane reset <sprite>
```

Resolve `sprite` only from fixed installation paths. Pass
`--provider-cli <absolute-path>` before the command for a different explicit,
regular, no-symlink installation. The helper descriptor-opens and snapshots
the chosen executable once. An authenticated local broker holds that snapshot
descriptor. It signs nonce-bound requests and responses without sending its
secret over the socket. It refuses replacement snapshot leaves. Replacing the
original installation path or published broker path cannot select provider
bytes.

Write preparation receipts to
`~/.omp/agent/receipts/sprite-lane/<lane-id>.json`. Write the initial
`preparing` receipt before any remote mutation. Use terminal state `prepared`,
`setup_failed`, or `interrupted`, with the exact observed setup exit code.
Record remote work and card paths for the external launch owner. Do not include
raw remote logs or launch credentials. Use descriptor-relative no-follow
traversal and anonymous-descriptor installs for preparing and terminal writes.
Fsync files and directories. Report a post-commit sync failure as
durability-unknown. Keep recovery-link cleanup debt distinct from failure
before commit.

Write a non-secret ownership record to
`~/.omp/agent/state/sprite-lane/<sprite>.owner`. Match its version and random
nonce exactly to the remote marker and one checkpoint comment. Use this local
witness to prevent an arbitrary or recycled Sprite from declaring ownership.

On first use after the path move, atomically migrate legacy
`~/.roster/receipts/sprite-lane` and `~/.roster/state/sprite-lane` directories
to these destinations only when each destination is absent. If a destination
collides, stop the command and leave the legacy directory untouched. Resolve
the collision explicitly before retrying. Explicit `SPRITE_LANE_RECEIPTS` or
`SPRITE_LANE_OWNERS` overrides disable this default migration.

## Ownership and isolation

Run `bake` only on a newly created Sprite or on one proven to have an exact
owned marker/checkpoint/witness tuple. Reject legacy, arbitrary, or ambiguous
state. Replace transactionally. Keep the known-good checkpoint available until
you commit the new checkpoint and local witness.

For every preparation, restore the whole owned checkpoint. Create a unique
`/home/sprite/lanes/<lane-id>/work` clone. Stream only the staged lane card on
standard input. Run lane creation, card write, and the relative `work` clone
in one Python process. Physically anchor that process to held, no-follow
remote directory descriptors.
Keep Git and a neutral identity in the baseline. Reject known Harness, GitHub
CLI, SSH, netrc, XDG Git, proxy, and Git credential state. Run public clones
under an empty environment with system/global Git configuration disabled.
Accept only a public GitHub `owner/name` slug or credential-free HTTPS URL.

Keep the local `sprite` client's existing provider session in its
HOME/XDG-owned store. The helper must not read or copy it. The external launch
owner must inject short-lived authority at its isolated process boundary. That
owner must handle termination, redaction, expiry, and completion proof.

See `references/provisioning.md` for the exact handoff and failure contract.

## Lane cards

A card states the end state, executable acceptance oracle, boundaries,
verification surface, and expected output. Use `templates/lane-card.md`. Give
the prepared checkout only the card and public repository. Include all task
context that the later launch needs.

## Gotchas

- `prepared` means only that the checkout exists. It never means an agent ran.
- Hold exclusive use of the dedicated Sprite while restoring and preparing it.
  The infrastructure owner manages cross-client leasing.
- Any marker/checkpoint ambiguity fails closed. Recreate under a new dedicated
  name. Do not adopt unknown state.
- This public primitive intentionally omits private Git, Harness launch,
  credential injection, remote log retention, and detached lifecycle.
