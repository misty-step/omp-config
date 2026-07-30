# Image-gen providers — full detail

Verified 2026-07-07.
Prices and model IDs move monthly.
Re-check the linked official page before quoting exact numbers to a customer.
Reference environment keys by NAME only.

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

**Access:** Use the Gemini API with `GEMINI_API_KEY` in the environment.
Use the new **Interactions API**:
`POST https://generativelanguage.googleapis.com/v1beta/interactions`, with header
`x-goog-api-key`.
The body carries `model`, `input` (text plus optional base64 image refs), and
`response_format` with `mime_type` and `aspect_ratio` (`1:1`,`16:9`,…).
Use `image_size` (`512px|1K|2K|4K`).
For editing or multi-turn work, add image objects to `input`.
Vertex AI also provides this access.
Google AI Studio free tier: ~500 images/day. Batch API: −50%.

**Pricing (~):** Nano Banana (2.5-flash-image) ~$0.039; Nano Banana 2
~$0.045–0.067 @1K; Nano Banana Pro ~$0.134 @2K, ~$0.24 @4K;
Imagen 4 Fast $0.02 / Standard $0.04 / Ultra $0.06.

**Fit:** Use Gemini first for agent loops.
It is headless, fast (~4s on flash tiers), has the best in-image text, and has a
generous free tier.
Use Pro when a human will review the mockup.
Use flash for diagrams, figures, and informational images.

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

**Access:** Use the OpenAI API with `OPENAI_API_KEY`.
Generate with `POST /v1/images/generations` and
`{model, prompt, size, quality, n}`.
Edit or inpaint with `POST /v1/images/edits` (input image + optional mask).
Use `n` to produce variants and contact sheets.

**Pricing (~):** GPT Image 2 roughly $0.01–0.25/image by quality+size;
mini ~$0.005 low.
Verify prices on the [pricing page](https://developers.openai.com/api/docs/pricing).

**Fit:** GPT Image 2 is a co-leader with Nano Banana Pro for mockups.
It offers native reasoning, a strong inpainting/edit surface, `n` variants,
and precise-brief adherence.
Prefer it for editing/inpainting or tight text control.

## Black Forest Labs — Flux 2

**Models:** `flux.2-pro`, `flux.2-max` (quality ceiling), `flux.2-dev`,
`flux.2-schnell` (open-weight, self-hostable).
These models provide strong photoreal, style/character consistency, and
reference conditioning. Text improved, but they are not text-first models.

**Access:** Use the BFL API (`bfl.ai`, credit-based, 1 credit = $0.01), plus
fal.ai, Replicate, OpenRouter, or Azure AI Foundry.
The access is fully headless.

**Pricing (~):** Flux 2 Max costs input $0.03/megapixel, first output MP $0.07,
and each further MP $0.03. Pro/Dev/Schnell cost less by tier.

**Fit:** Use Flux when you need photoreal or stylized imagery, or open weights.
Use Dev/Schnell for on-prem or no-per-call-cost work.
Do not choose Flux for heavy in-image UI copy.

## Ideogram 3

Ideogram is a typography specialist.
It provides ~90–95% text accuracy versus ~30–50% for most competitors.
Its "Design" style mode targets posters and typography-hero images.
Use the Ideogram API or Recraft Studio. Credit-based pricing is ~$0.08/image.
**Fit:** Choose it when text or typography *is* the subject, such as posters,
wordmarks, or ad headlines.

## Recraft V4

Recraft V4 is the only major model with **native editable SVG / vector output**.
It creates genuine paths, not a raster trace.
It provides brand-style controls and works well for logos, icons, and
delivery-ready design assets.
Its text ceiling is lower than Ideogram.
It is API-accessible with credit-based pricing (~$0.10–0.15).
**Pro pattern:** Use Ideogram for the wordmark and Recraft for the final
editable vector.
**Fit:** Choose it when the deliverable must be editable/vector, not a flat image.

## xAI — Grok / Aurora

**Aurora** is an autoregressive mixture-of-experts image model behind
**Grok Imagine** (image + video).
It uses a REST API with token auth and usage-based pricing.
It also proxies Flux models and requires a paid subscription.
**Fit:** Treat it as niche for design agent loops.
Use OpenAI, Gemini, or Flux first unless X-ecosystem integration is the point.

## Midjourney

Midjourney has an aesthetic ceiling and best-in-class art direction.
Its v8.1 default (2026-06-10) includes native image-to-video.
**No official public developer API** exists as of 2026.
Third-party or unofficial APIs violate ToS and risk bans.
**Fit:** Use it manually for hero art; it is **not agent-fit**.
For comparable quality with official APIs, use GPT Image 2, Nano Banana Pro,
or Flux 2 Pro.

## Anthropic / Claude

**No image-generation model.** Claude cannot produce images.
This was confirmed 2026-07-07.
Route all generation to Gemini or OpenAI.

## Content / secret discipline

- Reference environment keys by NAME (`GEMINI_API_KEY`, `OPENAI_API_KEY`).
  Never print values. Resolve `op://` refs at the point of use.
- Write outputs to a scratch/work dir.
  Do not commit raw model output or raw diffs into a repo tree except allowlisted
  fixture dirs. Redact and allowlist before publishing anything downstream.
