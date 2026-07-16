# Sprite provisioning: credential-free public handoff

This primitive owns one narrow boundary: restore a dedicated clean checkpoint,
clone one public GitHub repository into a new directory, stream one lane card,
and emit a truthful local handoff receipt. Launch and workflow authority belong
to another system.

## Trust boundaries

- The local `sprite` client uses its existing HOME/XDG-owned provider session.
  `sprite-lane` snapshots one descriptor-opened regular provider executable,
  serves that immutable descriptor through a nonce-bound authenticated broker,
  starts it with an allowlisted environment and exact host
  `PATH=/usr/bin:/bin`, and never reads or copies the session. The broker secret
  is not sent over its reconnectable socket. Replacement of the installation,
  published snapshot, broker root, or socket pathname cannot supply provider
  bytes or forge a successful response.
- Existing remote state is usable only when an exact v3 marker, one uniquely
  matching checkpoint, and the caller's local non-secret ownership record all
  contain the same nonce.
- The remote clone is public and unauthenticated. Private Git access and GitHub
  tokens are unsupported.
- No Harness or model credential enters this helper. An external launch owner
  consumes the handoff and owns short-lived injection, process isolation,
  signals, output, completion observation, and credential expiry.

## Bake contract (version 3)

A clean bake contains:

1. Git and a mode-0700 lane root.
2. No `.codex`, `.claude`, `.omp`, GitHub CLI, XDG Git, SSH, netrc, Git
   credential, or known Tier-1 Harness state.
3. An exact three-line neutral Git identity with no includes, URL rewrites,
   credential helpers, or HTTP headers.
4. `~/.sprite-lane-golden` containing `v3 <nonce>`.
5. Exactly one checkpoint whose comment is
   `sprite-lane golden v3 <same-nonce>`.
6. A mode-0600 local record at
   `~/.roster/state/sprite-lane/<sprite>.owner` containing that marker.

Replacement keeps the prior checkpoint until the new checkpoint exists, its
identity is verified, and the local witness is durably replaced through a held
no-follow directory descriptor. The new bytes are fsynced in an anonymous
inode, the old inode receives a descriptor-created recovery link, and the new
inode is installed from its descriptor before the directory commit. A failed
replacement attempts to restore the prior checkpoint while preserving the
primary failure code. If restoration itself fails, the old checkpoint and
local witness are retained as recovery evidence, ownership checks fail closed,
and an explicit operator-recovery error is emitted. Failure to retire the old
checkpoint or recovery link is reported as cleanup debt but does not invalidate
the newly committed exact marker tuple.

An observed HUP, INT, or TERM before the new marker/checkpoint/witness tuple is
verified follows the same rollback path, with further termination signals
ignored until cleanup finishes. The verified tuple is the commit boundary. A
signal observed after it does not turn a committed direct bake into a reported
failure; prior-checkpoint retirement completes as best-effort cleanup. If a
provider interruption prevents a pre-commit rollback, the prior checkpoint and
witness remain available and normal ownership checks refuse the divergent live
state.

The primitive never converts legacy state and never cleans an arbitrary
existing Sprite. Use a new name or recreate it outside this command. After an
external destroy, remove the stale local witness before reusing the name.

## Prepare contract

1. Validate the Sprite name, public GitHub source, Git branch, and regular lane
   card locally.
2. Traverse and open the card through held no-follow descriptors, reject
   non-regular leaves without blocking, and keep only bytes from that opened
   descriptor in the authenticated snapshot broker.
3. Durably write and activate a `preparing` receipt before any remote call,
   using the same descriptor-install/recovery-link transaction as the ownership
   witness.
4. Create a new dedicated Sprite and clean checkpoint, or restore the exact
   immutable owned checkpoint and verify its filesystem.
5. In one remote Python process, physically anchor the Sprite home and lane-root
   working directories with no-follow descriptors, create a unique mode-0700
   lane, stream only the staged card on standard input, and clone into `.` from
   the held `work` directory.
6. Clone with `env -i`, system/global Git configuration disabled, prompting and
   askpass disabled, and no proxy, SSH agent, GitHub token, or Harness key.
7. Durably finish the receipt as `prepared` with the remote work/card paths.

Every preparation uses a new checkout after a whole-Sprite restore. The caller
must hold exclusive use of that Sprite for the preparation; leasing belongs to
the external infrastructure owner.

## Failure handling

- Local validation failures occur before the receipt and before remote mutation.
- Once `preparing` exists, every observed setup failure finishes it as
  `setup_failed` without replacing the primary exit code if receipt persistence
  itself fails. A terminal retry preserves the exact intended state, exit code,
  finish time, and successful `prepared` outcome; it never synthesizes a setup
  failure after remote preparation committed. The receipt remains active until
  a terminal write succeeds or reports a typed committed outcome. Cleanup
  retries once and emits the lane identifier as explicit recovery evidence if
  persistence is still unavailable.
- Signals finish it as `interrupted`; no claim is made about a Harness because
  this helper never launches one.
- Unknown Sprite state is evidence to stop, not permission to delete.
