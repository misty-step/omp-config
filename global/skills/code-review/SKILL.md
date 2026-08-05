---
disable-model-invocation: true
name: code-review
description: Apply the frozen committed-range review protocol with three independent submissions and gate-owned evidence. Trigger: /code-review, /review.
argument-hint: "[branch|diff|files]"
---

# /code-review

Run the harness-neutral substantive review protocol. Callers load review skills,
supply worker attribution, and submit v1 results. The gate owns range, passes,
receipt, and verification. Leaves own no orchestration, provider, model,
or invocation route.

Review is **encouraged, not enforced**. The pre-push `hook` runs in advisory
mode by default: it warns with the exact commands when a range lacks a clean
receipt and lets the push through. Repositories that want hard blocking opt in
with `--enforce`. When the sequence IS run, its artifacts are immutable and
gate-verified — the receipt remains the evidence standard for completion claims.

Review order:

1. `autoreview`
2. `thermo-nuclear-review`
3. `thermo-nuclear-code-quality-review`

The last two are standalone skills:

```text
global/skills/thermo-nuclear-review/SKILL.md
global/skills/thermo-nuclear-code-quality-review/SKILL.md
```

Neither invokes `/code-review`, another workflow, or a nested reviewer.
`thermos/skills` may remain in external sync metadata as provenance only.

## Sequence and CLI

```text
freeze -> submit -> record -> verify
```

No aggregate substantive invocation command exists.

| Command | Contract |
|---|---|
| `classify` | Classify range: `trivial` or `substantive`. |
| `freeze` | Recompute range; write fixed `.omp/review-freeze.json`. |

| `submit` | Read `omp.review-result.v1` from file or stdin for either official leaf; require attribution; write gate-owned pass. |
| `record` | Discover exactly three canonical passes; write `.omp/review-receipt.json`. |
| `verify` | Recompute range, packets, passes, receipt, and skill digest. |
| `waive` | Write actor-attributed waiver for an inert trivial prose/config-only range. |
| `hook` | Advisory pre-push check (default): warn with guidance when the receipt is missing; `--enforce` blocks the push. Safety failures (malformed ref updates, protected-branch deletion) always block. |

Exit status: `0` clean evidence; `1` valid non-clean `submit` result; `2`
protocol, schema, range, or artifact failure. `record` and `verify` return `2`
for an incomplete or non-clean required set.

## Enforcement model

- **Advisory (default):** the pre-push hook computes the pushed range and
  prints one of three outcomes: clean receipt, trivial-waiver guidance, or
  the exact `freeze -> submit -> record -> verify` commands to record
  evidence. It exits 0 either way. The push is never blocked for missing
  review evidence.
- **Enforced (opt-in):** `python3 bin/review_gate.py hook --repo . --enforce`
  (or a repo-local wrapper) restores the hard block for ranges without a
  clean receipt or waiver. Use it for release trains, high-risk surfaces,
  or operator-mandated repositories.
- **Safety always enforced:** malformed pre-push input and deleting a
  protected default branch fail the push in both modes.
- When the sequence runs, the gate fails closed if frozen range, result
  shape, attribution, passes, receipt, or projected skill digest changes. A
  clean substantive receipt requires three `clean` submissions, zero
  actionable findings, empty findings, and distinct `(harness, run_id)`
  pairs. A non-clean result requires fix, refreeze, and the complete
  sequence. Malformed or stale artifacts are protocol failures.

```bash
REPO=.
GATE=bin/review_gate.py
OLD_OID="$(git merge-base <base-ref> HEAD)"
NEW_OID="$(git rev-parse HEAD)"

python3 "$GATE" freeze --repo "$REPO" \
  --old-oid "$OLD_OID" --new-oid "$NEW_OID"

python3 "$GATE" submit --repo "$REPO" \
  --reviewer autoreview \
  --actor "$AUTOREVIEW_ACTOR" --harness "$AUTOREVIEW_HARNESS" \
  --model "$AUTOREVIEW_MODEL" --run-id "$AUTOREVIEW_RUN_ID" \
  --result "$AUTOREVIEW_RESULT"
python3 "$GATE" submit --repo "$REPO" \
  --reviewer thermo-nuclear-review \
  --actor "$LEAF_ACTOR_A" --harness "$LEAF_HARNESS_A" \
  --model "$LEAF_MODEL_A" --run-id "$LEAF_RUN_ID_A" \
  --result "$LEAF_RESULT_A"
python3 "$GATE" submit --repo "$REPO" \
  --reviewer ponytail \
  --actor "$LEAF_ACTOR_B" --harness "$LEAF_HARNESS_B" \
  --model "$LEAF_MODEL_B" --run-id "$LEAF_RUN_ID_B" \
  --result "$LEAF_RESULT_B"

python3 "$GATE" record --repo "$REPO"
python3 "$GATE" verify --repo "$REPO"
```

`submit` accepts only the two official leaf names. Direct leaves must provide
`actor`, `harness`, `model`, and `run_id`; the core chooses no defaults.
Official leaves use distinct harness/run-id pairs.
Adapter-executed `autoreview` requires attestation. `review_runner.py run-one`
may invoke one skill and supplies attestation through the same seam. It does not
define semantics, select model/provider/harness, create another receipt path, or
replace this sequence; direct callers may omit it.

The gate fails closed if frozen range, packet bytes, result shape, attribution,
passes, receipt, or projected skill digest changes. A clean substantive receipt
requires three `clean` submissions, zero actionable findings, empty findings,
and distinct `(harness, run_id)` pairs. A non-clean result requires fix,
refreeze, and the complete sequence. Malformed or stale artifacts are protocol failures.

## Committed range

Review committed objects, never mutable worktree bytes. Resolve the base with
`git merge-base <base-ref> HEAD`, or the exact pre-push old object in a hook; set
`NEW_OID` with `git rev-parse HEAD`. `freeze` rejects dirty worktrees for frozen
paths and records the repository, old/new object ids, ordered introduced commits,
sorted changed paths, and `bundle_digest` (`sha256:` plus 64 lowercase hexadecimal characters).

Never reuse freeze, packet, pass, or receipt after the range changes. Commit the
fix, freeze, prepare, collect all three submissions, record, and verify again.

## Artifacts and Worktrees

Workers execute in read-only worktrees checked out at `new_oid`. They read `git diff` directly.
No packet re-serialization or byte redaction layer exists.
`submit` normalizes `omp.review-result.v1`, rejects missing, malformed,
non-integer, or negative finding counts, and never coerces invalid data to zero.
It writes exactly one gate-owned `omp.review-pass.v3` per canonical reviewer:

```text
.omp/review-passes/autoreview.json
.omp/review-passes/thermo-nuclear-review.json
.omp/review-passes/thermo-nuclear-code-quality-review.json
```

Callers cannot choose pass paths or hand-author substitutes. `record` reads these
files in canonical order, binds digests to `.omp/review-receipt.json`, and records
the v3 receipt. `verify` re-reads bound paths, recomputes Git identity and packet
digest, validates skill identity, and checks attribution.

## Projected modules

| Module | Owns |
|---|---|
| `bin/review_common.py` | `REVIEW_SPECS`, `floor_plan`, v1/v2/v3 schema names, digest/identity validation, `skill_identity`, explicit `worker_attribution`; no defaults. |
| `bin/review_bundle.py` | Git range identity, bundle digest, planned lanes, confined artifact paths, freeze loading, committed-range checks. |
| `bin/review_receipt.py` | `submit_result`, v3 passes, `record_receipt`, `verify_receipt`, binding, clean enforcement. |
| `bin/review_gate.py` | Public `classify`, `freeze`, `submit`, `record`, `verify`, `waive`, `hook`; core composition, no defaults. |

```python
review_receipt.submit_result(
    repo, freeze_file, reviewer, attribution, result, adapter=None
)
review_receipt.record_receipt(repo, freeze_file, output=None)
review_receipt.verify_receipt(repo, document, identity, scope_for_paths)

review_common.REVIEW_SPECS
review_common.floor_plan(paths)
review_common.skill_identity(reviewer)
review_common.worker_attribution(actor, harness, model, run_id)
```

Result: `omp.review-result.v1`; pass: `omp.review-pass.v3`; receipt: `omp.review-receipt.v3`.

## Trivial prose/config waiver

Use `waive` only for inert prose/config-only ranges outside policy paths.
`global/skills/**` and `SKILL.md` remain substantive even for prose.
`.gitattributes` remains substantive because it can change evidence rendering.
A waiver cannot authorize policy, executable, or evidence-rendering changes.

```bash
python3 bin/review_gate.py waive \
  --repo . \
  --actor "<stable-name-or-email>" \
  --reason "prose-only documentation change with no executable or policy behavior"
python3 bin/review_gate.py verify --repo .
```

## Closeout

Report `bundle_digest`, exact reviewer identities, worker attributions, submission
and command statuses, finding counts, fixes/refreezes, and final `record` plus
`verify` commands. Put residual risk and evidence in the
`global/references/verification-system-first.md` evidence packet. Do not call
review complete from one submission, optional critic, prose summary, hand-authored
artifact, or stale receipt.
