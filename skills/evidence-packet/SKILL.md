---
name: evidence-packet
description: Prove observable UI, CLI, API, runtime, state, performance, or infrastructure claims on the real surface.
---

# Evidence packet

Evidence connects one claim to one real scenario and observed result. Tests
protect future behavior; they do not prove the current runtime.

## Plan

Before production edits, record each claim, real surface, exact scenario,
fixture, evidence type, source revision, runtime identity, and whether a baseline
is required. Fixes, comparisons, state changes, and performance claims need a
baseline. A new surface may not.

Read `UI.md` for visual work or `NONVISUAL.md` for other surfaces.

Done when each claim has a proof that can fail.

## Capture

Capture required baselines before edits. Repeat the same scenario and fixture
after the final change. Use the real interface and record source revision,
dirty state, runtime identity confidence, actions, artifact, and observation.
Do not disturb operator state.

Done when every claim has comparable current evidence or a concrete gap.

## Inspect and deliver

Open every artifact. Confirm it shows the stated scenario, supports the claim,
has accurate identity, and exposes no secret or unrelated data. Read
`DELIVERY.md` before publishing. Attach reviewer-open artifacts only when a PR
or public write is requested; otherwise return inspected local paths.

State each failed attempt, substitute, and unproved claim. A local path or hash
alone does not complete PR evidence.

Done when every claim is proved or carries an explicit evidence gap.
