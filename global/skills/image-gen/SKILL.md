---
disable-model-invocation: true
name: image-gen
description: >
  Generate images for UI/UX mockups and redesign concepts, labeled diagrams and
  system maps, design contact sheets, doc figures, and on-brand images with
  legible in-image text. Call the provider API directly; no wrapper scripts.
  Use when: "mock up this UI", "redesign concept", "show me design variations",
  "generate an image/diagram/figure", "vibe design", "wireframe to visual",
  "make a contact sheet", or "art for this doc/poster/status". Reach for it
  during DESIGN work, not just illustration. Trigger: /image-gen.
argument-hint: "[mockup|diagram|contact-sheet|figure] <subject and intent>"
---

# image-gen

Image generation is a standing model-native affordance.
Do not request or gate it behind one harness's native tool.
In 2026, frontier models (Google **Nano Banana Pro**, OpenAI **GPT Image 2**)
render legible, accurate in-image text and reason about spatial layout.
Practitioners can now produce real **UI/UX mockups and redesign concepts** with
these models. Reach for image gen during **design work**, not only for
informational figures.

`GEMINI_API_KEY` and `OPENAI_API_KEY` are in the environment.
Use the names only; never print values.
Call the provider API directly. Do not build or maintain a wrapper script.
Anthropic/Claude cannot generate images. Route generation to Gemini or OpenAI.

## Decide first: image or not?

Generate an image when the deliverable is **visual information or a design
concept** that a human will view.
Examples include a mockup for design review, a labeled system map, a redesign
direction, a contact sheet of variants, a poster/status, or a doc figure.

Do **not** generate an image for a **production interface or anything code-bound**.
Raster mockups are non-responsive, show one viewport, fail accessibility,
provide no component architecture, and hide loading/error/empty states.
Visual output reads ~80% done while the buildable reality is ~20%.
For these targets, build an **HTML/CSS prototype** (house "think in HTML"
doctrine and the `design`/`impeccable` skills) or a Figma/wireframe.
These options render real fonts, data, and breakpoints, and remain editable.
Image gen supports early design work, such as ideation, exploration, and
stakeholder buy-in. It is not the shipped UI.
Keep routine plans and simple status reports text-first.

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

Costs per image (~2026): Imagen 4 Fast **$0.02** ·
GPT Image mini ~**$0.005–0.01** low · Nano Banana 2 ~**$0.045–0.067** @1K ·
GPT Image 2 ~**$0.01–0.25** by quality/size · Nano Banana Pro ~**$0.134** @2K /
**$0.24** @4K · Flux 2 Max ~**$0.07** first MP.
Gemini free tier: ~500 img/day via AI Studio; Batch API −50%.
Verify live before quoting exact numbers.
Read `references/providers.md` for full per-provider detail.

## Mockup prompting playbook

Use this prompt sequence for UI mockups and redesigns:

1. **Order the prompt and line-break the sections:** `scene/context → subject →
   key details (layout, hierarchy, spacing) → intended artifact → constraints`.
   Name the artifact ("UI mockup", "infographic", "ad") to set the model's mode
   and polish.
2. **Describe the product as if it already ships.** Use real interface elements,
   not concept-art language: *"Settings screen for a macOS menu-bar app; left nav
   rail, 5 items; main panel is a toggle list with section headers"* beats
   *"a beautiful modern app."*
3. **Put literal copy in quotes or ALL CAPS.** Specify typography (family, size,
   weight, color, placement). Spell brand and tricky words letter-by-letter.
   Use `quality="high"` for dense text/infographics.
4. **Edit = Change + Preserve + Physical Realism.** State the change.
   List what stays identical.
   **Re-specify the Preserve list every iteration** or the design drifts.
   Pass the prior image and a style reference as input images to keep the design
   system continuous.
5. **Make variants:** Use `n` (OpenAI) or several calls (Gemini), then make a
   contact sheet for review.
   **Iterate:** Generate, hand the result to a fresh critic (human or different
   model), and feed the diff back as a Change/Preserve edit.

## Calling it from an agent (headless)

Call both providers with plain REST.
Read key names from the environment and never print them.
**Gemini (default for speed/cost, and Nano Banana Pro for mockups)** — Use the
Interactions API, `POST https://generativelanguage.googleapis.com/v1beta/interactions`,
with header `x-goog-api-key: $GEMINI_API_KEY`.
Use this body: `{"model":"gemini-3-pro-image",
"input":[{"type":"text","text":"<prompt>"}, {optional image refs}],
"response_format":{"type":"image","mime_type":"image/jpeg","aspect_ratio":"16:9",
"image_size":"2K"}}`.
Set `mime_type` to `image/jpeg`; png is rejected.
Use sizes `"512"|"1K"|"2K"|"4K"`.
This list was verified live 2026-07-07. A wrong value returns 400 with the
supported list, so errors self-correct.
Edit or continue by adding
`{"type":"image","mime_type":...,"data":"<base64>"}` items to `input`.

**OpenAI (GPT Image 2 for mockups/text/inpainting)** —
Use `POST https://api.openai.com/v1/images/generations`, `Authorization: Bearer
$OPENAI_API_KEY`, and this body:
`{"model":"gpt-image-2","prompt":"<prompt>",
"size":"1536x1024","quality":"high","n":1}`.
Use `/v1/images/edits` for edits or inpainting with an input image (+ mask).
Do not build on `gpt-image-1`; it retires 2026-10-23.

Save outputs under a scratch/work dir.
Never commit raw model output into a repo tree except allowlisted fixture dirs.
See `references/providers.md` for Flux, Ideogram, Recraft, xAI, Midjourney
access paths and full pricing.
