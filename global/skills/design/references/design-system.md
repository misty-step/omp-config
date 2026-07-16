# Design System Judgment

Use this reference when visual work touches recurring surfaces, shared
components, docs/report layouts, theme files, or visual rules that should remain
coherent across the product.

## Universal Craft vs Repo-Specific Facts

Keep these layers separate:

- **Universal craft rules:** hierarchy, density, typography, contrast, motion
  restraint, focus affordance, responsiveness, and anti-generic taste checks.
  These are portable. Link `anti-slop.md`, `interface-polish.md`, and
  `taste-layer.md` instead of duplicating their lists here.
- **Repo-specific facts:** product intent, brand attributes, tokens,
  typography choices, component grammar, content voice, golden examples, and
  audience-specific density. These must come from live repo evidence, user
  input, or a labeled inference.

`DESIGN.md` is the repo-owned file for those facts. If it exists, it is not
background reading; it is an active contract for visual work. If it is missing
and the repo has recurring or product-facing visual work, create it through
`/design scaffold` rather than letting each agent rediscover the visual system.

A design-system document can organize product facts; it cannot replace rendered
artifact critique. Final judgment still needs a screenshot, URL, rendered
artifact, or an explicit unverified caveat.

## Holistic System Labs

**Expose** every candidate as a reusable system proposition, not a bespoke
application shell. When the repo already owns a canonical gallery or registry,
compose that complete surface into every option; do not replace it with a tiny
hand-picked sampler. The requested primitive is the varying system rule. The
comparison corpus and all other established design facts stay fixed.

Every candidate renders the same review matrix:

- **Foundations:** semantic color, spacing and density, shape and elevation,
  plus light and dark themes.
- **Typography:** display, body, labels, metadata, numerics, and long wrapping
  content.
- **Target anatomy and states:** the primitive's complete anatomy across
  default, hover, focus, current/selected, expanded, disabled, loading, empty,
  error, overflow, and reduced-motion states where applicable.
- **Adjacent components:** buttons, inputs, menus, cards, tables, alerts, and
  tabs using the established grammar.
- **Motion:** enter, exit, expansion, selection, and route transitions, with a
  reduced-motion counterpart.
- **Compositions:** the gallery/docs surface, content/detail, dense work/data,
  and an unfamiliar product-neutral composition at desktop, tablet, and phone.

Use one truthful, product-neutral role and stress corpus across candidates so
the operator compares the system move rather than changing content. Existing
applications may provide secondary stress tests, but their nouns,
destinations, data, and one-off rules must not define the proposition. If the
repo lacks a canonical gallery, build this matrix once as shared comparison
content; lanes contribute propositions, not substitute galleries.

## What Belongs In A Repo Design System

Keep the design system local to the consuming repo. Roster provides the
process and checks; the product owns the visual language.

The reusable system includes:

- **Tokens:** primitive values, semantic aliases, component-level roles, and
  theme values.
- **Typography:** font families, type scale, line heights, numeric formatting,
  and when to use tabular numbers.
- **Spacing and density:** base grid, section rhythm, compact/dense modes, and
  exceptions.
- **Shape and elevation:** radii, shadows, outlines, borders, and stacking
  rules.
- **Component grammar:** approved components, variants, composition patterns,
  empty/loading/error states, and anti-patterns.
- **Motion:** duration bands, easing choices, reduced-motion behavior, and
  interaction affordances.
- **Accessibility:** contrast, focus, target size, labels, landmarks, keyboard
  paths, and screen-reader expectations.

## When A Token Layer Earns Its Cost

Add or enforce a token layer only when at least one of these is true:

- The repo has multiple recurring UI surfaces.
- The same visual decision appears in several components.
- Product identity matters and drift is visible.
- Multiple agents or humans are changing UI in parallel.
- A downstream app needs themes, white-labeling, or brand variants.

Do not add a token layer for a one-off report, static page, prototype, or
single bounded polish pass. Improve the rendered surface directly.

## Audit Questions

- Are raw colors, spacing values, shadows, or font sizes bypassing existing
  tokens?
- Which facts are observed, provided, or inferred?
- Are reference-brand examples marked `do-not-copy` where the repo does not own
  them?
- Do component variants cover loading, empty, error, disabled, active, hover,
  focus, and selected states?
- Are components composed consistently, or are agents inventing local grammar?
- Does the design system describe what to avoid, not only what to use?
- Can a future agent inspect one local file and know the product's visual
  direction?

## Enforcement

Start soft:

1. Route visual diffs through `/design`; accessibility checks ride with the design pass.
2. Capture rendered evidence with `/qa`.
3. Read, create, or update `DESIGN.md` when durable repo-owned design facts are
   present.
4. Harden repeated findings into repo-local lint, tests, or scaffolded design
   guidance.

Escalate to CI only for deterministic checks: token bypass, missing states,
contrast, focus, invalid component imports, or forbidden raw values.
