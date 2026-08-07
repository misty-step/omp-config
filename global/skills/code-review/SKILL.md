---
disable-model-invocation: true
name: code-review
description: >
  Run the frozen committed-range review protocol. Freeze a range, run the
  path-planned leaf reviewers, submit results, record and verify the receipt.
  Trigger: /code-review, /review.
argument-hint: "[branch|diff|files]"
---

# /code-review

Own the review **protocol**. Do not own leaf judgment.

The gate freezes a committed range, computes `planned_lanes` from changed
paths, accepts one `omp.review-result.v1` per planned lane, and verifies a
receipt. Leaves judge the diff. This skill does not replace a leaf.

Completion claims for code require a clean verified receipt for the frozen
range. Report `bundle_digest` with the claim.

## Sequence

```text
freeze → submit each planned lane → record → verify
```

```bash
GATE=bin/review_gate.py
OLD_OID="$(git merge-base <base-ref> HEAD)"
NEW_OID="$(git rev-parse HEAD)"

python3 "$GATE" freeze --repo . --old-oid "$OLD_OID" --new-oid "$NEW_OID"
# read planned_lanes from .omp/review-freeze.json, then for each lane:
python3 "$GATE" submit --repo . \
  --reviewer <lane> \
  --actor "$ACTOR" --harness "$HARNESS" \
  --model "$MODEL" --run-id "$RUN_ID" \
  --result "$RESULT_JSON"
python3 "$GATE" record --repo .
python3 "$GATE" verify --repo .
```

Optional: `classify` prints scope and planned lanes without writing artifacts.

| Command | Contract |
|---|---|
| `classify` | Optional preview of scope and planned lanes. |
| `freeze` | Bind range, paths, `planned_lanes`, and `bundle_digest`. Clear stale passes/receipt. |
| `submit` | One canonical reviewer from `REVIEW_SPECS`. Require actor, harness, model, run_id. |
| `record` | Build receipt from exactly the planned passes. |
| `verify` | Recompute identity; check floor ⊆ plan and passes == plan. |
| `waive` | Actor-attributed waiver for inert trivial prose/config only. |
| `hook` | Advisory pre-push by default; `--enforce` blocks without receipt/waiver. |

Exit: `0` clean; `1` valid non-clean submit; `2` protocol/schema/range failure.

## Dynamic floor

Source of truth: `review_common.floor_plan` and `review_scope` in
`bin/review_common.py` (see also ADR 0007). Freeze copies the result into
`planned_lanes` and binds it into `bundle_digest`.

Submit only the freeze `planned_lanes`, in order. Do not drop a floor lane.
Do not invent a reviewer outside `REVIEW_SPECS`.

Use `classify` or read the freeze file for the lane set. Policy paths and
`.gitattributes` stay substantive. Trivial waiver never authorizes policy,
executable, or evidence-rendering changes.

```bash
python3 bin/review_gate.py waive --repo . \
  --actor "<stable-name-or-email>" \
  --reason "prose-only documentation change with no executable or policy behavior"
python3 bin/review_gate.py verify --repo .
```

## Leaf roles

Each leaf is a separate skill. Leaves never invoke `/code-review` or each
other. Optional critics (extra panels, OpenCode, ad-hoc chat review) never
replace a planned lane.

| Lane | Skill | Job |
|---|---|---|
| `autoreview` | `global/skills/autoreview/SKILL.md` | Automated closeout: structured engine review, secrets scan, P0-default. |
| `thermo-nuclear-review` | `global/skills/thermo-nuclear-review/SKILL.md` | Correctness, security, breakage, feature-gate leaks, devex traps in the diff. |
| `thermo-nuclear-code-quality-review` | `global/skills/thermo-nuclear-code-quality-review/SKILL.md` | Maintainability: structure, spaghetti growth, bad abstractions, file bloat. |
| `ponytail` | `global/skills/ponytail/SKILL.md` | Erasure and YAGNI: delete unjustified surface, deps, and ceremony. |

Vendor copies under `global/external/` are provenance. Projected skill paths
above are the review authority.

### How to run a leaf

1. Read-only worktree (or checkout) at `new_oid`.
2. Load that lane's skill. Judge `git diff old_oid..new_oid` only.
3. Emit `omp.review-result.v1` with status, findings, and counts.
4. `submit` with real attribution. Distinct `(harness, run_id)` per lane.

`autoreview` requires adapter attestation on submit. Pass CLI flags
`--adapter-name`, `--adapter-executable`, `--adapter-executable-sha256`, and
`--adapter-engine` (or call `submit_result` with the same fields). Use
`global/skills/autoreview/openclaw_autoreview.py` (or the projected path) as
the executable. Direct leaf submits for thermos and ponytail need no adapter.

The chief (or caller) runs each planned leaf and submits results.

## Committed range

Review commits, not dirty worktree bytes. `freeze` rejects dirty frozen paths.
After a fix: commit, freeze again, rerun every planned lane, record, verify.
A receipt for a superseded range is not a receipt.

Workers read `git diff` directly.

## Artifacts

```text
.omp/review-freeze.json
.omp/review-passes/<lane>.json
.omp/review-receipt.json
```

Pass schema `omp.review-pass.v3`. Receipt schema `omp.review-receipt.v3`.
Result schema `omp.review-result.v1`.

Clean substantive receipt requires: every planned lane `status=clean`, zero
actionable findings, empty findings lists, matching skill digests, and
distinct harness/run pairs.

## Modules

| Module | Owns |
|---|---|
| `bin/review_common.py` | `REVIEW_SPECS`, `floor_plan`, `review_scope`, digests, skill identity |
| `bin/review_bundle.py` | Range identity, `planned_lanes`, `bundle_digest`, freeze load |
| `bin/review_receipt.py` | submit, record, verify, adapter attestation |
| `bin/review_gate.py` | CLI: classify, freeze, submit, record, verify, waive, hook |

## Enforcement

- **Advisory (default):** pre-push warns with exact commands; push proceeds.
- **Enforced:** `python3 bin/review_gate.py hook --repo . --enforce`
- **Safety always on:** malformed ref updates and protected-branch deletion fail closed.

RULES still require a clean receipt before completion claims when the sequence
applies. Advisory push does not waive that claim standard.

## Closeout

Report `bundle_digest`, `planned_lanes`, each lane status, attributions, and
verify output. Name residual risk. Do not call review complete from one leaf,
an optional critic, a prose summary, a hand-written receipt, or a stale digest.
