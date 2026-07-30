# Sprite provisioning: credential-free public handoff

This primitive owns one narrow boundary: restore a dedicated clean checkpoint,
clone one public GitHub repository into a new directory, stream one lane card,
and emit a truthful local handoff receipt. Another system owns launch and
workflow authority.

## Trust boundaries

- The local `sprite` client uses its existing HOME/XDG-owned provider session.
  `sprite-lane` snapshots one descriptor-opened regular provider executable.
  It serves that immutable descriptor through a nonce-bound authenticated
  broker. It starts the executable with an allowlisted environment and exact
  host `PATH=/usr/bin:/bin`. It never reads or copies the session. The broker
  secret never crosses its reconnectable socket. Replacing the installation,
  published snapshot, broker root, or socket pathname cannot supply provider
  bytes or forge a successful response.
- Use existing remote state only when an exact v3 marker, one uniquely matching
  checkpoint, and the caller's local non-secret ownership record contain the
  same nonce.
- Keep the remote clone public and unauthenticated. Do not support private Git
  access or GitHub tokens.
- Do not put a Harness or model credential in this helper. An external launch
  owner consumes the handoff and owns short-lived injection, process isolation,
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
   `~/.omp/agent/state/sprite-lane/<sprite>.owner` containing that marker.

Keep the prior checkpoint until the new checkpoint exists, its identity is
verified, and the local witness is durably replaced through a held no-follow
directory descriptor. Fsync the new bytes in an anonymous inode. Give the old
inode a descriptor-created recovery link. Install the new inode from its
descriptor before the directory commit. If replacement fails, attempt to
restore the prior checkpoint while preserving the primary failure code. If
restoration fails, retain the old checkpoint and local witness as recovery
evidence, fail ownership checks closed, and emit an explicit
operator-recovery error. Report failure to retire the old checkpoint or
recovery link as cleanup debt. Do not invalidate the newly committed exact
marker tuple.

Before verifying the new marker/checkpoint/witness tuple, treat an observed
HUP, INT, or TERM as the same rollback path. Ignore further termination
signals until cleanup finishes. Treat the verified tuple as the commit boundary.
A signal after that boundary does not turn a committed direct bake into a
reported failure. Retire the prior checkpoint as best-effort cleanup. If a
provider interruption prevents pre-commit rollback, keep the prior checkpoint
and witness available. Normal ownership checks must refuse the divergent live
state.

Never convert legacy state or clean an arbitrary existing Sprite. Use a new
name or recreate it outside this command. After an external destroy, remove
the stale local witness before reusing the name.

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

After restoring the whole Sprite, use a new checkout for every preparation.
The caller must hold exclusive use of that Sprite during preparation. The
external infrastructure owner manages leasing.

## Failure handling

- Local validation failures occur before the receipt and before remote mutation.
- After `preparing` exists, finish every observed setup failure as
  `setup_failed`. If receipt persistence itself fails, do not replace the
  primary exit code. A terminal retry preserves the exact intended state, exit
  code, finish time, and successful `prepared` outcome. Never synthesize a
  setup failure after remote preparation commits. Keep the receipt active until
  a terminal write succeeds or reports a typed committed outcome. Retry cleanup
  once. If persistence remains unavailable, emit the lane identifier as
  explicit recovery evidence.
- Finish signals as `interrupted`. Make no claim about a Harness because this
  helper never launches one.
- Treat unknown Sprite state as evidence to stop, not permission to delete.
