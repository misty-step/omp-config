# Model, Provider, and Reasoning Matrix

This file owns role-fit policy.
Keep the factual catalog and freshness evidence in
`skill://peer-harnesses/references/model-provider-harness-index.md`.
`global/config.yml` owns model-role bindings and retry fallbacks.
Read both when a model id or provider route changed after this file's last update.


Last policy update: 2026-08-01.

## Preferred capability models

| Model | Provider route | Reasoning levels we use | Use for | Do not use for |
|---|---|---|---|---|
| Claude Fable 5 | `anthropic` | high, xhigh | chief execution, ambiguous synthesis, integration, high-consequence judgment | cheap mechanical collection |
| GPT-5.6 Sol | `openai-codex` | high, xhigh, max | architecture, decomposition, formal reasoning, difficult cross-system debugging | routine file mechanics |
| GPT-5.6 Luna | `openai-codex` | high, xhigh, max | primary accepted implementation and repository work; text+image tasks; broader hosted tools; cost-sensitive high-volume work when modality and local evidence fit | independent review of its own work; high-consequence arbitration without an independent check |
| DeepSeek V4 Flash 0731 | `openrouter/deepseek/deepseek-v4-flash-0731` | high locally; first-party low, high, max | cost-shaped, high-volume, bounded text-only agentic and coding work | image/file work, high-consequence arbitration, or default use without local workload proof |
| Claude Sonnet 5 | `anthropic` | high, xhigh | tool-heavy execution, verification, reliable general work | primary architecture when Sol or Fable fits |
| Kimi K3 | `kimi-code` | high | long-context research, broad synthesis, design bench work | high-consequence arbitration without an independent check |
| Grok 4.5 | `xai-oauth` | high | adversarial review, assumption breaking, strategy, independent challenge | implementing the artifact it reviews |
| GLM 5.2 | `openrouter/z-ai/glm-5.2` | high | design alternatives and implementation alternatives when no native Z.AI route exists | default routing when a native subscription model fits |
| Gemini 3.6 Flash | `openrouter/google/gemini-3.6-flash` | minimal, low, medium, high | multimodal inspection, broad fast analysis, rendered UI verification | flash-lite work; accepted implementation |
| Gemini 3.5 Flash Lite | `openrouter/google/gemini-3.5-flash-lite` | auto | tiny classification, bounded inventory, cheap fallback | primary judgment or implementation |
| GPT-5.5 Pro browser | `peer-harnesses` browser mode | provider default | a signed-in, large-context second opinion on hard architecture or debugging | API mode or routine review |

## Cost-aware selection

Select with task quality, marginal spend, modality, provider route, and local harness evidence together.
Treat independent benchmark near-parity as a prior, not transfer proof for local task quality.
Use Luna at xhigh for normal accepted builds; raise to max only for demonstrated hard autonomous work.
The generic `task` role is an explicit policy exemption: it receives unclassified substantive work and stays at Luna max. Declared builder/fixer accepted implementation stays at xhigh on Luna.
Use DeepSeek Flash 0731 at high for bounded text-only cost-shaped work because local OpenRouter metadata exposes high only. The representative local workload probe is recorded in `global/skills/peer-harnesses/references/model-provider-harness-index.md` and covers only a bounded repository-read task.
DeepSeek does not replace Luna for accepted implementation, image/file work, or high-consequence arbitration.
For builder/fixer, DeepSeek is a resilience-only terminal fallback after Luna and Sonnet provider failure; it is not the accepted-implementation primary.
Select DeepSeek only after the representative local workload evaluation confirms the task fit; that bounded repository-read probe does not prove all workloads.

Use native subscription providers first when they offer the required model.
For API-key-only providers, route calls through
`http://mint.tail5f5eb4.ts.net:4949/proxy/https/<host>/<path>`.
Config carries only value-free `__mint.<service>.<name>__` placeholders.
Tailnet WhoIs identifies callers. Mint policy is the grant, and its approved
rule owns `Authorization` at the upstream boundary.
Never put credential bytes in agent context.

The review protocol does not use this matrix to select a leaf, runner,
provider, model, or harness. A caller supplies explicit worker attribution to
the gate; this matrix remains general role-fit guidance only.


## Reasoning selection

| Work | Default | Raise when | Ceiling |
|---|---|---|---|
| chief synthesis | high | irreversible, security-sensitive, architectural, or deeply ambiguous | xhigh |
| architecture or formal debugging | high | several systems, hidden invariants, or high consequence | max on Sol |
| implementation | xhigh on Luna | already the default for accepted build lanes | max only for a demonstrated hard reasoning need |
| review or verification | high | high risk or ambiguous evidence | the role model's supported ceiling |
| research | high | conflicting sources or broad synthesis | provider-supported high |
| mechanical collection | default/auto | never; reclassify the work if judgment appears | high only after reclassification |

Unknown estimate or risk never lowers reasoning.
Treat unknown risk as at least medium and add an independent verifier.


Fallback chains in `global/config.yml` activate only after an error or timeout.
They do not express quality order.
Pin a model explicitly when capability or provider diversity matters.

Use a different model family for independent review.
Do not ask one model to verify its own work and call the result independent.

OpenRouter-only routes use the Mint upstream boundary at
`http://mint.tail5f5eb4.ts.net:4949/proxy/https/openrouter.ai/api/v1`.
The route uses the `__mint.<service>.<name>__` grammar, specifically
`__mint.openrouter.default__`. Tailnet WhoIs identifies the caller.
Mint policy is the grant and owns `Authorization` at the upstream boundary.
Prefer native OAuth routes when capabilities are equivalent.
Do not replace a current model with an older model from the same class because a subscription catalog lacks the newer model.


`global/config.yml` carries DeepSeek as the `smol` primary and other models in retry chains.
The explicit matrix and shaped local evidence justify role fit; retry order never does.
