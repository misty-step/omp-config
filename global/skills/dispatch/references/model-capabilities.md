# Native model and reasoning policy

This reference owns agent-model fit.
It does not own model facts.
Read `skill://harness-engineering/references/model-provider-harness-index.md` for
dated availability, price, context, and harness evidence.

## Agent ladders

OMP 17.2.3 reads each named agent's ordered model list.
The first route is the normal route.
Later routes provide availability resilience after a provider failure.
They are not per-task choices or independent opinions.

Two OpenRouter routes are the primary workhorses for dispatched work:

1. `openrouter/openai/gpt-5.6-luna:xhigh` — deep-reasoning workhorse.
2. `openrouter/deepseek/deepseek-v4-flash-0731:high` — fast bulk workhorse.

Every agent ladder starts with these two routes.
`researcher`, `qa-master`, and `qa-persona` lead with DeepSeek; the rest lead
with Luna. `designer` keeps Kimi K3 first because it spends no premium quota.
Subscription routes follow as escalation and availability fallbacks.
Every ladder ends with `openrouter/x-ai/grok-4.5:high` →
`openrouter/z-ai/glm-5.2:high`.

| Agent | Workhorse head | Subscription fallbacks after the head | Reasoning |
|---|---|---|---:|
| `architect` | Luna → DeepSeek | GPT-5.6 Sol → Fable 5 → Opus 5 → GPT-5.6 Luna (codex) → Kimi K3 → Grok 4.5 → Gemini 3.6 Flash | `xhigh` |
| `builder` | Luna → DeepSeek | GPT-5.6 Luna (codex) → GPT-5.6 Sol → Fable 5 → Kimi K3 → Grok 4.5 → Gemini 3.6 Flash → Opus 5 | `xhigh` |
| `verifier` | Luna → DeepSeek | GPT-5.6 Sol → Fable 5 → Opus 5 → GPT-5.6 Luna (codex) → Grok 4.5 → Gemini 3.6 Flash → Kimi K3 | `xhigh` |
| `researcher` | DeepSeek → Luna | Gemini 3.6 Flash → Grok 4.5 → GPT-5.6 Luna (codex) → GPT-5.6 Sol → Fable 5 → Kimi K3 → Opus 5 | `high` |
| `designer` | Kimi K3 → Luna → DeepSeek | Fable 5 → GPT-5.6 Luna (codex) → GPT-5.6 Sol → Gemini 3.6 Flash → Grok 4.5 → Opus 5 | `max` |
| `qa-master` | DeepSeek → Luna | GPT-5.6 Luna (codex) → Gemini 3.6 Flash → Grok 4.5 → Fable 5 → GPT-5.6 Sol → Kimi K3 → Opus 5 | `high` |
| `qa-persona` | DeepSeek → Luna | Gemini 3.6 Flash → GPT-5.6 Luna (codex) → Grok 4.5 → Fable 5 → GPT-5.6 Sol → Kimi K3 → Opus 5 | `high` |
| `sculptor` | Luna → DeepSeek | GPT-5.6 Sol → Fable 5 → Opus 5 → GPT-5.6 Luna (codex) → Grok 4.5 → Gemini 3.6 Flash → Kimi K3 | `max` |

## Fixed policy

Every listed favorite can perform every role.
The order records preference and provider resilience, not a capability boundary.
OpenRouter spend is accepted: the two workhorse routes preserve premium
subscription tokens (GPT-5.6 Sol, Claude Fable 5, Claude Opus 5, and other
subscription quotas). Premium routes are escalation and availability
fallbacks, not the normal route.
Kimi K3 is primary only for `designer`.
Use GPT-5.6 Luna `medium` as the cheap route for `commit`, `smol`, and `tiny`.

No active route uses Claude Sonnet 5.
Every DeepSeek route must be exactly
`openrouter/deepseek/deepseek-v4-flash-0731:high`.
Do not use unversioned, older, newer, or provider-alias DeepSeek selectors.

`high` is the minimum substantive reasoning level.
Unknown risk never lowers reasoning.
Verifier independence requires a fresh non-mutating lane and a distinct oracle.
A different model alone does not provide independence.

## Provider boundary

Mint is the only credential boundary.
Route OpenRouter through
`http://mint.tail5f5eb4.ts.net:4949/proxy/https/openrouter.ai/api/v1`.
Use only the value-free `__mint.openrouter.default__` placeholder.
Never put credential bytes in a task brief, declaration, or log.

## Evidence

Provider catalogs prove availability only.
They do not prove task quality, billing, or tool reliability.
Keep the lane result and its oracle.
Record a fallback as transport resilience, not a second opinion.
