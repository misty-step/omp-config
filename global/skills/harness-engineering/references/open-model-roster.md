---
roster_review_due: 2026-08-05
---

# Open-Model Roster Notes

Last researched: 2026-07-08 (OpenRouter catalog re-pulled; harness notes from
2026-06-19 substrate report unless dated otherwise).

Use this when choosing open-model defaults and variants for OMP peer lanes.
Treat this as a one-day operating snapshot.
Re-check OpenRouter and run live local smokes before each default change.

The substrate positioning came from a 2026-06-19 coding-agent substrate report.
The model catalog rows still depend on the 2026-06-14 OpenRouter snapshot
unless a later live probe is cited.

## Current Defaults

| Lane | Default | Use first when |
|---|---|---|
| OpenCode | `openrouter/moonshotai/kimi-k2.7-code` | Code-centric review, diff analysis, event-stream capture, or future runner-adapter work where session/service shape matters. |
| Pi | `openrouter/moonshotai/kimi-k2.7-code` | Quick open-model peer lanes, model-family variants, and small decorrelated critiques where minimal harness overhead wins. |
| Goose | `openrouter/moonshotai/kimi-k2.7-code` | MCP-heavy workflows that span code plus trackers, docs, browsers, chat, or internal tools. |

Claude, Antigravity, Cursor, and Grok remain useful conditional tools.
They are not the default composition bias for OMP peer lanes when a
smoke-tested open-model lane can answer the same question.
Conditional does not mean static.
Grok Build's default moved to grok-4.5 on 2026-07-08 (Opus-class at `$2/$6`,
with `--best-of-n` and `--check` self-verification).
When a proprietary lane's price/capability crosses into open-model territory,
re-run the comparison instead of citing the old verdict.
Facts: `global/skills/peer-harnesses/references/model-provider-harness-index.md`.

## Local Smoke Evidence

Sentinel objective: `open-model-roster-smoke`, expected output
`HARNESS_OPEN_MODEL_OK`, run through each provider's direct headless surface on
2026-06-14.

| Lane | Receipt | Verdict | Note |
|---|---|---|---|
| Pi | `efd464ab-bed2-465c-9a89-b644822733ae` | succeeded | Passed after adding `--no-extensions`; previous attempt matched output but exited 1 due personal `ops-watchdog` extension. |
| Goose | `4f0b6928-7abc-4080-a0cb-1b195a7dd74a` | succeeded | `goose run --provider openrouter --model moonshotai/kimi-k2.7-code`. |
| OpenCode | `9601cf81-428f-4718-980f-15ee161b7b6e` | succeeded | `opencode run --model openrouter/moonshotai/kimi-k2.7-code --format json`. |

## Model Notes

### Kimi K2.7 Code

`moonshotai/kimi-k2.7-code` is the current open-model dispatch-floor default.
OpenRouter listed it on 2026-07-08 with:

- 262,144 context tokens.
- **16,384 max completion tokens — down from 262,144 in the 2026-06-14
  snapshot.** Verify this before promoting it for long-output lanes (big diffs,
  generated docs).
  This drift alone may justify re-evaluating the default.
- text+image input to text output.
- prompt `$0.74/M`, completion `$3.50/M`, cache read `$0.15/M`.
- supported parameters including tools, tool choice, parallel tool calls,
  structured outputs, reasoning, and reasoning effort.

Quote prices from the catalog/page at dispatch time.
Do not hard-code them into gates.

Sources: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
`moonshotai/kimi-k2.7-code` on 2026-07-08, and
https://openrouter.ai/moonshotai/kimi-k2.7-code.

### Kimi rollback and reasoning variants

- `moonshotai/kimi-k2.6` remains `previous_kimi` for rollback and A/B checks.
- `moonshotai/kimi-k2-thinking` remains `thinking_kimi` when the lead wants
  the Kimi family but a different reasoning surface.

Do not restore K2.6 as default without a fresh OpenRouter catalog check and a
local task smoke.

### DeepSeek

- `deepseek/deepseek-v4-pro` remains `long_context`.
  OpenRouter listed 1,048,576 context tokens, 384,000 max completion tokens,
  tools, structured outputs, and reasoning on 2026-06-14.
- `deepseek/deepseek-v4-flash` is `budget_long_context`.
  It has the same 1M context class, a lower catalog price, and a smaller max
  completion.

Use these through Pi/Goose/OpenCode when long context or cheap large-context
review matters more than Kimi-family continuity.

### MiniMax

`minimax/minimax-m3` is the `alternate_agentic` candidate.
OpenRouter listed it on 2026-06-14 with 1,048,576 context tokens, 512,000 max
completion tokens, text+image+video input, tools, structured outputs, and
reasoning.
Prefer it over stale M2.x defaults unless a smoke shows a regression.

### Qwen

`qwen/qwen3-coder-next` is `qwen_coder`, a coding-family comparator with 262K
context and tool parameters.
The 2026-07-08 catalog confirmed `$0.11/$0.80`.
Use it when you need a non-Kimi, non-DeepSeek coding lane.

### GLM

`z-ai/glm-5.2` (2026-06-16) is a new cheap-1M-context candidate.
It has 1,048,576 context, 128,000 max completion, and `$0.42/M` in /
`$1.32/M` out on 2026-07-08.
It has tools, parallel tool calls, structured outputs, and reasoning effort.
It is a strong bench-diversity family.
It needs a local smoke receipt before any default promotion.

## Harness Notes

### Pi

Pi stays the smallest open-model peer lane.
The receipts above already cover dispatch and model-override behavior for it.
Invoke it with `--no-extensions` so optional personal Pi extensions cannot make
a successful model response exit nonzero.
Pi also supports custom OpenAI-compatible providers/models through
`~/.pi/agent/models.json`.

Source: https://pi.dev/docs/latest/models.

### Goose

Goose is a primary open-model harness candidate for MCP-heavy work.
Official docs list OpenRouter as a supported provider requiring
`OPENROUTER_API_KEY`.
The local CLI exposes:

```sh
goose run --no-session --quiet --provider openrouter --model moonshotai/kimi-k2.7-code --text "task"
```

Source: https://block.github.io/goose/docs/getting-started/providers.

### OpenCode

OpenCode is the preferred open substrate candidate for code-centric review
runner experiments.
OpenRouter's official integration docs say OpenCode supports OpenRouter as a
built-in provider through `/connect`, `/models`, or `opencode.json`.
It accepts OpenRouter model ids through the `openrouter/<model>` form.
The 2026-06-19 substrate report's core distinction is that OpenCode is
session/service-shaped.
That shape fits coordinator/specialist review lanes and structured event
collection better than wrapping terminal-first tools.

Source: https://openrouter.ai/docs/cookbook/coding-agents/opencode-integration.

## Operating Rules

- Prefer OpenCode first for code-review substrate experiments.
  Prefer Goose first for cross-system MCP workflows.
  Prefer Pi first for small, cheap, decorrelated peer critiques.
  The model family may be the same; the harness behavior is not.
- Promote a default only with live OpenRouter catalog evidence, a local binary
  probe, and at least one real local smoke receipt.
  Record the receipt in the table above.
- Keep model facts in
  `global/skills/peer-harnesses/references/model-provider-harness-index.md`.
  Keep role-fit policy here and in shared doctrine.
- Do not add a new provider wrapper when Pi/Goose/OpenCode plus model variants
  cover the failure mode.
- Do not treat any CLI as a production control plane.
  Keep durable queueing, sandboxing, policy, publication credentials,
  budget/circuit breakers, and eval storage outside the per-job agent kernel.
