---
name: exa-ai
description: Search and fetch technical sources through Exa AI.
disable-model-invocation: false
---

# Exa AI

Use Exa for current-source discovery, technical-source ranking, highlights, and
known-URL text retrieval. Use a direct known-URL reader when Exa ranking adds no
value.

## Authentication and command

The `exa-ai` CLI uses the Mint credential broker with a value-free Exa marker.
Raw Exa credentials never enter the agent process or command environment.

```bash
exa-ai search "<query>" --num 5 --highlights
exa-ai fetch "<url>" --chars 2000
```

Use `--json` only when structured processing is needed. Use `--since <date>`
only for a real freshness constraint. Search types are `instant`, `fast`,
`auto`, `deep-lite`, `deep`, and `deep-reasoning`; default to `auto`.

## Bounds and evidence

- Start with 5 results; normally stay within 5-10.
- Prefer highlights in agent loops; fetch full text only for sources selected for use.
- Prefer primary sources and corroborate consequential claims independently.
- Report the query, accepted source URLs, publication dates when available, and unresolved coverage gaps.
