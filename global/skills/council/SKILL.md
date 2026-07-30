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
Convene a small bench of distinct model families.
Give each member a different generative persona.
Ask all members to think divergently about one question.
Then synthesize their output.
The purpose is decorrelated thinking that one orchestrator cannot produce alone.

This is the **generative** sibling of `/peer-harnesses`.
Its adversarial bench reviews an artifact to find bugs, with one lens for each lane.
A council generates options, framings, first-principles takes, non-obvious moves, and real disagreements.
Dispatch lanes through the peer harness CLIs and model index from
`/peer-harnesses`.
This skill owns composition and synthesis.


## When to convene (and when not)

- Convene for a contested design or direction decision, a wide-open approach question, a divergence pass before a plan, or an open ideation task where one model's taste should not decide.
  The divergence-for-design-decisions mandate (≥4 structurally distinct voices on non-trivial architecture) applies here.
- Do not convene for a factual lookup, a settled decision, or work that a native
  subagent or one moment can answer.
  A council costs real money because each lane is a paid inference run.
  Use it only when the options justify that cost.


## Compose the bench (the judgment)

Two axes must vary.
Decorrelation comes from family × lens:

1. **Distinct model families.** Use 4–6 members.
   Give each member a different family (Kimi/Moonshot, DeepSeek, Qwen, GLM/Zhipu, MiniMax, …).
   Same-family variants do not decorrelate.
   They waste a wide bench.
   Optionally add a frontier closed model on its own CLI (`codex`, `grok`, `agy`) for more family spread.
   - **Model slugs change quickly. Never hardcode them.** Pull current top models live from `global/skills/peer-harnesses/references/model-provider-harness-index.md` or the **OpenRouter MCP** (`models-list`, `benchmarks`, `model-endpoints` for current quality + pricing).
     `pi --provider openrouter --list-models <family>` lists live slugs.
2. **Distinct generative personas.** Give each member a different persona that pulls in a different direction.
   Use `references/personas.md`.
   Compose a bespoke lens for the real question instead of forcing a stock role.

Scale the bench to task risk.
A quick divergence uses 3 members.
A load-bearing design decision uses 5–6 members plus one or two native subagents on further lenses.


## Run it

`scripts/council.sh` runs the bench in parallel, caps each lane, and collects every output.
Report failed lanes; do not hide them.

```
# members.tsv:  label <TAB> cli <TAB> model <TAB> persona   ('#' comments ok)
scripts/council.sh --task /tmp/q.txt --members /tmp/members.tsv --outdir /tmp/council
```

Write the shared task to one file.
Include all context because lanes run without shared history.
The default `cli` is `opencode` (`opencode run --model
openrouter/<slug>`).
`pi` is the lighter no-tools alternative.
See `/peer-harnesses` for exact headless forms.

Choose the timeout as part of the composition.
The script default is 1200s because tool-using reasoning lanes need real wall time from startup.
Shorten it only for smoke checks or slug probes.
Raise `--timeout` to 1800s for load-bearing design calls.
If a lane hits the cap, the caller capped it.
Rerun or exclude that lane before treating it as a model-quality verdict.


Reading the lanes is the work.
Do not paste them without analysis.

- **Surface the non-obvious.** Report the idea or framing you would not have reached alone.
- **Name the real disagreement.** Where lanes diverge, present the tension and your call, not an average.
- **Do not vote or tally.** Agreement across N models is weak evidence because training overlaps.
  One model's sharp dissent can be right.
  Weigh evidence; do not count votes.
- **Own the result.** Treat council output as evidence.
  You decide and remain accountable.
  A rambling or failed lane is also a result.
  Say so.


## Gotchas

- **Monoculture produces correlated output.** Same family across lanes, or the same lens across all lanes, does not provide useful diversity.
  Vary both axes or do not convene.
- **Independent lanes need full context.** Members share only the task file.
  Put constraints, goal, and quality criteria in the task.
  A member missing context invents it.
- **Model slugs can become stale.** A lane that fails instantly usually has a dead or renamed slug or an auth lapse.
  Re-check live with the `/peer-harnesses` model index or OpenRouter MCP.
  Then rerun that lane.
- **Divergence does not converge in one step.** Use the council to widen the options.
  Then you or a focused follow-up can narrow them.
  Do not ask the bench to pick the winner.
  The chair makes that call.
- **Cost is real.** Match bench size to task risk.
  Use `--timeout` as the execution limit.
  The OpenRouter MCP `credits-get` shows remaining balance.

## Composes with

- `/peer-harnesses` — peer dispatch mechanics, live model index, the adversarial-critique
  counterpart (use that to *review*, this to *generate*).
- `nous-creative-ideation` — a routed library of named ideation methods. Seed a
  member's persona with a specific method (OuLiPo, TRIZ, lateral provocations),
  or run the question through one first when the bench risks converging on the
  obvious.
- The OpenRouter MCP (user-scoped) — live model catalog, benchmarks, pricing,
  and balance for choosing the bench.
