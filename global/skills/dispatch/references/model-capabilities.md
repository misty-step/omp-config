# Native model and reasoning policy

This reference owns agent-model fit.
It does not own model facts.
Read `skill://peer-harnesses/references/model-provider-harness-index.md` for
dated availability, price, context, and harness evidence.

## Agent ladders

OMP 17.2.3 reads each named agent's ordered model list.
The first route is the normal route.
Later routes provide availability resilience after a provider failure.
They are not per-task choices or independent opinions.

Every agent appends this OpenRouter tail after its subscription routes:

`openrouter/deepseek/deepseek-v4-flash-0731:high` →
`openrouter/openai/gpt-5.6-luna:<role-effort>` →
`openrouter/x-ai/grok-4.5:high` →
`openrouter/z-ai/glm-5.2:high`.

| Agent | Ordered subscription routes before the shared OpenRouter tail | Reasoning |
|---|---|---:|
| `architect` | GPT-5.6 Sol → Fable 5 → Opus 5 → GPT-5.6 Luna → Kimi K3 → Grok 4.5 → Gemini 3.6 Flash | `max` |
| `builder` | GPT-5.6 Luna → GPT-5.6 Sol → Fable 5 → Kimi K3 → Grok 4.5 → Gemini 3.6 Flash → Opus 5 | `xhigh` |
| `verifier` | GPT-5.6 Sol → Fable 5 → Opus 5 → GPT-5.6 Luna → Grok 4.5 → Gemini 3.6 Flash → Kimi K3 | `max` |
| `researcher` | Gemini 3.6 Flash → Grok 4.5 → GPT-5.6 Luna → GPT-5.6 Sol → Fable 5 → Kimi K3 → Opus 5 | `high` |
| `designer` | Kimi K3 → Fable 5 → GPT-5.6 Luna → GPT-5.6 Sol → Gemini 3.6 Flash → Grok 4.5 → Opus 5 | `max` |
| `qa-user` | GPT-5.6 Luna → Gemini 3.6 Flash → Grok 4.5 → Fable 5 → GPT-5.6 Sol → Kimi K3 → Opus 5 | `high` |
| `qa-user-leaf` | Gemini 3.6 Flash → GPT-5.6 Luna → Grok 4.5 → Fable 5 → GPT-5.6 Sol → Kimi K3 → Opus 5 | `high` |

## Fixed policy

Every listed favorite can perform every role.
The order records preference and provider resilience, not a capability boundary.
Kimi K3 is primary only for `designer`.
`verifier` starts with GPT-5.6 Sol and Claude Fable 5.
`researcher` starts with Gemini 3.6 Flash, Grok 4.5, and GPT-5.6 Luna.
Subscription routes precede the shared OpenRouter tail.

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
