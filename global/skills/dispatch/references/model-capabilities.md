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

| Agent | Native model ladder | Reasoning |
|---|---|---:|
| `architect` | `openai-codex/gpt-5.6-sol:max` → `anthropic/claude-fable-5:xhigh` → `kimi-code/k3:max` | `max` |
| `builder` | `openai-codex/gpt-5.6-luna:xhigh` → `kimi-code/k3:high` → `openrouter/deepseek/deepseek-v4-flash-0731:high` | `xhigh` |
| `verifier` | `kimi-code/k3:high` → `xai-oauth/grok-4.5:xhigh` → `openai-codex/gpt-5.6-sol:high` → `openrouter/deepseek/deepseek-v4-flash-0731:high` | `xhigh` |
| `researcher` | `kimi-code/k3:high` → `openrouter/deepseek/deepseek-v4-flash-0731:high` → `openai-codex/gpt-5.6-luna:xhigh` → `anthropic/claude-fable-5:high` | `high` |
| `designer` | `kimi-code/k3:max` → `anthropic/claude-fable-5:xhigh` → `anthropic/claude-opus-5:xhigh` → `openai-codex/gpt-5.6-luna:xhigh` | `max` |
| `qa-user` | `kimi-code/k3:high` → `openai-codex/gpt-5.6-luna:xhigh` | `high` |
| `qa-user-leaf` | `kimi-code/k3:high` → `openai-codex/gpt-5.6-luna:xhigh` | `high` |

## Fixed policy

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
