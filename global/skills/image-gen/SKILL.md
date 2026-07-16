---
name: image-gen
description: >
  Generate images from an agent loop — UI/UX mockups and redesign concepts,
  labeled diagrams and system maps, design contact sheets, doc figures, and
  on-brand informational images with legible in-image text. Model-native
  primitive: call the provider API directly, no wrapper scripts. Use when:
  "mock up this UI", "redesign concept", "show me design variations", "generate
  an image/diagram/figure", "vibe design", "wireframe to visual", "make a
  contact sheet", "art for this doc/poster/status". Reach for it during DESIGN
  work, not just illustration. Trigger: /image-gen.
argument-hint: "[mockup|diagram|contact-sheet|figure] <subject and intent>"
---

# image-gen

Image generation is a standing model-native affordance, not a capability to
request or gate behind one harness's native tool. Two things changed the calculus
in 2026: frontier models (Google **Nano Banana Pro**, OpenAI **GPT Image 2**) now
render legible, accurate in-image text and reason about spatial layout — good
enough that practitioners produce real **UI/UX mockups and redesign concepts** with
them. Reach for image gen during **design work**, not only for informational
figures.

`GEMINI_API_KEY` and `OPENAI_API_KEY` are already in the env (names only — never
print values). Call the provider API directly; do not build or maintain a wrapper
script. Anthropic/Claude cannot generate images — route to Gemini or OpenAI.

## Decide first: image or not?

Generate an image when the deliverable is **visual information or a design
concept** a human will look at: a mockup for design review, a labeled system map,
a redesign direction, a contact sheet of variants, a poster/status, a doc figure.

Do **not** generate an image when the target is a **production interface or
anything code-bound**. Raster mockups are non-responsive, expose one viewport,
fail accessibility, carry no component architecture, and hide loading/error/empty
states — visual output reads ~80% done while the buildable reality is ~20%. For
those, build an **HTML/CSS prototype** (house "think in HTML" doctrine, and the
`design`/`impeccable` skills) or a Figma/wireframe — they render real fonts, real
data, real breakpoints, and are editable. Image gen accelerates the **front** of
the design funnel (ideation, exploration, stakeholder buy-in); it is not the
shipped UI. Routine plans and simple status reports stay text-first.

## Model decision table

| Job | Reach for | Why |
|---|---|---|
| **UI/UX mockup, redesign concept** (legible copy, real layout) | **Nano Banana Pro** (`gemini-3-pro-image`) or **GPT Image 2** (`gpt-image-2`) | ~99% text accuracy, spatial layout, 4K, reasons before drawing |
| **Fast cheap on-brand image / diagram / labeled map** | **Nano Banana 2 / 2 Lite** (`gemini-3.1-flash-image` / `-lite-image`) | ~4s, ~$0.03–0.07, in-image text — the house default |
| **Photoreal / cinematic / style + character control** | **Flux 2 Pro/Max**, or **Imagen 4** | photoreal ceiling; Flux Dev/Schnell are open-weight |
| **Typography-hero poster, text is the subject** | **Ideogram 3** | tuned "Design" style, ~90–95% text |
| **Editable SVG / vector — logo, icon, design asset** | **Recraft V4** | only major model with native editable vector output |
| **Variant contact sheet** | GPT Image 2 (`n` param) or several Nano Banana calls | multiple directions on one board |
| Aesthetic ceiling, art direction | Midjourney (v8.1) | **no official API — not agent-fit**; use manually |

Costs (per image, ~2026, verify live before quoting): Imagen 4 Fast **$0.02** ·
GPT Image mini ~**$0.005–0.01** low · Nano Banana 2 ~**$0.045–0.067** @1K ·
GPT Image 2 ~**$0.01–0.25** by quality/size · Nano Banana Pro ~**$0.134** @2K /
**$0.24** @4K · Flux 2 Max ~**$0.07** first MP. Gemini free tier: ~500 img/day via
AI Studio; Batch API −50%. Full per-provider detail: `references/providers.md`.

## Mockup prompting playbook

The operator's emphasis — how to actually prompt for UI mockups/redesigns:

1. **Order the prompt, line-break the sections:** `scene/context → subject →
   key details (layout, hierarchy, spacing) → intended artifact → constraints`.
   Name the artifact ("UI mockup", "infographic", "ad") — it sets the model's mode
   and polish.
2. **Describe the product as if it already ships.** Real interface elements, not
   concept-art language: *"Settings screen for a macOS menu-bar app; left nav rail,
   5 items; main panel is a toggle list with section headers"* beats *"a beautiful
   modern app."*
3. **Literal copy in quotes or ALL CAPS**; specify typography (family, size,
   weight, color, placement); spell brand/tricky words letter-by-letter. Use
   `quality="high"` for dense text/infographics.
4. **Edit = Change + Preserve + Physical Realism.** State the change, list what
   stays identical, and **re-specify the Preserve list every iteration** or it
   drifts. Pass the prior image + a style reference as input images to keep the
   design system continuous.
5. **Variants:** `n` (OpenAI) or several calls (Gemini) → a contact sheet for
   review. **Iterate:** generate → hand to a fresh critic (human or a different
   model) → feed the diff back as a Change/Preserve edit.

## Calling it from an agent (headless)

Both are plain REST; keys by name from env, never printed.

**Gemini (default for speed/cost, and Nano Banana Pro for mockups)** — Interactions
API, `POST https://generativelanguage.googleapis.com/v1beta/interactions`, header
`x-goog-api-key: $GEMINI_API_KEY`. Body: `{"model":"gemini-3-pro-image",
"input":[{"type":"text","text":"<prompt>"}, {optional image refs}],
"response_format":{"type":"image","mime_type":"image/jpeg","aspect_ratio":"16:9",
"image_size":"2K"}}`. `mime_type` must be `image/jpeg` (png is rejected); sizes are
`"512"|"1K"|"2K"|"4K"` (verified live 2026-07-07: a wrong value 400s with the
supported list, so errors self-correct). Edit/continue by adding
`{"type":"image","mime_type":...,"data":"<base64>"}` items to `input`.

**OpenAI (GPT Image 2 for mockups/text/inpainting)** —
`POST https://api.openai.com/v1/images/generations`, `Authorization: Bearer
$OPENAI_API_KEY`, body `{"model":"gpt-image-2","prompt":"<prompt>",
"size":"1536x1024","quality":"high","n":1}`. Edits/inpainting via
`/v1/images/edits` with an input image (+ mask). Deprecating: `gpt-image-1`
(retires 2026-10-23) — don't build on it.

Save outputs under a scratch/work dir, never commit raw model output into a repo
tree except allowlisted fixture dirs. See `references/providers.md` for Flux,
Ideogram, Recraft, xAI, Midjourney access paths and full pricing.
