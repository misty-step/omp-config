# Review gate FSM

Fixed protocol for committed-range review receipts.
Implementation: `bin/review_gate.py`, `bin/review_bundle.py`, `bin/review_receipt.py`, `bin/review_common.py`.
Tests: `tests/test_review_gate.py`, `tests/test_protocol_fsms.py`.

## States

| State | Durable mark |
|---|---|
| `idle` | no freeze for the range |
| `frozen` | `.omp/review-freeze.json` matches old/new oid + bundle identity |
| `prepared` | packet/pass slots ready for required reviewers |
| `passes_partial` | one or more pass files recorded; set incomplete |
| `passes_complete` | every required reviewer has a clean matching pass |
| `receipted` | `.omp/review-receipt.json` recorded for the freeze identity |
| `verified` | `verify` recomputed digests and accepted the receipt |
| `failed` | gate error; remain fail-closed until refreeze or repair |

Terminal happy path for ship claims: `verified`.
Superseded range: any commit that changes the frozen range invalidates prior receipt (`idle` or must refreeze).

## Legal transitions

| From | Event | To |
|---|---|---|
| `idle` | `freeze` (valid oids, clean worktree policy) | `frozen` |
| `frozen` | `prepare` | `prepared` |
| `prepared` | `submit` clean pass for required reviewer | `passes_partial` or `passes_complete` |
| `passes_partial` | `submit` remaining clean passes | `passes_partial` or `passes_complete` |
| `passes_complete` | `record` | `receipted` |
| `receipted` | `verify` success | `verified` |
| any pre-verify | identity drift / forge / schema obsolete | `failed` |
| `failed` or superseded | `freeze` new range | `frozen` |

Reviewer floor comes from `floor_plan` / `REVIEWERS` in `review_common.py`.
Lane skill name `ponytail` is the method skill; structure critic agent is `sculptor`.

## Illegal transitions (must fail closed)

- `verify` or ship claim from `idle` / `frozen` / `prepared` / `passes_partial`
- `record` before all required clean passes
- `submit` with wrong bundle digest, oid pair, or obsolete schema
- reuse receipt after range bytes change without refreeze
- duplicate harness run identity with different bytes
- status/findings disagreement on a pass
- empty required reviewer set when floor plan requires lanes

## Process proof

Protocol changes here need process-adversarial coverage: see
`global/references/process-adversarial-testing.md`.
