---
disable-model-invocation: true
name: image-gen
description: >
  Generate informational images and design concepts. Route production interfaces
  and code-bound work to HTML/CSS. Use for mockups, diagrams, figures, contact
  sheets, and on-brand visuals. Trigger: /image-gen.
argument-hint: "[mockup|diagram|contact-sheet|figure] <subject and intent>"
---

# image-gen

## Route first

Generate an image when the deliverable is visual information or a design concept.
Use it for mockups, labeled diagrams, redesign directions, contact sheets, posters, and document figures.

Build an HTML/CSS prototype or Figma wireframe for a production interface or code-bound deliverable.
Raster mockups show one viewport, fail accessibility, and hide component states.
Keep routine plans and simple status reports text-first.
Anthropic and Claude cannot generate images; route generation to Gemini or OpenAI.

## Invoke

Call the provider API through the Mint broker. Do not build or maintain a wrapper script.

```bash
curl -sS -X POST \
  'http://mint.tail5f5eb4.ts.net:4949/proxy/https/generativelanguage.googleapis.com/v1beta/interactions' \
  -H "x-goog-api-key: __mint.gemini.default__" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemini-3.1-flash-image","input":[{"type":"text","text":"PROMPT"}],"response_format":{"type":"image","mime_type":"image/jpeg","aspect_ratio":"16:9","image_size":"2K"}}' \
  > "$TMPDIR/image-response.json"
```

## Credentials

Use `__mint.gemini.default__` for Gemini or `__mint.openai.default__` for OpenAI in the provider credential field.
Tailnet WhoIs identifies the caller. Mint policy owns authorization. Never print or store resolved credential values.
Save outputs under a scratch or work directory.

## Provider authority

Read `global/references/image-generation.md` for current request shapes, image inputs, output handling, and safety rules.
