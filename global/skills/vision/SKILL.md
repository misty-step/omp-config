---
disable-model-invocation: true
name: vision
description: |
  Compatibility trigger for product north-star work. Loads /groom vision mode.
  Prefer /groom. Trigger: /vision, /north-star.
argument-hint: "[create|update|refresh|audit] [context]"
---

# /vision

Compatibility entry only.

1. Load `'/home/phaedrus/.omp/agent/skills/groom'`.
2. Run **vision** mode: create or refresh root `VISION.md` and wire consumers.
3. Do not keep a separate vision procedure here.
