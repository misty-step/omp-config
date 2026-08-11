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

`global/skills/dispatch/references/agent-roster.json` holds the exact ordered
ladders. `bin/check` fails when the roster and the agent frontmatter disagree,
so read the roster instead of copying ladders into prose.

| Agent | Head | Terminal | Reasoning |
|---|---|---|---:|
| `architect` | GPT-5.6 Sol | DeepSeek | `max` |
| `builder` | GPT-5.6 Sol | DeepSeek | `xhigh` |
| `verifier` | GPT-5.6 Sol | DeepSeek | `max` |
| `sculptor` | GPT-5.6 Sol | DeepSeek | `max` |
| `designer` | Kimi K3 | DeepSeek | `max` |
| `researcher` | DeepSeek | Claude Opus 5 | `high` |
| `qa-master` | DeepSeek | Claude Opus 5 | `high` |
| `qa-persona` | DeepSeek | Claude Opus 5 | `high` |

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
Agent ladders and the chief configuration do not use Claude Sonnet 5.

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
