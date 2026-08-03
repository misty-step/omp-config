---
name: dispatch
description: |
  Route substantive work to five broad native OMP agents. Use when the operator
  asks to delegate, investigate, build, verify, review, design, or research.
  Trigger: /dispatch, /route, /delegate.
argument-hint: "[task|card]"
---

# /dispatch

Keep the chief on intent, decomposition, supervision, integration, and final judgment.
Use native OMP task dispatch.
Do not add a scheduler, process wrapper, generated agent, or task-specific declaration.

Read `references/primitive-routing.md` and
`references/model-capabilities.md` before substantive dispatch.

## Native agents

- `architect` owns read-only system boundaries, tradeoffs, and dependency order.
- `builder` owns accepted repository mutation and live delivery.
- `verifier` owns independent review, security, live QA, and incident evidence.
- `researcher` owns read-only repository, library, API, and external research.
- `designer` owns product and interface design through rendered proof.

`qa-user` and `qa-user-leaf` are structural persona utilities.
Persona QA always uses chief → `qa-user` → `qa-user-leaf`.
The chief dispatches the coordinator directly.
No executive dispatches persona QA.

## Route

1. State one accepted outcome and its oracle.
2. Choose the broad agent that owns the outcome.
3. Put task-specific method, scope, and evidence needs in the brief.
4. Name any specialist skill the agent must read.
5. Dispatch independent slices together.
6. Keep shared decisions and integration with the chief.

Do not create a specialist agent because a prompt can carry the method.
Do not create a coordinator when the chief can supervise the lanes directly.
Use one agent for coupled work.
Use multiple agents only for independent evidence or independent mutable surfaces.

## Native limits

OMP 17.2.3 selects the model ladder from the named agent declaration.
It cannot select a different model, tool list, or skill bundle for one native spawn.
Accept that limit.
Do not emulate it with a second process protocol.

Every declaration has one explicit tool envelope and one short skill bundle.
Task briefs may narrow work by instruction.
They do not widen the declared tool authority.

## Model policy

Use `high` as the minimum reasoning level for substantive work.
Treat every listed favorite as capable of every role.
Use role order to express preference, not exclusivity.
Kimi K3 is primary only for `designer`.
`verifier` starts with GPT-5.6 Sol and falls back first to Claude Fable 5.
`researcher` starts with Gemini 3.6 Flash, Grok 4.5, and GPT-5.6 Luna.

Always use at least one appropriate subscription route before OpenRouter.
Use GPT-5.6 Luna `medium` for `commit`, `smol`, and `tiny`.
Every OpenRouter tail starts with DeepSeek V4 Flash 0731.
Only OpenRouter GPT-5.6 Luna, Grok 4.5, and GLM 5.2 follow it.
DeepSeek must use `openrouter/deepseek/deepseek-v4-flash-0731:high`.
Do not route active work to Claude Sonnet 5.
Treat later entries as availability fallbacks, not independent reviews.

## Verification

For medium-risk work, add one independent verifier.
For high-risk work, add a verifier and review before integration.
The verifier uses a fresh non-mutating lane and a distinct oracle.
The verifier reports findings and never repairs them.

## Completion

A dispatch completes when each native lane returns its evidence.
The chief resolves contradictions and exercises the integrated live oracle.
Subagent confidence is not evidence.
