---
disable-model-invocation: true
name: code-review
description: |
  Apply the frozen committed-range review protocol with three independent
  submissions and gate-owned evidence. Trigger: /code-review, /review.
argument-hint: "[branch|diff|files]"
---

# /code-review

Use this skill for the substantive review protocol. The protocol is
harness-neutral: a caller or harness explicitly loads the review skills it
needs, supplies worker attribution, and submits the resulting v1 documents.
The gate owns the frozen range, packet, pass artifacts, receipt, and
verification. No leaf owns gate orchestration, a provider, a model, or a
particular invocation route.

The required reviewer order is:

1. `autoreview`
2. `thermo-nuclear-review`
3. `thermo-nuclear-code-quality-review`

The last two names are ordinary standalone skills. Any agent or harness may
load either projected skill explicitly:

```text
global/skills/thermo-nuclear-review/SKILL.md
global/skills/thermo-nuclear-code-quality-review/SKILL.md
```

They do not invoke `/code-review`, another review workflow, or a nested
reviewer. The upstream `thermos/skills` name may remain in external sync
metadata as provenance for those immutable payloads; it is not a runtime owner
or an invocation route.

## Canonical public sequence

The only substantive sequence is:

```text
freeze -> prepare -> submit -> record -> verify
```

The public gate CLI exposes the following commands. There is no aggregate
substantive invocation command:

| Command | Contract |
|---|---|
| `classify` | Classify a committed range as `trivial` or `substantive`. |
| `freeze` | Recompute one committed range and write the fixed `.omp/review-freeze.json`. |
| `prepare` | Load that freeze and write the gate-owned `.omp/review-packet/manifest.json` plus bounded datasets. |
| `submit` | Read one `omp.review-result.v1` from a file or stdin for either official leaf, require explicit worker attribution, and write the gate-owned pass artifact. |
| `record` | Discover exactly the three canonical pass artifacts and write the fixed `.omp/review-receipt.json`. |
| `verify` | Recompute the range and every packet, pass, receipt, and skill digest. |
| `waive` | Write an explicit actor-attributed waiver for an inert trivial prose/config range only. |
| `hook` | Enforce one unique pushed range and the same freeze/prepare/submit/record/verify protocol. |

Exit status is part of the CLI contract: `0` means the command completed with
clean evidence, `1` means `submit` received a valid non-clean reviewer result,
and `2` means a protocol, schema, range, or artifact failure. `record` and
`verify` fail with `2` when the required set is incomplete or non-clean.

Use the repository entrypoint and fixed artifact locations:

```bash
REPO=.
GATE=bin/review_gate.py
OLD_OID="$(git merge-base <base-ref> HEAD)"
NEW_OID="$(git rev-parse HEAD)"

python3 "$GATE" freeze --repo "$REPO" \
  --old-oid "$OLD_OID" --new-oid "$NEW_OID"
python3 "$GATE" prepare --repo "$REPO"

# `autoreview` is first. The optional adapter submits through the same seam.
python3 bin/review_runner.py run-one --repo "$REPO" \
  --reviewer autoreview --engine "$ENGINE" \
  --actor "$AUTOREVIEW_ACTOR" --harness "$AUTOREVIEW_HARNESS" \
  --model "$AUTOREVIEW_MODEL" --run-id "$AUTOREVIEW_RUN_ID"
# The two official leaves submit directly through the gate CLI. Use distinct
# harness/run-id pairs for the two required submissions.
python3 "$GATE" submit --repo "$REPO" \
  --reviewer thermo-nuclear-review \
  --actor "$LEAF_ACTOR_A" --harness "$LEAF_HARNESS_A" \
  --model "$LEAF_MODEL_A" --run-id "$LEAF_RUN_ID_A" \
  --result "$LEAF_RESULT_A"
python3 "$GATE" submit --repo "$REPO" \
  --reviewer thermo-nuclear-code-quality-review \
  --actor "$LEAF_ACTOR_B" --harness "$LEAF_HARNESS_B" \
  --model "$LEAF_MODEL_B" --run-id "$LEAF_RUN_ID_B" \
  --result "$LEAF_RESULT_B"

python3 "$GATE" record --repo "$REPO"
python3 "$GATE" verify --repo "$REPO"
```

The gate `submit` command accepts only the two official leaf names. Every
direct leaf submission must provide `actor`, `harness`, `model`, and `run_id`
explicitly. The core does not select defaults for any of them. The
`autoreview` result requires an adapter attestation when an adapter executes
it; the optional `run-one` adapter supplies that attestation and uses the same
gate submission seam.

The optional `review_runner.py run-one` command is an adapter for one worker.
It may invoke a chosen skill and then calls the same
`review_receipt.submit_result` seam. It does not define canonical skill
semantics, select a model/provider/harness, create a second receipt path, or
replace the public sequence. A direct leaf caller may omit it.

The gate fails closed when the frozen range, packet bytes, result shape,
worker attribution, pass artifacts, receipt, or projected skill digest
changes. A substantive receipt is clean only when all three submissions have
status `clean`, zero actionable findings, empty findings, and distinct
`(harness, run_id)` identities. A non-clean submission is a review finding
outcome, not a protocol substitute; fix the finding, refreeze, and repeat the
complete sequence. A malformed or stale artifact is a protocol failure.

## Committed-range boundary

Review committed objects, never mutable worktree bytes. Resolve the requested
base to `OLD_OID`, normally with `git merge-base <base-ref> HEAD`, or use the
exact pre-push old object id in the hook. Set `NEW_OID` to `git rev-parse HEAD`.
`freeze` rejects a dirty worktree for frozen paths and records the repository,
old/new object ids, ordered introduced commits, sorted changed paths, and
`bundle_digest` (`sha256:` plus 64 lowercase hexadecimal characters).

Never reuse a freeze, packet, pass artifact, or receipt after the committed
range changes. A fix changes the range: commit it, freeze again, prepare a new
packet, collect all three submissions, record, and verify again.

## Gate-owned packet and artifacts

`prepare` creates one deterministic, redacted packet at
`.omp/review-packet/`. It includes the freeze identity, exact committed diff,
bounded dataset views, dataset digests, evidence policy, and exactly the three
review assignments. Deleted files retain their path and removed-line count but
not their body. Credential-shaped values and lines naming credential
primitives are replaced with explicit omission markers.

Review workers receive only the packet and declared inputs in a temporary
packet-only workspace. They must not inspect the detached repository, mutable
worktree, host paths, or unrelated network state. The packet manifest and all
dataset bytes are read-only and digest-bound.

`submit` owns result normalization. It accepts `omp.review-result.v1`, rejects
missing, malformed, non-integer, or negative finding counts, and never coerces
invalid data to zero. It writes exactly one gate-owned
`omp.review-pass.v3` artifact per canonical reviewer:

```text
.omp/review-passes/autoreview.json
.omp/review-passes/thermo-nuclear-review.json
.omp/review-passes/thermo-nuclear-code-quality-review.json
```

Callers cannot choose pass paths or hand-author substitutes. `record` reads
those exact files in canonical order, binds their digests to
`.omp/review-receipt.json`, and records the v3 receipt. `verify` re-reads every
bound path, recomputes the Git identity and packet digest, validates skill
identity, and checks the worker attribution.

## Six projected review modules

The six projected Python modules have one ownership boundary each:

| Module | Owns |
|---|---|
| `bin/review_common.py` | `REVIEW_SPECS`, v1/v2/v3 schema names, digest and identity validation, `skill_identity`, and explicit `worker_attribution`. It chooses no worker defaults. |
| `bin/review_bundle.py` | Git object/range identity, bundle digest, confined artifact paths, freeze loading, and committed-range checks. |
| `bin/review_packet.py` | `prepare_packet`, `load_packet`, `verify_packet`, deterministic redaction, bounded datasets, the packet manifest, and packet digests. |
| `bin/review_receipt.py` | `submit_result`, gate-owned v3 pass artifacts, `record_receipt`, `verify_receipt`, receipt binding, and clean-result enforcement. |
| `bin/review_runner.py` | Optional one-worker execution adapter only. It feeds explicit attribution and a v1 result through `submit_result`; it does not own leaf, model, provider, or harness semantics. |
| `bin/review_gate.py` | Public `classify`, `freeze`, `prepare`, `submit`, `record`, `verify`, `waive`, and `hook` commands. It composes the core APIs and owns no worker default. |

The core API names are:

```python
review_packet.prepare_packet(repo, freeze_file)
review_packet.load_packet(repo, freeze_identity)
review_packet.verify_packet(repo, packet, freeze_identity)

review_receipt.submit_result(
    repo, freeze_file, reviewer, attribution, result, adapter=None
)
review_receipt.record_receipt(repo, freeze_file, output=None)
review_receipt.verify_receipt(repo, document, identity, scope_for_paths)

review_common.REVIEW_SPECS
review_common.skill_identity(reviewer)
review_common.worker_attribution(actor, harness, model, run_id)
```

The result schema is `omp.review-result.v1`; gate-owned pass artifacts use
`omp.review-pass.v3`; the final receipt uses `omp.review-receipt.v3`.

## Trivial prose/config waiver

Use the explicit waiver command only for an inert prose/config-only range
outside policy paths. Policy files, including `global/skills/**` and
`SKILL.md`, remain substantive even when their contents are prose.
`.gitattributes` remains substantive because it can change how later evidence
is rendered. A waiver cannot authorize policy, executable, or
evidence-rendering changes.

```bash
python3 bin/review_gate.py waive \
  --repo . \
  --actor "<stable-name-or-email>" \
  --reason "prose-only documentation change with no executable or policy behavior"
python3 bin/review_gate.py verify --repo .
```

## Closeout

Report the frozen `bundle_digest`, exact reviewer identities, worker
attributions, submission statuses, command exit statuses, finding counts,
fixes and refreezes, and the final `record` plus `verify` commands. Include
residual risk and evidence in the `global/references/verification-system-first.md` evidence packet.
Do not call the review complete from one submission, an optional critic, a
prose-only summary, a hand-authored artifact, or a stale receipt.
