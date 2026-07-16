# Image-gen providers — full detail

Verified 2026-07-07. Prices/model IDs move monthly — re-check the linked official
page before quoting exact numbers to a customer. Env keys referenced by NAME only.

## Google — Gemini image models (default stack)

**Models (current IDs):**
- **Nano Banana Pro** — `gemini-3-pro-image` (Gemini 3 Pro Image). Studio-quality,
  ~99% text accuracy, spatial-layout understanding, 4K, multilingual text, a
  "deep thinking" step before drawing. **Best-in-class for UI mockups** — Google's
  own Antigravity agent uses it to generate UI mockups for review before coding.
- **Nano Banana 2** — `gemini-3.1-flash-image`. Fast, cheap, strong in-image text.
- **Nano Banana 2 Lite** — `gemini-3.1-flash-lite-image`. 1K only; cheapest/fastest.
- **Nano Banana (legacy)** — `gemini-2.5-flash-image`.
- **Imagen 4** — dedicated text-to-image, tiers Fast/Standard/Ultra; photoreal.

**Access:** Gemini API, `GEMINI_API_KEY` in env. New **Interactions API**:
`POST https://generativelanguage.googleapis.com/v1beta/interactions`, header
`x-goog-api-key`. Body carries `model`, `input` (text + optional base64 image
refs), `response_format` with `mime_type`, `aspect_ratio` (`1:1`,`16:9`,…),
`image_size` (`512px|1K|2K|4K`). Editing/multi-turn: add image objects to `input`.
Also on Vertex AI. Google AI Studio free tier ~500 images/day; Batch API −50%.

**Pricing (~):** Nano Banana (2.5-flash-image) ~$0.039; Nano Banana 2 ~$0.045–0.067
@1K; Nano Banana Pro ~$0.134 @2K, ~$0.24 @4K; Imagen 4 Fast $0.02 / Standard $0.04
/ Ultra $0.06.

**Fit:** first choice for agent loops — headless, fast (~4s on flash tiers), best
in-image text, generous free tier. Pro tier when a human will design-review the
mockup; flash tier for diagrams/figures/informational images.

## OpenAI — GPT Image

**Models:**
- **GPT Image 2** — `gpt-image-2`. Released 2026-04-21, GPT-5.4 backbone, native
  reasoning ("thinking"), near-perfect text rendering, up to 4K
  (3840×2160 experimental >2560×1440). Recommended default; strong at UI mockups,
  infographics, editing/inpainting, reference-image conditioning. `quality` =
  `low|medium|high`.
- **GPT Image 1.5** — `gpt-image-1.5`. Prior gen (2025-12-16), back-compat.
- **GPT Image 1-mini** — `gpt-image-1-mini`. Cost-optimized (~$0.005 low @1024).
- **GPT Image 1** — `gpt-image-1`. **Deprecating 2026-10-23** — do not build new.

**Access:** OpenAI API, `OPENAI_API_KEY`. Generate:
`POST /v1/images/generations` `{model, prompt, size, quality, n}`. Edit/inpaint:
`POST /v1/images/edits` (input image + optional mask). `n` yields variants →
contact sheets.

**Pricing (~):** GPT Image 2 roughly $0.01–0.25/image by quality+size; mini ~$0.005
low. Verify on the [pricing page](https://developers.openai.com/api/docs/pricing).

**Fit:** co-leader with Nano Banana Pro for mockups. Advantages: native reasoning,
strong inpainting/edit surface, `n` variants, precise-brief adherence. Prefer it
when you need editing/inpainting or tight text control.

## Black Forest Labs — Flux 2

**Models:** `flux.2-pro`, `flux.2-max` (quality ceiling), `flux.2-dev`,
`flux.2-schnell` (open-weight, self-hostable). Strong photoreal, style/character
consistency, reference conditioning. Text improved but not a text-first model.

**Access:** BFL API (`bfl.ai`, credit-based, 1 credit = $0.01), plus fal.ai,
Replicate, OpenRouter, Azure AI Foundry. Fully headless.

**Pricing (~):** Flux 2 Max: input $0.03/megapixel, first output MP $0.07, each
further MP $0.03. Pro/Dev/Schnell cheaper down the tiers.

**Fit:** best when you need photoreal/stylized imagery or open weights (Dev/Schnell
for on-prem/no-per-call-cost). Not the pick for heavy in-image UI copy.

## Ideogram 3

Typography specialist. ~90–95% text accuracy vs ~30–50% for most competitors; a
"Design" style mode tuned for posters and typography-hero images. Available via
Ideogram API and inside Recraft Studio. Credit-based (~$0.08/image). **Fit:** the
pick when text/typography *is* the subject (posters, wordmarks, ad headlines).

## Recraft V4

The only major model with **native editable SVG / vector output** — genuine paths,
not a raster trace. Brand-style controls, strong for logos, icons, and delivery-
ready design assets. Text ceiling lower than Ideogram. API-accessible, credit-based
(~$0.10–0.15). **Pro pattern:** Ideogram for the wordmark, Recraft for the final
editable vector. **Fit:** when the deliverable must be editable/vector, not a flat
image.

## xAI — Grok / Aurora

**Aurora** — autoregressive mixture-of-experts image model behind **Grok Imagine**
(image + video). REST API with token auth and usage-based pricing; also proxies
Flux models. Requires a paid subscription. **Fit:** niche for design agent loops —
reach for OpenAI/Gemini/Flux first unless X-ecosystem integration is the point.

## Midjourney

Aesthetic ceiling, best-in-class art direction; v8.1 default (2026-06-10) with
native image-to-video. **No official public developer API** as of 2026 —
third-party/unofficial APIs violate ToS and risk bans. **Fit:** manual/human use
for hero art; **not agent-fit**. For comparable quality with official APIs use
GPT Image 2, Nano Banana Pro, or Flux 2 Pro.

## Anthropic / Claude

**No image-generation model.** Claude cannot produce images. Confirmed 2026-07-07.
Route all generation to Gemini or OpenAI.

## Content / secret discipline

- Reference env keys by NAME (`GEMINI_API_KEY`, `OPENAI_API_KEY`) — never print
  values; resolve `op://` refs at point of use.
- Write outputs to a scratch/work dir. Do not commit raw model output or raw diffs
  into a repo tree except allowlisted fixture dirs; redact/allowlist before
  publishing anything downstream.
