---
disable-model-invocation: true
name: code-review
description: |
  Run the mandatory frozen-bundle review receipt gate: pinned OpenClaw
  autoreview plus independent Cursor Thermos correctness/security and
  maintainability/code-quality passes. Use when: "review this", "code review",
  "is this ready to ship", "second-model review". Trigger: /code-review, /review.
argument-hint: "[branch|diff|files]"
---

# /code-review

Run the immutable three-pass receipt gate. The author does not ship on the
author's own review. `global/AGENTS.md` owns closeout duty; `bin/review_gate.py`
owns freeze identity, the pinned run, receipt schema, and protected-push verdict.

## Canonical entrypoints

Use repository-pinned paths, not a home-directory or stale external path:

- `python3 bin/review_gate.py freeze` writes the committed-range freeze.
- `python3 bin/review_gate.py run` runs the pinned three-pass wave and writes the
  receipt. It is the only public substantive receipt-creation command.
- `python3 bin/review_gate.py verify` checks the receipt against the exact range.
- `global/skills/autoreview/scripts/autoreview` is the projected OpenClaw helper;
  its executable and payload are pinned and the runner forces `--engine codex`.
- `global/skills/thermos/SKILL.md` is the projected Thermos coordinator.
- `global/skills/thermo-nuclear-review/SKILL.md` is the correctness/security leaf.
- `global/skills/thermo-nuclear-code-quality-review/SKILL.md` is the
  maintainability/code-quality leaf.
These projected skills are pinned from the `cursor-thermos` external source.
The canonical external payloads behind those projections are:

- `global/external/openclaw-autoreview/scripts/autoreview`, pinned by
  `global/external/openclaw-autoreview/.sync-meta.json`.
- `global/external/cursor-thermos/thermos/SKILL.md`, the pinned coordinator.
- `global/external/cursor-thermos/thermo-nuclear-review/SKILL.md`, the pinned
  correctness/security leaf.
- `global/external/cursor-thermos/thermo-nuclear-code-quality-review/SKILL.md`,
  the pinned maintainability/code-quality leaf.
- `global/external/cursor-thermos/.sync-meta.json`, the Thermos payload pin.

The runner must resolve and hash these canonical payloads; do not substitute a
home-directory copy or a stale external path.

The pass order is `freeze -> run -> verify`; within `run`, the OpenClaw pass
and both Thermos passes are independent consumers of the one frozen packet.
The two Thermos passes MUST run in parallel, and no optional critic or
synthesis may substitute for or precede the complete mandatory wave.


The two Thermos skills are leaf reviewers. They never invoke `/code-review`,
another review orchestrator, or a nested reviewer.

## Sole substantive flow: freeze -> run -> verify

Review committed objects, never mutable worktree bytes. Resolve the requested
base to `OLD_OID` (normally `git merge-base <base-ref> HEAD`; for a protected
push use the exact pre-push old object id) and set `NEW_OID` to
`git rev-parse HEAD`:

```bash
REPO=.
GATE=bin/review_gate.py
FREEZE=.omp/review-freeze.json
OLD_OID="$(git merge-base <base-ref> HEAD)"
NEW_OID="$(git rev-parse HEAD)"

python3 "$GATE" freeze --repo "$REPO" \
  --old-oid "$OLD_OID" --new-oid "$NEW_OID" --output "$FREEZE"
python3 "$GATE" run --repo "$REPO" --freeze "$FREEZE"
python3 "$GATE" verify --repo "$REPO"
```

`freeze` fails when any frozen path is dirty. Do not work around that failure.
The freeze contains the canonical repository, `old_oid`, `new_oid`, ordered
introduced commits, sorted changed paths, and `bundle_digest` (`sha256:` plus 64
lowercase hexadecimal characters).

`run` creates one read-only evidence packet containing the freeze JSON, bundle
digest, and exact committed diff. OpenClaw reviews each bounded dataset view of
that packet independently; the runner aggregates all chunk findings. A
digest-named read-only local marker only selects the dataset review. Entirely
deleted file bodies become path and removed-line
metadata. Credential-shaped values become explicit `redacted` placeholders.
After each old/new hunk passes path-dialect secret scanning, its diff prefixes
become comment-prefixed added/removed/context labels, and lines naming
credential primitives become explicit omission markers in OpenClaw's dataset
transport. Both projected Cursor workers receive the exact packet with fixed
model `composer-2.5`. The runner checks that the packet,
frozen worktree, and Git range did not change before it records the receipt.
For OpenClaw chunking, preserve a structured summary for every bounded
dataset, then run one final bounded cross-chunk pass over those summaries.
The final pass is mandatory and remains bounded; a clean individual dataset
pass cannot stand in for the final cross-chunk pass, and no dataset summary
may be dropped. Keep each per-dataset report and the final report in the raw
evidence preserved by the runner.
Every OpenClaw chunk report must include a non-empty `change_summary` string
of at most 4096 characters and an `interface_effects` array with at most 64
non-empty strings, each at most 4096 characters. Preserve chunk reports under
`raw_report.chunks` with their dataset names.

The runner writes `autoreview.integration.json` into the immutable packet with
schema `omp.review-integration.v1`, the frozen `bundle_digest`, and the
bounded chunk summaries/findings. It then writes
`autoreview.integration.raw.json`; the final bounded pass consumes the
freeze, evidence packet, and integration artifact and returns
`findings`, `actionable_findings`, and `overall_correctness`.


Thermos correctness and quality workers use packet-only temporary workspaces
outside the detached repository. Their workspace contains the frozen evidence
packet and declared inputs only; they must not inspect the detached repo,
mutable worktree, or host paths.
The runner stages `review-skill.md` inside that packet for each Thermos worker;
the worker cwd is the packet-only temporary workspace, never the detached
repository or a mutable worktree.



The receipt preserves each raw report and findings separately. Every reviewer
entry records its principal, harness, fixed model, resolved executable and
SHA-256 digest, resolved payload and SHA-256 digest, status, actionable finding
count, exit code, and raw report path/content. A clean pass requires status
`clean`, zero actionable findings, and exit code `0` for all three reviewers.
The run owns normalization; callers cannot select reviewer commands or submit
pass envelopes through the public CLI.
When normalizing a report, `actionable_findings` is a declared non-negative
integer and `findings` is a list. Reject missing-both, non-integer, invalid, or
negative values; do not coerce malformed data to zero. The effective count is
`max(actionable_findings, len(findings))`, and clean requires that effective
count to be zero as well as status `clean` and exit code `0`.

The runner owns these exact pass artifacts and rejects copied or hand-authored
substitutes:

```text
.omp/review-passes/autoreview.json
.omp/review-passes/thermo-nuclear-review.json
.omp/review-passes/thermo-nuclear-code-quality-review.json
```

Each receipt reviewer entry carries `pass_artifact: {path, sha256}` for its
gate-owned JSON file. Verification re-reads that path, recomputes its digest,
requires exact equality with the receipt entry, and re-hashes the live worker
executable plus recursive payload. The worker metadata is
`principal`, `harness`, `model`, `executable`, `payload`,
`executable_sha256`, and `payload_sha256`; an unsupported `resolved`
attestation field fails closed.
Executable and payload digests are audit evidence: the local gate proves
review-artifact, committed-range, and worker-drift integrity, not signer
identity or protection from a compromised host/root account or an operator who
can replace the hook or bypass it.

The hook accepts one unique committed range per push; push divergent branches
separately so each range receives its own receipt.
The pre-push hook classifies the frozen range before starting the expensive
review run. For `trivial`, it emits the exact actor-attributed `waive`
command shown below and stops; it never invents an actor, reason, or waiver.
For substantive scope, it proceeds to the mandatory three-pass run.
For a trivial range, the hook emits this command template and stops before the
expensive run:

```text
run: <sys.executable> <absolute bin/review_gate.py> waive --repo <repo> --freeze <repo>/.omp/review-freeze.json --actor <git user.email or user.name, else <actor>> --reason '<operator-supplied reason>'
```

This is an argv template, not a shell-safe paste target. The actor and reason
are operator-supplied values; the hook never fabricates either value.

## Fix and rerun

After the wave returns, verify every finding against the frozen committed diff.
Fix each accepted actionable finding before closeout. A fix changes the range:
commit it, set `NEW_OID` to the new `HEAD`, and repeat the complete
`freeze -> run -> verify` flow. Never reuse a pass report, evidence packet, or
freeze from an older digest.

An unavailable or failed mandatory reviewer is not a substitute for an optional
critic. OpenCode or any other optional critic may run only after all three
mandatory passes are clean. If an optional critic causes a code or policy fix,
refreeze and rerun the complete mandatory flow.

## Trivial prose/config waiver

Only an inert prose/config-only range outside policy paths may use the explicit
waiver command instead of the substantive flow:

```bash
python3 bin/review_gate.py waive \
  --repo . \
  --freeze .omp/review-freeze.json \
  --output .omp/review-receipt.json \
  --actor "<stable-name-or-email>" \
  --reason "prose-only documentation change with no executable or policy behavior"
python3 bin/review_gate.py verify --repo .
```

Policy files, including `global/skills/**` and `SKILL.md`, are substantive even
when their contents are prose. `.gitattributes` is substantive because it can
change how later evidence is rendered. A waiver cannot authorize policy,
executable, or evidence-rendering changes.

## Closeout

Report the frozen digest, exact three reviewer identities, pass statuses, finding
counts, exit codes, fixes/refreezes, and the final `run` plus `verify` commands.
Include residual risk and evidence in the `global/AGENTS.md` closeout format. Do
not call a phase complete from one reviewer, an optional critic, a prose-only
summary, a hand-authored pass, or a stale receipt.
