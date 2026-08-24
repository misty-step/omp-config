---
name: explore-design
description: Generate an interactive visual catalog of no fewer than half a dozen (≥6) distinct, production-grade UI design directions for a component or page.
disable-model-invocation: true
argument-hint: "[component, page, or product surface]"
---

# Explore Design

Explore and compare competing visual and interaction designs for a product
surface. Fan out no fewer than half a dozen ($\ge 6$) radically distinct,
production-grade directions across orthogonal tension axes, compile them into
one interactive HTML showcase sandbox, and present the catalog for operator
selection.

```text
deconstruct -> fan out (≥6 directions) -> build interactive showcase -> browser preview -> handoff
```

## 1. Deconstruct the surface and data

Inspect the product surface, user role, and functional jobs. Identify:

- the primary user actions and secondary utility actions;
- the core data entities, attributes, numbers, states, and relations;
- information density requirements (compact data vs reading rhythm);
- interactive moments (forms, selection, filters, hover states, drills).

Do not settle on a single layout yet. Deconstruct the raw functional components
so each design scout can assemble them under a distinct visual thesis.

Completion criterion: Core actions, data entities, states, and functional
components are enumerated.

## 2. Formulate $\ge 6$ orthogonal design theses

Generate no fewer than six ($\ge 6$) genuinely distinct design theses across
three fundamental tension axes:

1. **Spatial & Information Density:** Compact tabular vs expansive negative space.
2. **Materiality & Texture:** Structural hairline borders vs tactile frosted glass vs stark monochrome.
3. **Typography & Hierarchy:** High-contrast editorial serifs vs pure monospace telemetry vs geometric grotesque.

Each direction must represent a distinct design archetype. Example baseline set:

- **Direction 1: Swiss Modernist / Editorial Print**
  - *Type:* High-contrast display serif (Fraunces / Instrument Serif) + crisp geometric sans body.
  - *Layout:* Asymmetric grid, strong typographic hierarchy, hairline rule dividers.
  - *Palette:* Warm paper / alabaster base, deep carbon text, single vibrant vermilion spot accent.
- **Direction 2: Cyber-Industrial / Technical Terminal**
  - *Type:* Strict monospace hierarchy (JetBrains Mono / Berkeley Mono).
  - *Layout:* Structural borders, bordered data tables, telemetry cards, status indicators.
  - *Palette:* Deep obsidian, high-contrast dark gray borders, amber/cyan phosphor accents.
- **Direction 3: Tactile Neu-Material / Glassmorphic Elegance**
  - *Type:* Modern clean sans (Geist / Satoshi) with refined tracking.
  - *Layout:* Floating layered surfaces, subtle directional lighting, rounded pill controls.
  - *Palette:* Charcoal/slate base with frosted translucent panels, subtle border highlights.
- **Direction 4: Neo-Brutalist / High-Impact Pop**
  - *Type:* Bold heavy grotesque (Clash Display / Syne / Archivo).
  - *Layout:* Solid 2px dark borders, hard offset drop shadows (0px blur), high contrast.
  - *Palette:* High-contrast monochrome background with vibrant block color fills.
- **Direction 5: Minimalist Zen / Quiet Luxury**
  - *Type:* Understated humanist sans (Inter Tight / Neue Montreal).
  - *Layout:* Extreme negative space discipline, subtle borderless sectioning, micro-labels.
  - *Palette:* Muted warm stone, soft taupe, dark charcoal text (never harsh pure black).
- **Direction 6: Data-Dense Executive Dashboard**
  - *Type:* Compact tabular numerals, tight tracking, clear micro-labels.
  - *Layout:* Split-pane navigation, dense multi-column layout, inline micro-sparklines.
  - *Palette:* High-contrast utility palette where color is reserved strictly for status data.

Additional directions may be added when justified by the brief or domain.

Completion criterion: $\ge 6$ orthogonal, non-overlapping design theses are
formulated with explicit typography, color, and layout rules.

## 3. Parallel dispatch

Dispatch parallel designer subagents (or parallel generation passes). Assign
each scout exactly one design thesis and the deconstructed data model.

Each scout must produce a complete, self-contained implementation with:

- valid semantic HTML, scoped CSS variables, and interactive vanilla JS;
- real, realistic sample data (no "Lorem Ipsum" or placeholder text);
- working interactive states: hover, active, focus, tab switching, form input;
- responsive layout styling.

Completion criterion: All $\ge 6$ design directions return complete, working
markup and styles.

## 4. Compile the interactive showcase sandbox

Assemble all directions into a single, standalone HTML artifact written to the
OS temporary directory (`/tmp/design-showcase-<surface>.html`) or `local://`:

1. **Sticky Top Control Bar:**
   - Direction switcher buttons labeled `1` through `N` with direction titles.
   - Hotkey support: pressing keys `1` through `9` on the keyboard switches directions instantly.
   - Viewport preview toggle: Desktop (100%), Tablet (768px), Mobile (375px) iframe/container.
   - Design Tokens Drawer: Displays the active direction's CSS variables, color swatches, and font imports.
2. **Embedded Viewport:** Renders the active direction cleanly without CSS style leaking between directions.

Open the compiled showcase in the browser or report the exact file path for
operator review.

Completion criterion: A single interactive HTML showcase exists containing all
$\ge 6$ fully functional directions with a working hotkey switcher.

## 5. Selection and handoff

Present a summary table comparing the directions:

| # | Direction Name | Spatial Density | Aesthetic Vibe | Key Tradeoff |
|---|---|---|---|---|
| 1 | Swiss Modernist | Balanced | Editorial, literary | High font personality |
| 2 | Cyber-Industrial| Dense | Terminal, utility | Monospace body |
| ... | ... | ... | ... | ... |

Once the operator selects a direction:

- Export its CSS design tokens, typography imports, and component markup.
- Hand off directly to `/frontend-design` for production polish, or `/deliver` for full slice implementation.

Completion criterion: All $\ge 6$ directions are viewable; selection path and
design tokens are ready for production handoff.
