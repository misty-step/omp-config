---
name: design
description: |
  Interface and design-system design by parallel bench: every /design
  invocation fans out blind
  subagent lanes — each obeying one vendored design philosophy end to end —
  and composes their rendered explorations into one clickable lab catalog the
  operator browses and gives verdicts on. Needs a screenshot, URL, rendered
  artifact, or file plus intent. Use when: "improve the design", "redesign
  this", "critique this screen", "show me options", "prototype this", "deslop
  this", "polish the UI", "is this accessible", "scaffold DESIGN.md", or any
  product-facing visual artifact — docs layout, dashboards, charts, diagrams.
  Do not use when: a mechanical style fix with no design decision (just make
  the edit), or behavior verification (/qa). Trigger: /design, /prototype.
argument-hint: "<artifact-or-surface> [intent]"
---

# /design

One method, every invocation — no routes, verbs, modes, or preset menus. A
design request never picks a specialist; it benches them:

**fence → bench → catalog → verdicts → converge**

One context brainstorming N variants produces one taste wearing costumes. Real
spread comes from blind parallel lanes, each obeying a different vendored
philosophy end to end. The operator decides from rendered options, never from
a menu of style names — and the pick is never delegated to the model.

## Fence

Name the artifact and its intent in one sentence. Read `DESIGN.md` when
present; scaffold it for recurring product-facing work
(`references/scaffold.md`). State what is FIXED (tokens, brand, platform, a11y
floor) and which axes vary — `references/divergence.md` owns the per-mode axes
and fan-width calibration. Set VARIANCE / MOTION / DENSITY targets
(`references/anti-slop.md`). When the operator supplies reference sites or
screenshots, the DNA-not-dress protocol in
`references/external-design-references.md` binds every lane. Route to `/shape`
first when the product direction itself is unsettled.

When motion intent arrives as a vague effect without a name, load
`emil-animation-vocabulary` before fencing it. The glossary sharpens the brief;
it does not join the generative bench.

When the target is itself a design system or component library—or the request
changes shared tokens, recurring components, or multi-surface grammar—classify
it as a **holistic system lab** and read `references/design-system.md` before
dispatch. A named primitive is the variable inside the system, not the whole
option.

## Bench

Fan out 4–6 blind lanes in parallel (the harness's subagent capability;
sequential fresh-context lanes where it has none — blindness is the
requirement, parallelism the speed). Each lane card is three lines: the fence,
the path to one philosophy's `SKILL.md` ("read it fully; obey it"), and the
lane output contract (`references/lab-registry.md` § Lane modules). Each lane
returns 1–3 structurally distinct options. Lanes get the fence and the
contract only — never each other's output or your reasoning trail (shared
AGENTS.md: Prove).

For a cheap zero-build holistic system lab, use six blind philosophies and
require three proposals from each before dedupe. This is an exploration floor,
not permission to keep weak work.

The philosophies (vendored under `primitives/skills/.external/`; licences and
boundaries in `references/external-design-references.md`):

| Lane | Brings |
|---|---|
| `anthropic-frontend-design` | distinctive aesthetic thesis; calibration against the known AI default looks |
| `emil-apple-design` | fluid physical interaction: direct manipulation, interruptibility, velocity, momentum, spatial continuity, and material depth |
| `leon-taste-skill` | metric-based anti-default rules; the dials |
| `leon-soft-skill` | glossy, luxe, agency-tier |
| `leon-minimalist-skill` | flat editorial (Notion/Linear), no gradient or shadow |
| `leon-brutalist-skill` | raw industrial-terminal, Swiss print × military terminal |
| `leon-gpt-tasteskill` | GSAP scroll choreography, AIDA macrostructure |
| `leon-images-taste-skill` | image-first: generate design images, build to match (image-gen runtime is live) |
| `leon-redesign-skill` | keep-the-stack redesign; a11y/SEO omissions checklist |
| `nutlope-hallmark` | macrostructure-first genres, 20-theme rotation, 58-gate slop test |
| `impeccable-impeccable` | 23 discipline lenses (typeset, colorize, distill, harden, …); brand-vs-product register |

Pick the spread against the fence, not a fixed roster: a dense operational
surface benches density-honest philosophies; a landing page benches hallmark's
genres against the soft and brutalist poles. Gesture-driven, sheet, spring,
drag/swipe, or spatial-motion surfaces bench `emil-apple-design`; static visual
work usually does not. `references/aesthetic-library.md` holds six
operator-endorsed directions lanes can seed from.

## Catalog

Compose the lab-registry paged viewer (`references/lab-registry.md`): one
full-viewport page per option, adjustable viewport, arrow-key nav. Dedupe
cross-lane reskins, refill to the applicable target, include the current
shipped state as the round-1 baseline, and badge every option with its originating
philosophy — provenance is how verdicts feed back ("kill everything from that
lane") and how each vendored skill earns its keep.

**The Design Labs Law (stated here only; everything else points here):** the
candidate catalog holds **6–20 structurally distinct propositions**, scaled to
render cost. The round-1 baseline is shown separately and never satisfies the
count. Six is the floor for expensive options, not the default stopping point;
cheap zero-build and holistic system labs retain **12–20** candidates after
dedupe. Palette/font swaps of one layout count as one option. The pick is the
operator's.

In a holistic system lab, one option means one reusable system proposition
rendered through the same complete gallery contract. A standalone application
screen is a supplemental stress test, not an option.

## Verdicts

Rounds per the registry contract: the operator kills, mutates, locks; sections
refill toward the Law. Mutations return to the originating lane's philosophy;
`nous-creative-ideation` methods (SCAMPER, lateral provocations) drive
within-lane mutation and round reseeding. Anything the operator phrases as a
definite fix ships immediately, outside the lab.

## Converge

Build the locked winner in the real stack; update `DESIGN.md` when a durable
fact changed; the lab is a sketch — never ship its files. Convergence gates:

| Gate | Source |
|---|---|
| slop | `references/anti-slop.md` quick gate + `npx impeccable detect` (exit 2 on findings) |
| micro-polish | `jakub-make-interfaces-feel-better` — exact radii, optical alignment, hit areas |
| motion | `emil-emil-design-eng` to author, `emil-review-animations` to review |
| a11y / guidelines | `vercel-web-design-guidelines`; WCAG AA contrast, keyboard reach; checklist in `references/interface-polish.md` |
| React architecture | `vercel-composition-patterns`, `vercel-react-view-transitions` |

For substantive or external-facing changes, approval is earned, default-deny:
one fresh-context design-director read plus the deterministic scan,
synthesized — not concatenated. Presumptive blockers the author must justify:

- an off-system value (color / spacing / radius / type) not in the repo's tokens;
- a surviving slop tell from `references/anti-slop.md`;
- contrast below WCAG AA, or an interactive control unreachable by keyboard;
- no distinctive decision — the surface is template-clean but anonymous;
- meta-copy: UI that explains the agent's process instead of naming the thing;
- a catalog below the Law, or cross-lane "options" that are reskins of one layout.

After visible changes, verify desktop and mobile render and report the
evidence. Use `/qa` for behavior verification and evidence capture. Delegate
per the Shared Operating Spine (Act).

## Completion Gate

See `primitives/shared/AGENTS.md` (Prove) for the shared core;
design-specific fields:

```markdown
**Completion Gate**
- Fence: artifact, intent, fixed vs varying, dial targets.
- Lanes: philosophies fanned, options returned per lane.
- Catalog: lab path, option count vs the Law, round number, baseline present.
- Verdict state: locked winner (option id) or awaiting operator verdicts.
- Converge evidence: desktop+mobile render evidence; `npx impeccable detect` result.
- DESIGN.md: read, created, updated, or waived one-off.
- Residual risk: remaining design, a11y, or QA risk.
```

## Gotchas

- A lane that skims its philosophy emits house-style output — the philosophy
  IS the decorrelation. Spot-check each lane's options against its source
  skill's signature moves before composing.
- Two lanes can converge on the same obvious layout; dedupe counts them once.
- Critique and audit asks get the catalog too: findings render as fixed
  options in the viewer, not as a prose report.
- Aesthetic preference is not blocking unless it hurts comprehension, trust,
  conversion, accessibility, or domain fit.
- Never hide UI defects behind feature explanations. Point to the visible
  artifact and the concrete change.
- Meta-copy in UI is a design defect: real product policy, privacy,
  draft-state, or compliance copy is fine when the user is meant to see it;
  leaking the agent's caution is not.

## References

- `references/lab-registry.md` — the paged viewer and the lane output contract
  (file layout, namespaced IDs, provenance badges, round mechanics).
- `references/divergence.md` — per-mode variation axes, fence-naming,
  fan-width calibration, converge handoff.
- `references/anti-slop.md` — the single ban-core: slop tells, dials, quick gate.
- `references/external-design-references.md` — vendored-skill inventory,
  licences, DNA-not-dress reference work.
- `references/aesthetic-library.md` — six operator-endorsed aesthetic
  directions with runnable HTML examples.
- `references/scaffold.md` — repo-owned `DESIGN.md` and `design-contract.md`
  provenance.
- `references/design-system.md` — token and component-system judgment.
- `references/taste-layer.md` — direction menus and anti-generic critique
  lenses for seeding lanes.
- `references/interface-polish.md` — micro-polish and accessibility checks.
- `references/critique-shape.md` — the finding shape lanes use when annotating
  options.
- `references/ui-surface-routing.md` — composing `/design` + `/qa` +
  `/code-review` on visual diffs.
- `evals/bench-eval.md` — this skill's verification system.
