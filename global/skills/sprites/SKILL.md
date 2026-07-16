---
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

`scripts/sprite-lane` prepares one clean public checkout and writes a local
handoff receipt. It does not launch a Harness, handle a model or Git credential,
manage a detached session, or report work it cannot observe.

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

The helper resolves `sprite` only from fixed installation paths. Pass
`--provider-cli <absolute-path>` before the command for a different explicit,
regular, no-symlink installation. It descriptor-opens and snapshots the chosen
executable once. An authenticated local broker holds that snapshot descriptor,
signs nonce-bound requests and responses without sending its secret over the
socket, and refuses replacement snapshot leaves. Replacing either the original
installation path or the published broker path cannot select provider bytes.

Preparation receipts land in
`~/.roster/receipts/sprite-lane/<lane-id>.json`. The initial `preparing`
receipt exists before any remote mutation. Its terminal state is `prepared`,
`setup_failed`, or `interrupted`, with the exact observed setup exit code.
It records the remote work and card paths for the external launch owner and
contains no raw remote log or launch credential. Preparing and terminal writes
use descriptor-relative no-follow traversal and anonymous-descriptor installs
with file and directory fsync. A post-commit sync failure is reported as
durability-unknown; recovery-link cleanup debt remains distinct from failure
before commit.

A non-secret ownership record lands in
`~/.roster/state/sprite-lane/<sprite>.owner`. Its version and random nonce must
exactly match the remote marker and one checkpoint comment. This local witness
prevents an arbitrary or recycled Sprite from declaring itself owned.

## Ownership and isolation

`bake` works only on a newly created Sprite or one already proven to have an
exact owned marker/checkpoint/witness tuple. It refuses legacy, arbitrary, or
ambiguous state. Replacement is transactional: the known-good checkpoint stays
available until the new checkpoint and local witness are committed.

Every preparation restores the whole owned checkpoint, creates a unique
`/home/sprite/lanes/<lane-id>/work` clone, and streams only the staged lane
card on standard input. Lane creation, card write, and the relative `work`
clone run in one Python process physically anchored to held, no-follow remote
directory descriptors.
The baseline has Git plus a neutral identity and rejects known Harness,
GitHub CLI, SSH, netrc, XDG Git, proxy, and Git credential state. Public clones
run under an empty environment with system/global Git configuration disabled.
Only a public GitHub `owner/name` slug or credential-free HTTPS URL is accepted.

The local `sprite` client's existing provider session remains in its
HOME/XDG-owned store; the helper neither reads nor copies it. The external
launch owner must inject short-lived authority at its own isolated process
boundary and own termination, redaction, expiry, and completion proof.

See `references/provisioning.md` for the exact handoff and failure contract.

## Lane cards

A card states the end state, executable acceptance oracle, boundaries,
verification surface, and expected output. Use `templates/lane-card.md`. The
prepared checkout receives only the card and public repository, so include all
task context the later launch needs.

## Gotchas

- `prepared` means only that the checkout exists; it never means an agent ran.
- A caller must hold exclusive use of the dedicated Sprite while restoring and
  preparing it. Cross-client leasing belongs to the infrastructure owner.
- Any marker/checkpoint ambiguity fails closed. Recreate under a new dedicated
  name instead of adopting unknown state.
- Private Git, Harness launch, credential injection, remote log retention, and
  detached lifecycle are intentionally absent from this public primitive.
