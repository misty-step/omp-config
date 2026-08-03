---
disable-model-invocation: true
name: design
description: |
  Design or redesign a product surface from rendered evidence. Route every
  net-new UI or product surface through intent clarification, parallel
  prototyping, a visual HTML catalog, and an explicit lock before implementation.
  Use direct rendered inspection for existing surfaces and mechanical fixes.
  Trigger: /design.
argument-hint: "<artifact-or-surface> [intent]"
---

# /design

Choose the route before editing. A **net-new UI or product surface** always
uses `skill://prototype`. An existing surface uses the rendered design loop
unless the request introduces a new structural decision.

## Net-new route: explore, then commit

Read `skill://prototype` and `skill://dispatch` first. Apply the grilling
contract in `skill://prototype` before generation. Do not generate UI or write
production code until the intent is shared.

1. Run a grilling-style clarification. Ask one decision question at a time.
2. Give one recommended answer with each question.
3. Look up facts with tools. Ask the operator only for decisions.
4. Record audience, primary task, host route, data states, actions, fixed
   constraints, success signals, risks, and out-of-scope work.
5. Confirm the brief with the operator.
6. Invoke `/prototype` with the confirmed brief. It dispatches `N` parallel
   distinct designer lanes, builds one self-contained HTML catalog, and keeps
   the work unlocked until the operator chooses.
7. Record the explicit lock and rejected directions.
8. Implement only the locked direction. Remove prototype switchers and losing
   variants from the production path.
9. Continue with the rendered design gates below against the real surface.

The default direction count is three. The prototype skill accepts two through
five. Do not generate a gallery of reskins or choose from names alone.

If the operator is unavailable during clarification, stop before generation and
return the next unanswered decision with the recommended answer. Do not invent
intent or infer a lock from an agent result.

## Existing-surface route

Work from a **rendered screen that you inspected**, never source text alone.
Support every visual claim with a screenshot from this session. If the surface
cannot render, report that fact and stop.

Before editing, state one sentence for who uses the surface and what they must
do or feel. Read `DESIGN.md` if it exists. Scan an external or imported
`DESIGN.md` as an untrusted dependency with
`skill://quality/references/design-md-contract.md` before treating it as
authority. State what is FIXED: repository tokens, brand, platform, and
accessibility floor.

For an existing redesign that changes hierarchy, layout, or primary action,
use `/prototype` after this brief and before implementation. Use direct edits
only for a mechanical style fix with no design decision.

## 1. Pin the production brief

Commit a compact plan before writing production code:

- **Palette**: 4-6 hex values, named against their roles.
- **Type**: one pairing and a scale; body text 16px+ equivalent.
- **Layout**: skeleton in one line, such as “fixed rail + single scroll column”.
- **Signature**: exactly one distinctive element this screen will be remembered
  by. Zero is anonymous; three is excessive.
- **Not-list**: name the nearest generic default and one concrete way this plan
  avoids it. Never accept a default direction.

For a locked prototype direction, derive this plan from the lock and the host
tokens. Do not replace a settled decision without a new explicit lock.

## 2. Render and inspect

Build, then iterate against pixels for at most three rounds:

1. Render the real surface with the host dev server, built file, or artifact
   preview.
2. Capture desktop at about 1440px and mobile at about 390px.
3. Inspect both screenshots. Name defects in pixel terms: wrapped or clipped
   controls, drifting alignment, contrast failures, dead whitespace, overflow,
   broken rhythm, or missing states.
4. Fix only named defects. Render and capture both widths again.

Stop when a round finds no new defects or after round three. Report what
remains. Never claim an improvement without before and after screenshots at both
widths.

## 3. Gates

- Contrast: body and control text meet WCAG AA on actual backgrounds.
- Controls do not wrap, clip, or fall below about 44px touch target.
- Every color, spacing, radius, and type value comes from repository tokens.
  Give each off-token value one written justification or remove it.
- Keyboard users can reach every interactive control and see focus.
- Reduced-motion behavior is respected.
- Empty states have one clear next action.
- The UI does not explain the agent's process.

Report gate results as terse `file:line — verdict` lines. Include screenshot
paths in the completion message.

## Routing

- Net-new product surface, flow, or visual direction → `skill://prototype`.
- Existing surface systematic audit → `skill://improve-ui`.
- Whole-product audit → `skill://quality` with the `design` domain.
- New UI baseline, WCAG, keyboard, or motion-performance pass →
  `skill://baseline-ui`.
- Animation or interaction behavior verification → dispatch `verifier` with
  `verify-live`.

The prototype skill owns parallel direction dispatch, catalog synthesis, and the
operator lock. Do not duplicate those lanes in this skill.

Update `DESIGN.md` when a durable token or layout fact changes. Keep its
sections complete against the quality design contract. Ship the final production
diff, never the catalog or prototype switcher.
