---
name: evidence-packet
description: Plan, capture, inspect, and deliver reviewable proof for changes to observable UI, CLI, TUI, API, runtime, persisted state, performance, or infrastructure behavior.
---

# Evidence Packet

```text
plan -> capture baseline -> change -> capture result -> inspect -> deliver
```

An evidence packet connects each claim to a real scenario, an observed result,
and a reviewable artifact. It does not create a guarantee that the available
runtime cannot prove.

## Plan

Before a production edit, record a compact evidence plan:

```yaml
claims:
  - statement: <observable result>
    surface: <real interface>
    scenario: <exact actions>
    fixture: <sanitized state>
    evidence: <screenshot, video, terminal, request-response, state, trace, or metric>
    baseline_required: <true or false>
```

Use `baseline_required: true` for a fix, regression, comparison, or performance
claim. Use `false` for a new surface that has no useful prior state.

Use no evidence packet only when the change has no observable behavior or state
claim. State the reason. Tests and source inspection do not make an observable
change non-observable.

Read the applicable branch before capture:

- UI or other visual state: `UI.md`;
- CLI, TUI, API, state, concurrency, performance, or infrastructure:
  `NONVISUAL.md`.

## Capture

Capture a required baseline before the production edit. Use an isolated checkout
at the baseline source when necessary. Do not reset or change operator work.

Use the existing real interface:

- `browser` for browser interaction and screenshots;
- the repository's existing Playwright, Cypress, or application recorder for
  video;
- `bash` or `hub` for CLI and TUI execution;
- real requests and owner-boundary state reads for API and persistence proof.

Use the same scenario and fixture for comparative captures. Keep each artifact
outside the product repository.

For every artifact, record:

```yaml
claim: <claim statement>
phase: <before or after>
source_revision: <commit and dirty-state note>
runtime_identity: <observed identity, inferred identity, or unavailable>
scenario: <exact actions>
fixture: <sanitized fixture>
artifact: <local path or delivered URL>
observation: <observed result>
```

Do not label an inferred runtime identity as verified. If the runtime does not
report its revision, state that the identity is unavailable.

A test protects future behavior. It does not replace current real-surface
evidence.

## Inspect

After the final behavior change, repeat the exact result scenario. Recapture the
result after a behavior-affecting source or runtime change.

Open every artifact. Confirm that:

- the file opens;
- it shows the declared scenario;
- it supports the claim;
- it contains no secret or unrelated operator data;
- its recorded source and runtime identity are accurate at the stated confidence.

Record an evidence gap only after a concrete safe attempt. State the exact
blocker, the attempt and result, the strongest substitute, and each unproved
claim.

## Deliver

Read `DELIVERY.md`. Publish only when the user requested a PR or another public
write. Do not commit evidence media to the product repository.

Finish only when:

- every claim has the required baseline and result evidence, or an explicit
  evidence gap;
- every artifact was opened and inspected;
- the final response links delivered evidence or gives local artifact paths;
- every runtime-identity limitation and evidence gap is visible.
