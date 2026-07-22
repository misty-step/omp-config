---
disable-model-invocation: true
name: design
description: |
  Design pass against rendered pixels: pin the brief, plan tokens with one
  signature element, build, then render-screenshot-fix until the gates pass.
  Needs a runnable screen or artifact plus intent. Use when: "improve the
  design", "redesign this", "polish the UI", "prototype this", "critique this
  screen", or any product-facing visual artifact. Options mode on request:
  2-4 blind parallel directions, each rendered and screenshot-verified.
  Do not use when: a mechanical style fix with no design decision (just make
  the edit), or behavior verification (dispatch `scully`). Trigger: /design.
argument-hint: "<artifact-or-surface> [intent]"
---

# /design

The unit of design work is a **rendered screen you have looked at**, never
source text. Every claim about visual quality must be backed by a screenshot
you took this session. If you cannot render it, say so and stop — do not
grade or restyle CSS from source.

## 1. Pin the brief

One sentence: who looks at this surface, and what must they be able to do or
feel. Read `DESIGN.md` if present; state what is FIXED (repo tokens, brand,
platform, accessibility floor) before touching anything.

Then commit a compact plan **before writing code**:

- **Palette**: 4-6 hex values, named against their roles.
- **Type**: one pairing and a scale; body text 16px+ equivalent.
- **Layout**: skeleton in one line (e.g. "fixed rail + single scroll column").
- **Signature**: exactly one distinctive element this screen will be
  remembered by. A screen with zero signatures is anonymous; one with three
  is noise.
- **Not-list**: name the nearest generic default (purple-gradient SaaS,
  Inter-on-white card grid, cream+serif broadsheet, dark-mode glassmorphism)
  and one concrete way this plan avoids it. Pick looks deliberately; never
  arrive at one by default.

## 2. The loop

Build, then iterate against pixels — at most three rounds:

1. Render the real surface (dev server, built file, or artifact preview).
2. Screenshot desktop (~1440w) and mobile (~390w).
3. **Look at the screenshots.** Name defects in pixel terms: wrapped or
   clipped controls, drifting alignment, contrast failures, dead whitespace,
   overflowing text, broken rhythm, missing states.
4. Fix only named defects. Re-render, re-shoot, re-look.

Stop when a round finds no new defects, or after round three — then report
honestly what remains. Never claim an improvement without before/after
screenshots at both widths.

## 3. Gates (self-run before showing anyone)

- Contrast: body and control text meet WCAG AA against actual backgrounds.
- No interactive control wraps, clips, or falls below ~44px touch target.
- Every color/spacing/radius/type value comes from the repo's tokens; each
  off-token value gets one written justification or gets removed.
- Keyboard: every interactive control reachable and visibly focused.
- No meta-copy: the UI never explains the agent's process.

Report gate results as terse `file:line — verdict` lines in the completion
message, with the screenshot paths.

## 4. Options mode (only when the operator asks for directions)

Fan out 2-4 blind parallel lanes, same brief, no shared output. Each lane
returns ONE direction: a modified copy, rendered, screenshotted at both
widths, plus its token plan. Present screenshots side by side; the operator
picks from pixels, never from style names. Kill reskins: two lanes that
produce the same layout with different paint count as one.

## 5. Routing

- Systematic UI audit of an existing app → `improve-ui`.
- Baseline hygiene rules for new UI → `baseline-ui`.
- WCAG/ARIA/keyboard deep pass → `fixing-accessibility`.
- Animation jank or scroll performance → `fixing-motion-performance`.
- Behavior verification and evidence capture → dispatch `scully`.

Update `DESIGN.md` when a durable token or layout fact changed; the lab copy
you iterated in is a sketch — ship the final diff, never the sketch files.
