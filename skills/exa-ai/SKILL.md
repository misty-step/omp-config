---
name: exa-ai
description: Research current external facts and technical sources. Use for discovery, comparison, or corroboration.
---

# Exa AI

Use `web_search` for discovery. Use `read` for a known URL.

- Start with five results; use at most ten unless coverage is missing.
- Apply recency only when the claim has a real freshness boundary.
- Prefer primary sources. Corroborate consequential claims.
- Fetch full text only for missing context, conflicts, or exact wording.
- Report source URLs, publication dates when available, and coverage gaps.

Use `omp search --provider exa` only to diagnose the provider. Do not use the
retired `exa-ai` CLI.
