---
name: model-research
description: Research current AI models, OMP roles, model effort, subscriptions, and fallback routes.
disable-model-invocation: false
argument-hint: "[role|model|provider]"
---

# /model-research

Research current models with the OpenRouter MCP and this skill.
Use this skill to add OMP, local account, and source checks.
Use a primary source for one known model fact.

## Method

1. Run `omp models refresh` and `omp models --json`.
2. Run `omp usage --json --redact`.
3. Read `references/evidence.md`.
4. Get live OpenRouter data with the OpenRouter MCP.
5. Read `references/roles.md` for role or fallback work.
6. Compare capability, quality, speed, price, access, and effort.
7. Record each conflict. Use the source that controls the target interface.
8. Give one dated table and one recommendation. State each limit.

Use ASD-STE100 language. Protect credentials and account data.

## Completion Gate

Complete the work when each selector exists in OMP, each effort is valid, each
fallback is usable or marked conditional, and each current claim has a dated
source.