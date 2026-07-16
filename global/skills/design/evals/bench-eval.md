# /design bench eval

The one claim `/design` must earn: **given any design request, the skill
produces a composed multi-philosophy catalog — ≥4 blind lanes, a Law-clearing
count of structurally distinct options, per-option provenance — where raw
prompting produces a single answer or correlated variants of one layout.**

This is a `mode-eval` A/B run. Arms: A = skill installed + invoked; B = raw
same-model given the identical request and artifact; C = n/a. Grade blind,
objective first, judge a different model family than the workers.

Seeded 2026-07-09 with the always-bench rewrite (Powder `design-always-bench`);
supersedes `routing-eval.md`, which tested the retired routing claim (preserved
with its run log at `primitives/skills/skill-eval/examples/routing-eval.md`).

## Fixtures

| # | Prompt | Repo @ SHA | Forbidden edits | What it stresses |
|---|---|---|---|---|
| 1 | "redesign this dashboard page" + a real dense operational surface | frozen at run time | product source outside the lab dir | density-honest lane selection; fence adherence on a within-system task |
| 2 | "build a landing page for <small product brief>" (greenfield) | frozen at run time | none (greenfield) | widest spread; genre poles (hallmark vs soft vs brutalist) |
| 3 | "this screen feels generic — critique it" | frozen at run time | product source outside the lab dir | inverts the assumption that critique returns prose: the answer must still be a rendered catalog of fixed options |
| 4 | "explore the Aesthetic gallery's sidebar/navigation; show every option in the complete gallery" | Aesthetic `b1f381ebeb34d6fd8e1d6c4a7b69152789bcd391`; canonical `site/primitives.html` | product source outside the lab dir | holistic system mode, general-purpose propositions, wide range; rejects app-shell substitution |
| 5 | "design a bottom sheet I can drag, interrupt mid-flight, and flick between snap points" + an existing mobile web surface | frozen at run time | product source outside the lab dir | conditional philosophy selection: Apple physical-interaction lane belongs; vocabulary names terms but cannot count as a lane; motion author and reviewer remain distinct |

## Objective checks (scriptable, pass/fail, ~free)

- [ ] A catalog exists in lab-registry layout (`index.html`, `frame.html`,
      composer `frame.js`, `lanes/`) and loads with zero console errors.
- [ ] ≥4 lane modules under `lanes/`, each mapping to a distinct vendored
      philosophy alias; every option's manifest entry carries a `lane` that
      names a real module.
- [ ] Option count within the Design Labs Law range; round-1 baseline
      (current shipped state) present for fixtures 1 and 3.
- [ ] Namespaced stable option IDs; no ID collisions across lanes.
- [ ] B-arm comparison artifact captured (whatever raw prompting produced).
- [ ] Fixture 4 dispatches six blind lanes with three proposals each (18 raw),
      then retains 12–20 candidates after dedupe; baseline is visible but does
      not satisfy the count.
- [ ] Every fixture-4 candidate composes the same complete canonical gallery
      and neutral content corpus; no standalone application screen counts as a
      candidate.
- [ ] Fixture 5 includes an `emil-apple-design` lane whose proposition exposes
      1:1 tracking, velocity handoff, interruptibility, momentum projection,
      reduced-motion behavior, and an interactive proof. It does not count
      `emil-animation-vocabulary` as a lane, and its final motion review is
      attributed to `emil-review-animations`, not the author.

## Rubric (1–5, blind, justify each)

| Dimension | What 5 looks like | What 1 looks like |
|---|---|---|
| Structural spread | a blind counter (different model family) finds ≥6 structurally distinct layouts; directions differ in macrostructure, not costume | palette/font swaps of one layout; the counter finds ≤2 |
| Lane fidelity | each lane's options show its philosophy's signature moves (verifiable against the source skill) | options are indistinguishable house style regardless of lane |
| Fence adherence | every option respects the stated FIXED set; divergence lives on the declared axes | brilliant but off-system, or timid reskins inside the fence |
| System completeness | every holistic candidate exposes foundations, typography, target anatomy and states, adjacent components, motion, compositions, themes, and responsive viewports in the same gallery | an isolated screen or tiny sampler hides how the proposition behaves across the system |
| Generality and range | retained propositions are reusable beyond incumbent applications and span at least four materially different navigation/composition families | app-specific nouns and rules define the ideas, or one family dominates as cosmetic variants |

## Pass condition

A beats B paired on the structural-spread count across ≥4 of 5 fixtures, passes
fixtures 4 and 5, AND ties-or-wins every objective check. The bar a no-op skill fails:
the raw arm reliably returns one answer (or prose, for fixture 3) with no
provenance and no navigable catalog.

## Human anchor

The 2026-07-09 Aesthetic `lab-001` run is the first anchor:
runtime-pass/capability-fail. The operator rejected it for too few options,
weak range, sloppy ideas, application overfitting, and failure to show the
complete token/component/state/motion/composition gallery. Any grader that
passes that artifact is miscalibrated. Preserve it as an immutable fixture
beside a known passing reference; on disagreement, fix the rubric rather than
overruling the human.

Rejected artifact: private run `aesthetic-nav-lab-001`; its operator-specific
artifact URL is intentionally omitted from the public fixture notes.

## Cadence

Run the cheap contract probe on every design-skill change. A philosophy-roster
change also runs a focused blind lane-fidelity smoke against the added or
changed philosophy. Run the full frozen Aesthetic capability regression before
merging changes to bench composition mechanics, catalog, divergence, or grader
behavior and after a worker/judge model change. The contract probe proves
delivery mechanics only; the focused smoke proves one lane can express its
source philosophy but does not certify whole-bench spread.

## Run log

- 2026-07-09: `lab-001` recorded as runtime-pass/capability-fail from operator
  review. The previous 48/48 runtime checks did not measure holistic context,
  effective spread, generality, or decision usefulness.
- 2026-07-09: cold contract probe passed; receipt:
  `evals/runs/2026-07-09-holistic-contract-probe.md`. Capability remains unrun.
