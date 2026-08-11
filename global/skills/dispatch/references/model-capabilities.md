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

Agent ladders use subscription capacity first, with one permitted OpenRouter
model as the terminal or high-volume route. The permitted model is
`openrouter/deepseek/deepseek-v4-flash-0731`; agent declarations use its `high`
selector. Deep-reasoning agents (`architect`, `builder`, `verifier`, and
`sculptor`) lead with subscriptions and end at DeepSeek. High-volume agents
(`researcher`, `qa-master`, and `qa-persona`) lead with DeepSeek before their
subscription cascade. `designer` leads with Kimi K3.

The chief `default` cascade in `global/config.yml` is the pattern these
ladders imitate: Claude Fable 5 → Claude Opus 5 → Kimi K3 → xai-oauth Grok
4.5 → Gemini 3.6 Flash → DeepSeek. Each agent keeps its canonical order while
preserving that subscription-first and terminal-DeepSeek shape.

| Agent | Ordered ladder | Reasoning |
|---|---|---:|
| `architect` | `openai-codex/gpt-5.6-sol:max` → `anthropic/claude-fable-5:xhigh` → `anthropic/claude-opus-5:xhigh` → `openai-codex/gpt-5.6-luna:xhigh` → `kimi-code/k3:max` → `xai-oauth/grok-4.5:xhigh` → `google-antigravity/gemini-3.6-flash:high` → `openrouter/deepseek/deepseek-v4-flash-0731:high` | `max` |
| `builder` | `openai-codex/gpt-5.6-sol:xhigh` → `openai-codex/gpt-5.6-luna:xhigh` → `anthropic/claude-fable-5:xhigh` → `kimi-code/k3:high` → `xai-oauth/grok-4.5:xhigh` → `google-antigravity/gemini-3.6-flash:high` → `anthropic/claude-opus-5:xhigh` → `openrouter/deepseek/deepseek-v4-flash-0731:high` | `xhigh` |
| `verifier` | `openai-codex/gpt-5.6-sol:max` → `anthropic/claude-fable-5:xhigh` → `anthropic/claude-opus-5:xhigh` → `openai-codex/gpt-5.6-luna:xhigh` → `xai-oauth/grok-4.5:xhigh` → `google-antigravity/gemini-3.6-flash:high` → `kimi-code/k3:high` → `openrouter/deepseek/deepseek-v4-flash-0731:high` | `max` |
| `sculptor` | `openai-codex/gpt-5.6-sol:max` → `anthropic/claude-fable-5:xhigh` → `anthropic/claude-opus-5:xhigh` → `openai-codex/gpt-5.6-luna:xhigh` → `xai-oauth/grok-4.5:xhigh` → `google-antigravity/gemini-3.6-flash:high` → `kimi-code/k3:high` → `openrouter/deepseek/deepseek-v4-flash-0731:high` | `max` |
| `designer` | `kimi-code/k3:max` → `anthropic/claude-fable-5:xhigh` → `openai-codex/gpt-5.6-sol:xhigh` → `openai-codex/gpt-5.6-luna:xhigh` → `google-antigravity/gemini-3.6-flash:high` → `xai-oauth/grok-4.5:xhigh` → `anthropic/claude-opus-5:xhigh` → `openrouter/deepseek/deepseek-v4-flash-0731:high` | `max` |
| `researcher` | `openrouter/deepseek/deepseek-v4-flash-0731:high` → `google-antigravity/gemini-3.6-flash:high` → `xai-oauth/grok-4.5:high` → `openai-codex/gpt-5.6-luna:xhigh` → `openai-codex/gpt-5.6-sol:high` → `anthropic/claude-fable-5:high` → `kimi-code/k3:high` → `anthropic/claude-opus-5:high` | `high` |
| `qa-master` | `openrouter/deepseek/deepseek-v4-flash-0731:high` → `google-antigravity/gemini-3.6-flash:high` → `openai-codex/gpt-5.6-luna:high` → `xai-oauth/grok-4.5:high` → `openai-codex/gpt-5.6-sol:high` → `anthropic/claude-fable-5:high` → `kimi-code/k3:high` → `anthropic/claude-opus-5:high` | `high` |
| `qa-persona` | `openrouter/deepseek/deepseek-v4-flash-0731:high` → `google-antigravity/gemini-3.6-flash:high` → `openai-codex/gpt-5.6-luna:high` → `xai-oauth/grok-4.5:high` → `openai-codex/gpt-5.6-sol:high` → `anthropic/claude-fable-5:high` → `kimi-code/k3:high` → `anthropic/claude-opus-5:high` | `high` |

## Fixed policy

Every listed favorite can perform every role.
The order records preference and provider resilience, not a capability boundary.
Subscription capacity is preferred for deep-reasoning routes.
The only OpenRouter model permitted in agent ladders is
`openrouter/deepseek/deepseek-v4-flash-0731`.
Kimi K3 is the head only for `designer`; other ladders may use it as a
fallback.

Agent ladders use exactly
`openrouter/deepseek/deepseek-v4-flash-0731:high`.
The chief configuration keeps its existing max-strength DeepSeek selectors for
roles and fallback chains; those selectors use the same permitted model.
Agent ladders do not use Claude Sonnet 5. The current `vision` fallback in
`global/config.yml` still names `anthropic/claude-sonnet-5:max` and requires
chief-owned reconciliation.

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
