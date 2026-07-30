---
disable-model-invocation: true
name: design
description: |
  Run a design pass against rendered pixels. Pin the brief, plan tokens with one
  signature element, build, then render, inspect, and fix until the gates pass.
  Need a runnable screen or artifact plus intent. Use when: "improve the
  design", "redesign this", "polish the UI", "prototype this", "critique this
  screen", or any product-facing visual artifact. Options mode on request:
  Use 2-4 blind parallel directions, each rendered and screenshot-verified.
  Do not use when a mechanical style fix has no design decision; make the edit
  directly. Do not use for behavior verification; dispatch `qa`. Trigger: /design.
argument-hint: "<artifact-or-surface> [intent]"
---

# /design

Work from a **rendered screen that you inspected**, never source text. Support
every claim about visual quality with a screenshot from this session. If you
cannot render it, report that fact and stop. Do not grade or restyle CSS from
source.

## 1. Pin the brief

Write one sentence that states who looks at this surface and what they must do
or feel. Read `DESIGN.md` if it exists. Before you edit, state what is FIXED
(repo tokens, brand, platform, accessibility floor).

Then commit a compact plan **before you write code**:

- **Palette**: 4-6 hex values, named against their roles.
- **Type**: one pairing and a scale; body text 16px+ equivalent.
- **Layout**: skeleton in one line (e.g. "fixed rail + single scroll column").
- **Signature**: exactly one distinctive element this screen will be
  remembered by. A screen with zero signatures is anonymous; one with three
  is excessive.
- **Not-list**: name the nearest generic default (purple-gradient SaaS,
  Inter-on-white card grid, cream+serif broadsheet, dark-mode glassmorphism)
  and one concrete way this plan avoids it. Choose the visual direction
  deliberately; never accept a default direction.

## 2. The loop

Build, then iterate against pixels for at most three rounds:

1. Render the real surface (dev server, built file, or artifact preview).
2. Screenshot desktop (~1440w) and mobile (~390w).
3. **Look at the screenshots.** Name defects in pixel terms: wrapped or
   clipped controls, drifting alignment, contrast failures, dead whitespace,
   overflowing text, broken rhythm, missing states.
4. Fix only named defects. Render again, take screenshots again, and inspect
   them again.

Stop when a round finds no new defects or after round three. Report what
remains. Never claim an improvement without before/after screenshots at both
widths.

## 3. Gates (self-run before showing anyone)

- Contrast: body and control text meet WCAG AA against actual backgrounds.
- No interactive control wraps, clips, or falls below ~44px touch target.
- Every color/spacing/radius/type value comes from the repo's tokens. Give each
  off-token value one written justification or remove it.
- Keyboard: every interactive control reachable and visibly focused.
- No meta-copy: the UI never explains the agent's process.

Report gate results in terse `file:line — verdict` lines. Include screenshot
paths in the completion message.

## 4. Options mode (only when the operator asks for directions)

Fan out 2-4 blind parallel lanes. Give each lane the same brief and no shared
output. Each lane returns ONE direction: a modified copy with a render and
screenshots at both widths. Include its token plan. Present screenshots side by
side. Let the operator choose from pixels, never style names. Discard reskins:
count two lanes as one when they share a layout and differ only in paint.

## 5. Routing

- Systematic UI audit of an existing app → `improve-ui`.
- Baseline hygiene rules for new UI → `baseline-ui`.
- WCAG/ARIA/keyboard deep pass → `fixing-accessibility`.
- Animation lag or scroll performance → `fixing-motion-performance`.
- Behavior verification and evidence capture → dispatch `qa`.

Update `DESIGN.md` when a durable token or layout fact changes. Treat the lab
copy as a sketch. Ship the final diff, never sketch files.
