---
roster_review_due: 2026-08-08
---

# Open-model roster policy

Choose open-model defaults for OMP peer lanes here.
**Live model facts, prices, CLI forms, and provider routes live in**
`/home/phaedrus/.omp/agent/skills/harness-engineering/references/model-provider-harness-index.md`.
Do not duplicate that catalog in this file.
Re-check the index and run a local smoke before any default change.

## Current defaults (role fit)

| Lane | Default (OpenRouter id) | Use first when |
|---|---|---|
| OpenCode | `moonshotai/kimi-k2.7-code` | Code-centric review, session/event shape, runner-adapter work |
| Pi | `moonshotai/kimi-k2.7-code` | Small decorrelated peer lanes with low harness overhead |
| Goose | `moonshotai/kimi-k2.7-code` | MCP-heavy cross-system workflows |

Claude, Antigravity, Cursor, and Grok remain conditional tools when a smoke-tested
open-model lane cannot answer the question.
Re-run price/capability comparison when a proprietary lane changes.

## Smoke before promotion

Require a headless smoke on the target CLI with a fixed sentinel before promoting
a default. Record receipt id, date, and command in the change that moves the
default — not as a permanent price table here.

## Named role aliases (not prices)

| Alias | Model family intent |
|---|---|
| `previous_kimi` | prior Kimi for rollback/A-B |
| `thinking_kimi` | Kimi thinking surface |
| `long_context` | DeepSeek V4 Pro class |
| `budget_long_context` | DeepSeek V4 Flash class |
| `alternate_agentic` | MiniMax M3 class |
| `qwen_coder` | Qwen coder family |

Resolve concrete slugs and limits from the central index at dispatch time.
