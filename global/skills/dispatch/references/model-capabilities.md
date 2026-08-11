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

Agent ladders use subscription capacity first, in one canonical order:
OpenAI subscription flagship first, then the Anthropic Sonnet-class, then the
Anthropic Opus-class, then XAI OAuth Grok, then Kimi Code K3, then the
Google flash-class. The one permitted OpenRouter model is the terminal
catch-all on every ladder:
`openrouter/deepseek/deepseek-v4-flash-0731`; agent declarations use its
`high` selector. Every ladder ends at DeepSeek. Reasoning level varies by
agent: `architect`, `builder`, `verifier`, and `sculptor` lead with the
OpenAI flagship at `max` or `xhigh`; `researcher`, `qa-master`, and
`qa-persona` run the same order at `high`; `designer` leads with the OpenAI
flagship at `max` and may prefer Kimi K3 for design-tuned work.

`global/skills/dispatch/references/agent-roster.json` holds the exact ordered
ladders. `bin/check` fails when the roster and the agent frontmatter disagree,
so read the roster instead of copying ladders into prose.

| Agent | Head | Terminal | Reasoning |
|---|---|---|---:|
| `architect` | OpenAI flagship | DeepSeek | `max` |
| `builder` | OpenAI flagship | DeepSeek | `xhigh` |
| `verifier` | OpenAI flagship | DeepSeek | `max` |
| `sculptor` | OpenAI flagship | DeepSeek | `max` |
| `designer` | OpenAI flagship | DeepSeek | `max` |
| `researcher` | OpenAI flagship | DeepSeek | `high` |
| `qa-master` | OpenAI flagship | DeepSeek | `high` |
| `qa-persona` | OpenAI flagship | DeepSeek | `high` |

## Fixed policy

Every listed favorite can perform every role.
The order records preference and provider resilience, not a capability boundary.
Subscription capacity is preferred for every route.
The only OpenRouter model permitted in agent ladders is
`openrouter/deepseek/deepseek-v4-flash-0731`.
DeepSeek is the paid catch-all terminal, never the head.
All other models in the ladder route through their subscription providers.

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
