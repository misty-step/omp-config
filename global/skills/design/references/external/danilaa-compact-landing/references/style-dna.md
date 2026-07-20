# Compact Landing Style DNA

Use this reference after choosing a direction. It defines a design space, not a template.

## Contents

- Invariants
- Direction families
- Variable axes
- Product-native artifacts
- Motion without layout shift
- Coherence checks

## Invariants

Compact means edited, focused, and immediately understandable. It does not require one fixed width or visual style.

Keep:

- one clear job for the page;
- one primary action visible early;
- restrained content depth;
- small, deliberate hierarchy;
- real product content or behavior;
- coherent repeated tokens;
- responsive, accessible, zero-shift interaction.

Vary everything else.

## Direction Families

Use these as starting bundles. Mutate at least two details so a family never becomes another frozen template.

### Field Note

- Silhouette: narrow editorial column with marginal marks or annotations.
- Measure: `420-520px`.
- Palette: warm paper, ink, one mineral or botanical accent.
- Type: editorial serif + restrained sans or mono.
- Geometry: sharp to `8px`.
- Surface: whitespace, paper rules, occasional inset hairline.
- Motif: stamp, handwritten mark, single emoji, tiny index.
- Motion: quiet fade, clipped underline, annotation float.

### Lab Instrument

- Silhouette: stacked live readout with controls attached to one product artifact.
- Measure: `440-560px`.
- Palette: cool fog or warm neutral with semantic data colors.
- Type: humanist/grotesk sans + mono.
- Geometry: `6-12px`, with true circular knobs or dots.
- Surface: inset hairlines or subtle rings.
- Motif: readouts, scales, colored state marks.
- Motion: trace/draw, press compression, state morph.

### Pocket Console

- Silhouette: framed command surface, logs, short instructions, one action rail.
- Measure: `480-620px`.
- Palette: charcoal, bone text, one terminal-like accent that is not default neon green.
- Type: purposeful all-mono or condensed sans + mono.
- Geometry: `0-6px`.
- Surface: flat dividers, technical frames, restrained inset depth.
- Motif: ASCII mark, cursor, line number, small status glyph.
- Motion: cursor/slot swap, scan reveal, subtle state wash.

### Playful Shelf

- Silhouette: compact catalogue of tangible choices around one main action.
- Measure: `500-640px`.
- Palette: lightly tinted canvas with one anchor and up to three semantic candy accents.
- Type: rounded or humanist sans + mono.
- Geometry: `12-22px`, using concentric nested radii.
- Surface: tinted panels or soft rings; avoid boxing every item.
- Motif: `1-3` emoji, doodles, object icons, or colored punctuation.
- Motion: ambient float, soft pop, state color change.

### Split Pamphlet

- Silhouette: compact two-zone editorial spread that collapses cleanly on mobile.
- Measure: `600-720px`.
- Palette: editorial white, ink, one deep brand color.
- Type: serif + sans, grotesk + condensed, or humanist sans + mono.
- Geometry: mixed sharp/soft with an explicit rule.
- Surface: whitespace, paper rules, one framed specimen.
- Motif: large initial, stamp, index, cropped product visual.
- Motion: opposing short slides, clipped reveal, image scale within a fixed frame.

### Compact Catalogue

- Silhouette: indexed rows, specimens, or products with an offset detail pane.
- Measure: `560-720px`.
- Palette: monochrome ink or product-tinted neutral with one anchor accent.
- Type: condensed + sans, grotesk + mono, or all-sans with numeric contrast.
- Geometry: `0-4px` or deliberate mixed radii.
- Surface: dividers and negative space; elevation only for selected detail.
- Motif: indices, swatches, tiny thumbnails, measurement marks.
- Motion: selection slide, crossfade in fixed pane, restrained row hover.

## Variable Axes

### Composition

Choose a first-screen silhouette before components:

- centered stack;
- offset rail with empty space on one side;
- split text/artifact;
- framed object floating in the canvas;
- catalogue with selected detail;
- stepped or staggered specimens;
- title wrapped around a compact product artifact.

On screens below `768px`, reduce complex compositions to one intentional column. Preserve reading order in the DOM.

### Measure and Density

- Narrow: `420-500px`.
- Comfortable: `500-600px`.
- Wide compact: `600-720px`, usually split or offset.
- Body: `13-16px`.
- Section gap: `22-44px`.
- Component gap: `4-16px`.

Use a wide compact canvas only when its second zone carries real content. Empty width is not variety.

### Palette

Build a role-based palette:

```css
--canvas: /* page */;
--surface: /* raised or grouped content */;
--ink: /* primary text */;
--muted: /* secondary text */;
--line: /* separators */;
--accent: /* primary identity/action */;
--signal: /* optional semantic state */;
```

Good families:

- warm paper: cream, brown-black, terracotta or honey;
- cool fog: blue-gray, charcoal, cobalt or pine;
- monochrome ink: bone/white, near-black, one saturated anchor;
- dark charcoal: off-black, smoke, warm white, muted bright accent;
- product-tinted: a very light/dark version of the actual brand hue;
- playful light: quiet base with one anchor plus tiny semantic accents.

Do not choose accents randomly per component. A rainbow is justified only when colors encode real categories or states.

### Typography

Choose for product character, then use the current project's fonts when close enough.

- Grotesk + mono: precise tools and utilities.
- Humanist sans + mono: approachable technical products.
- Editorial serif + sans: cultural, written, archival, or crafted products.
- Rounded sans + mono: playful consumer tools.
- Condensed + sans: catalogues, media, inventory, or dense labels.
- All-mono: genuine terminal or instrument concepts only.

Use `text-wrap: balance` for short headings and `text-wrap: pretty` for prose. Keep headline scale proportional to the compact canvas; hierarchy need not mean giant type.

### Radius

- Sharp: `0-2px`.
- Machined: `4-7px`.
- Balanced: `8-12px`.
- Friendly: `14-18px`.
- Soft: `20-24px`.
- Mixed: one family for structural frames and another for interactive objects.

Nested surfaces should be concentric: outer radius roughly equals inner radius plus padding. Use `9999px` only for true pills, dots, switches, or strongly intentional capsule controls.

### Surface Grammar

Pick one dominant treatment:

- whitespace and alignment;
- flat rules/dividers;
- inset hairlines;
- layered shadow rings;
- softly tinted panels;
- dashed technical frames;
- paper lines or print texture.

Do not mix every treatment. Cards exist to communicate grouping or elevation, not to fill a grid.

### Motifs

Choose zero or one motif family:

- `1-3` native emoji tied to product meaning;
- ASCII punctuation or terminal marks;
- numeric indices or coordinates;
- stamps or editorial annotations;
- simple CSS doodles or geometric marks;
- existing project icons;
- tiny product screenshots or object crops.

Reserve fixed boxes for emoji and icons. Do not embed SVG examples in generated skill documentation. In an actual project, reuse its icon system when available.

## Product-Native Artifacts

Start with the product action and make it visible.

- Audio: playable palette, waveform, mixer, or listening comparison.
- Animation library: real text/component demo with stable dimensions.
- CLI: executable-looking command, output specimen, or option toggles.
- Data tool: one honest transformation from input to output.
- Design package: token specimen, component states, or before/after control.
- Documentation tool: search, outline, rendered snippet, or copy action.
- Consumer product: miniature choice, collection, schedule, or status flow.

Prefer one convincing artifact over three generic feature cards. Decoration may echo its metaphor but must not replace it.

## Motion Without Layout Shift

Choose one entrance pattern:

- fade only;
- `translateY(4-8px)` + fade;
- short opposing `translateX` in split layouts;
- blur-to-sharp with opacity;
- clipped reveal inside a box whose dimensions already exist.

Choose up to two interaction patterns:

- press compression (`scale(0.96)`; `0.98` for wide controls);
- icon/label morph inside an overlaid fixed slot;
- trace or line draw inside a fixed SVG/canvas frame;
- state color wash;
- selection indicator moving by transform;
- ambient float of absolute decoration;
- fixed-pane crossfade.

Required safeguards:

```css
/* state variants occupy one stable box */
.state-slot { display: grid; }
.state-slot > * { grid-area: 1 / 1; }

/* reserve external media before it loads */
.media { aspect-ratio: 4 / 3; overflow: hidden; }

/* changing values do not alter character widths */
.number { font-variant-numeric: tabular-nums; }
```

- Animate only `transform`, `opacity`, and `filter`.
- Never animate layout properties or use `transition: all`.
- Keep hover font weight, padding, and border width unchanged.
- Extend small controls to a `40px` hit target with wrappers or pseudo-elements; avoid overlapping targets.
- Use fixed/min heights for tabs, previews, code panes, and asynchronously populated regions.
- Use metric-compatible font fallbacks or font metric overrides to reduce font-swap shift.
- Disable nonessential animation under `prefers-reduced-motion: reduce`.

## Coherence Checks

- Can the art direction be described in one sentence without listing components?
- Does the first viewport look different in silhouette from the last compact page?
- Do palette, type, radius, surface, motif, and motion express the same product character?
- Is color functional or meaningfully decorative rather than scattered?
- Is the signature artifact real enough to teach or prove something?
- Does dynamic UI keep the same geometry before, during, and after interaction?
- Did the page use fewer components than the first draft could have used?
