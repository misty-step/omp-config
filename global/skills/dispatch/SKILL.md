---
name: dispatch
description: |
  Route substantive work to native OMP agents by outcome. Use when the operator
  asks to delegate, investigate, build, verify, review, design, research, prune,
  or run persona QA. Trigger: /dispatch, /route, /delegate.
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
- `verifier` owns independent review, live proof, and incident evidence.
- `researcher` owns read-only repository, library, API, and external research.
- `designer` owns product and interface design through rendered proof.
- `sculptor` owns read-only deletion and deep-module critique inside a critic gate.

`qa-master` and `qa-persona` are structural persona QA utilities.
Persona QA always uses chief → `qa-master` → `qa-persona`.
The chief dispatches the master directly.
No executive dispatches persona QA.

## Kits

Each agent autoloads one primary kit. Branch methods stay hand-only until the kit or brief loads them.

| Agent | Autoloaded kit | Brief-only add-ons |
|---|---|---|
| architect | `project-engineering` | `mcp-design`, `eval-design` |
| builder | `deliver`, `ci` | `powder`, domain skills |
| designer | `design` | `prototype`, `improve-ui`, `baseline-ui`, `image-gen` |
| researcher | `research` | `peer-harnesses` |
| verifier | `verify` | lens names inside verify |
| sculptor | `prune` | none |
| qa-master | `qa-users` | none |
| qa-persona | `qa-persona` | none |

## Route

1. State one accepted outcome and its oracle.
2. Choose the broad agent that owns the outcome.
3. Put task-specific method, scope, and evidence needs in the brief.
4. Name any specialist skill the agent must read beyond its kit.
5. Dispatch independent slices together.
6. Keep shared decisions and integration with the chief.

Do not create a specialist agent because a prompt can carry the method.
Do not create a coordinator when the chief can supervise the lanes directly.
Use one agent for coupled work.
Use multiple agents only for independent evidence or independent mutable surfaces.

## Native limits

OMP selects the model ladder, tools, and autoloaded skills from the named agent declaration.
It cannot select a different model, tool list, or skill bundle for one native spawn.
Accept that limit.
Do not emulate it with a second process protocol.

Task briefs may narrow work by instruction.
They do not widen the declared tool authority.

Sealed launch compositions must list every root and child autoload skill.
Today the compiler injects the full composition skill list into the sealed root prompt.
Keep sealed roots thin, or fix per-agent injection before relying on fat child kits there.

## Model policy

Use `high` as the minimum reasoning level for substantive work.
Treat every listed favorite as capable of every role.
Use role order to express preference, not exclusivity.

Two OpenRouter routes are the primary workhorses for dispatched work:

1. `openrouter/openai/gpt-5.6-luna:xhigh` — deep-reasoning workhorse.
2. `openrouter/deepseek/deepseek-v4-flash-0731:high` — fast bulk workhorse.

OpenRouter spend is accepted. It preserves premium subscription tokens
(GPT-5.6 Sol, Claude Fable 5, Claude Opus 5, and other subscription quotas).
Premium subscription routes remain in every ladder as escalation and
availability fallbacks, not as the normal route.
`researcher`, `qa-master`, and `qa-persona` lead with DeepSeek V4 Flash 0731.
All other agents lead with GPT-5.6 Luna `xhigh` except `designer`, which leads with Kimi K3.
Kimi K3 stays primary only for `designer`; it spends no premium quota.

Use GPT-5.6 Luna `medium` for `commit`, `smol`, and `tiny`.
DeepSeek must use `openrouter/deepseek/deepseek-v4-flash-0731:high`.
Do not use unversioned or provider-alias DeepSeek selectors.
Do not route active work to Claude Sonnet 5.
Treat later ladder entries as availability fallbacks, not independent reviews.

## Verification

For medium-risk work, add one independent verifier.
For high-risk work, add a verifier and review before integration.
The verifier uses a fresh non-mutating lane and a distinct oracle.
The verifier reports findings and never repairs them.
Every substantive critic gate includes one fresh `sculptor` lane.

## Completion

A dispatch completes when each native lane returns its evidence.
The chief resolves contradictions and exercises the integrated live oracle.
Subagent confidence is not evidence.
