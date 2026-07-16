# Emil Apple Design focused lane smoke — 2026-07-09

Purpose: philosophy-roster regression required by `bench-eval.md`. This is a
focused blind lane-fidelity smoke, not a whole-bench capability verdict.

## Fixture

Design one implementable interaction system for a mobile-web bottom sheet that
tracks a drag 1:1, can be interrupted mid-flight, and can be flicked among
three snap points. Fixed: Pointer Events, neutral existing tokens, reduced
motion. The cold lane received only this fence, the lane-module output shape,
and `emil-apple-design/SKILL.md`.

## Lane artifact: Continuous Glass Rail

- State: `resting → pressed → dragging → settling`; `pointerdown` captures the
  pointer, cancels an active spring, and resumes from presentation `y` plus
  current velocity. Ten-pixel vertical hysteresis separates drag from tap.
- Drag: `y = pointerY - grabOffset` inside bounds; Apple rubber-band resistance
  outside them with constant `0.55`.
- Release: velocity is fit over the last 80ms and clamped to ±4000px/s. The
  landing point uses Apple's exponential projection with rate `0.99`, then
  chooses the nearest of three snaps.
- Settle: response `0.32s`; damping ratio `0.82` after a ≥450px/s flick and
  `1.0` otherwise; measured release velocity initializes the spring. Rendering
  changes only `translate3d` in `requestAnimationFrame`.
- Material: translucent neutral sheet, 24px blur, bright top edge, depth tied
  to openness, scrim capped at `0.32`, and no stacked translucent children.
- Reduced motion preserves direct manipulation but disables projected travel
  and bounce on release. Reduced transparency replaces blur with an opaque
  surface; increased contrast adds a defined border.
- Keyboard parity: focusable handle, Arrow Up/Down moves one snap, Escape
  returns to the bottom snap.

## Runnable proof proposed by the lane

Automate slow drag, two flick velocities, overshoot, and mid-spring reversal at
60Hz and 120Hz. Assert ≤1px 1:1 drag error, ≤2px interruption discontinuity,
≤0.5px final snap error, identical target choice across refresh rates, and no
frame over 25ms. Emulate reduced-motion, reduced-transparency, and increased-
contrast media features and assert their declared fallbacks.

## Objective result

- 1:1 direct manipulation: PASS
- current-presentation interruption: PASS
- velocity handoff and momentum projection: PASS
- soft boundaries: PASS
- reduced-motion/transparency/contrast behavior: PASS
- keyboard equivalent: PASS
- measurable acceptance plan: PASS

Fresh grader verdict: **PASS**. The grader's first rubric overreached by
requiring an implemented command from a philosophy-proposal lane; after the
oracle was corrected to lane fidelity, no check failed. Executable UI proof
belongs to convergence and `/qa`. This smoke proves the new lane can express
its source philosophy; it does not prove whole-bench structural spread or
implementation performance.
