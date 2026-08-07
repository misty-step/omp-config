# Product

Load this reference after `/quality` selects `product`. It supplies the live product oracle and QA tracks.

## Boundary and entrypoints

Audit real non-production entrypoints only. Allowed environments are exactly `local`, `dev`, and `staging`; never target production.

Use a read-only discovery lane to inspect docs, routes, scripts, rules, and live surfaces. Record each entrypoint's kind, exact URL or command, and exact environment. Require an HTTP status, rendered page, or command transcript. Never infer an entrypoint or a result.

## Frozen target and input

Record every entrypoint's golden paths, invariants, user-visible errors, and strengths in `.evidence/quality/product/product-target.md`. Put each golden path and invariant in a deterministic scenario row or a persona mission.

Freeze `.evidence/quality/product/input.v1.json` before persona execution. Derive it only from the discovery inventory and product target. The `skill://qa-users` contract owns its schema and semantic validation. The frozen input is authoritative for personas, missions, browser entrypoints, environments, and execution limits. Any added, removed, or reshaped input voids the run.

Each frozen browser entrypoint declares `real: true` and an allowed environment. A persona uses only its assigned frozen entrypoint.

## Deterministic track

Maintain one frozen scenario row per scenario with these fields:

| Field | Required content |
|---|---|
| `id` | stable scenario identifier |
| `entrypoint` | entrypoint from the discovery inventory |
| `preconditions` | exact fixture data, authentication, flags, and seed |
| `steps` | numbered user actions |
| `expected` | observable result stated before execution |
| `evidence` | screenshot, snapshot, status, console line, or transcript to capture |

A fresh, non-mutating `verifier` runs every row through `skill://verify` (live branch). Return `PASS`, `WARN`, `FAIL`, or `SKIP` with the exact interaction or command and observed result. `SKIP` names its blocker.

Keep rows deterministic and re-runnable. Do not depend on wall-clock time or row order. Reproduce a failure before recording it. Cover every golden path, invariant, and hostile edge: invalid input, empty state, authentication failure, double submit, refresh mid-flow, back navigation, and concurrent session.

## Persona track

Dispatch `qa-master` with `skill://qa-users`. It explores when needed, freezes `input.v1`, and dispatches exactly one browser-only `qa-persona` per configured persona. A persona receives mission, knowledge, and blind_spots, not a script.

Each persona returns exact steps, expected versus observed behavior, runtime evidence references, strengths, friction, and `failure_reason` when its mission fails. Preserve strengths and all friction, including friction below the finding threshold. A persona never reads product source, edits source, files issues, or invents an entrypoint. The master never runs a full persona mission on its own browser session.

The deterministic and persona tracks are complementary. Neither track replaces the other.

## Evidence triage and deduplication

Record evidence during exploration. Use a video for an interactive reproduction and one annotated screenshot for a static reproduction. Store heavy payloads as artifact paths, not inline report content.

`qa-master` confirms each candidate before synthesis. Each confirmed finding records its affected entrypoint, exact steps, expected behavior, observed behavior, evidence, severity, confidence, and category. Record a root cause only when runtime evidence establishes it.

One serialized chief tracker writer exhaustively scans every tracker page or cursor. It blocks on ambiguity or truncation. Deduplicate with the canonical SHA-256 finding fingerprint from `skill://qa-users` plus `affected_entrypoint`. File only actionable, evidence-backed findings within the frozen create ceiling, then read every created issue back. Accepted and matched findings retain their tracker issue identifier.

Do not mutate a user session. Use `fix-and-pr` only when `skill://qa-users` authorizes it after filing and read-back, with `inside_user_session: false`.

## Independent proof

A fresh, non-mutating verifier re-runs every failing deterministic scenario with the same steps, oracle, and live entrypoint. Redispatch personas for changed paths through `skill://qa-users`. Close a remediated finding only on live `PASS` evidence. A destroyed product strength is a regression, not closure.

## Evidence location

Store product evidence under `.evidence/quality/product/`. Keep `product-target.md`, frozen `input.v1.json`, `assessment.json`, and rendered `assessment.md` there. Link every scenario verdict, persona result or failure reason, finding, fingerprint read-back, remediation result, independent proof, strength, friction item, and blocker to evidence in that directory.
