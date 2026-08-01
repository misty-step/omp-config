---
disable-model-invocation: true
name: council
description: |
  Convene distinct OpenRouter model families through opencode/pi. Give each
  model a generative persona, then synthesize the result as chair.
  Trigger: /council, /thinktank.
argument-hint: "[question|task]"
---

# /council

You are the chair, not a participant.
Convene a small bench of distinct model families, give each member a different generative persona, and ask divergent questions.
Synthesize the output to produce decorrelated options, framings, first-principles takes, non-obvious moves, and disagreements.

This skill is the generative sibling of `/peer-harnesses`; use that skill for peer dispatch mechanics, CLIs, and the live model index.
The sibling reviews artifacts for bugs with one lens per lane; this skill owns composition and synthesis.

## When to convene

- Convene for contested design or direction, wide-open approach questions, divergence before a plan, or ideation where one model's taste must not decide.
- Use at least 4 structurally distinct voices for non-trivial architecture.
- Do not convene for factual lookups, settled decisions, or work one native subagent can answer.
- Each lane costs a paid inference run, so use a council only when options justify the cost.

## Compose the bench

Decorrelation requires two axes: model family and generative lens.

1. Use 4–6 distinct families, such as Kimi/Moonshot, DeepSeek, Qwen, GLM/Zhipu, or MiniMax.
   Same-family variants do not decorrelate; optionally add a frontier closed model for more spread.
   Never hardcode slugs. Use `global/skills/peer-harnesses/references/model-provider-harness-index.md` or the user-scoped OpenRouter MCP (`models-list`, `benchmarks`, `model-endpoints`).
2. Give each member a different persona from `references/personas.md` and a bespoke lens for the question.

Scale the bench to risk: use 3 members for quick divergence; use 5–6 plus one or two native subagents for load-bearing decisions.

## Run the council

`scripts/council.sh` runs lanes in parallel, caps each lane, and collects every output. Report failed lanes; do not hide them.

```text
# members.tsv: label <TAB> cli <TAB> model <TAB> persona   ('#' comments ok)
scripts/council.sh --task /tmp/q.txt --members /tmp/members.tsv --outdir /tmp/council
```

Write the shared task to one file because lanes have no shared history. Include every constraint, goal, and quality criterion.
Use the script default `1200s`; shorten only for smoke checks or slug probes; use `--timeout 1800s` for load-bearing calls.
The caller capped a lane that hits the limit; rerun or exclude it before treating it as a model-quality verdict.

## Synthesize

Read lanes; do not paste them without analysis.

- Surface the non-obvious idea or framing you would not reach alone.
- Name the real disagreement, state the tension, and make your call.
- Do not vote or tally. Agreement across models is weak evidence; one sharp dissent can be right.
- Weigh evidence and own the result. A failed or rambling lane is also a result; say so.

## Gotchas

- Same family or same lens across lanes does not provide useful diversity. Vary both axes or do not convene.
- Divergence widens options; the chair or a focused follow-up narrows them. Do not ask the bench to pick the winner.
- Cost is real. Match bench size to risk, use `--timeout` as the execution limit, and check OpenRouter MCP `credits-get`.

