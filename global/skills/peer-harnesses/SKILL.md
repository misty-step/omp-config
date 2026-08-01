---
disable-model-invocation: true
name: peer-harnesses
description: |
  Documents peer AI agent command surfaces (codex, pi, goose, opencode,
  claude, cursor-agent, grok, agy, hermes, oracle) and how to invoke each
  headlessly. A capability map, not an installation claim or quota: useful
  for fresh-context adversarial review on a different model family, second
  opinions, competing attempts, and wide benches. Use when: "ask codex",
  "ask another model", "second opinion", "cross-model review", "what AI
  tools do I have", "other agents", "different model family", "adversarial
  critique from another provider". Trigger: /peer-harnesses.
argument-hint: "[provider] [task]"
---

# /peer-harnesses

These command surfaces can run headlessly when installed. They are options, not obligations.
Native subagents remain the default delegation path. Give a peer harness a
lane only when it adds a decorrelated model family or a genuinely fresh
context.

## When a peer harness beats a native subagent

- **Adversarial critique of your own work.** Ask a different model family to review your work. Its failure modes differ from yours. Give critics only the artifact and oracle. Never give them the author's reasoning trail (Shared Operating Spine: Prove).
- **Second opinion on a contested judgment.** Use another model for an architecture call, risk assessment, or idiom check. Do not let one model's taste decide alone.
- **Competing attempts** at the same bounded problem, graded blind.
- **Wide bench.** Use a high-stakes adversarial review for a P0, security or data-loss surface, or pre-ship "be exhaustive" pass. Fan the artifact across several *distinct* open-model families through Pi/OpenRouter. Give each critic one lens. Distinct families find distinct real issues instead of confirming each other. See **Adversarial bench** below.

A native subagent remains better for exploration and scoped builds. Use it when
harness identity does not matter. It shares your tools, needs no cold start, and
the orchestrator is trained on it.

## The CLIs

Standalone command discovery was last positive on 2026-06-14, with Grok
re-probed on 2026-07-08. Native OMP Luna and OpenRouter routes passed
sentinels on 2026-08-01.
Probe each standalone command in its normal login environment before dispatch.
Each row shows its headless form.

| CLI | Stack | Headless invocation |
|---|---|---|
| `codex` | OpenAI Codex (gpt-5.6-luna) | `codex exec "<task>"` (`--model`, `--config model_reasoning_effort=`) |
| `pi` | Pi over OpenRouter (Kimi, DeepSeek, …) | `pi -p --no-extensions --provider openrouter --model <id> "<task>"` |
| `goose` | Goose over OpenRouter | `goose run --no-session --quiet --provider openrouter --model <id> --text "<task>"` |
| `opencode` | OpenCode over OpenRouter | `opencode run --model openrouter/<id> --format json "<task>"` |
| `claude` | Claude Code (Opus/Fable) | `claude -p "<task>"` (`--model`, `--effort`) |
| `cursor-agent` | Cursor (composer) | `cursor-agent -p "<task>"` |
| `grok` | xAI Grok Build (grok-4.5 default) | `grok -p "<task>"` (`--model`, `--reasoning-effort`, `--best-of-n`, `--check`, `--json-schema`) |
| `agy` | Antigravity (Gemini) | `agy --print "<task>"` |
| `hermes` | Hermes agent | `hermes -z "<task>"` (`-m <model>`) |
| `oracle` | Oracle browser consult | `npx -y @steipete/oracle --engine browser --model gpt-5.5-pro -p "<task>" --file <paths>` |

### OpenRouter credentials: Mint, no env keys

`pi`, `goose`, and `opencode` route OpenRouter through the Mint broker.
Each tool holds only the value-free placeholder `__mint.openrouter.default__`
and a Mint base URL; Mint policy injects the real key at egress.
No `OPENROUTER_API_KEY` environment variable exists on this machine.
Never set one, and never replace a placeholder with a real key.
Verified live with `LANE_OK` completions on 2026-08-01:

| CLI | Config file | Route |
|---|---|---|
| `pi` 0.83.0 | `~/.pi/agent/models.json` | `baseUrl: http://mint.tail5f5eb4.ts.net:4949/proxy/https/openrouter.ai/api/v1`, `apiKey: __mint.openrouter.default__` |
| `goose` 1.45.0 | `~/.config/goose/config.yaml` + `secrets.yaml` | `OPENROUTER_HOST: http://mint.tail5f5eb4.ts.net:4949/proxy/https/openrouter.ai` (goose appends `/api/v1/...` itself); placeholder in `secrets.yaml` with `GOOSE_DISABLE_KEYRING: true` |
| `opencode` 1.18.11 | `~/.config/opencode/opencode.json` | `provider.openrouter.options.baseURL` (Mint `/api/v1` URL) + `options.apiKey` placeholder |

A 401 from these lanes means the config file lost its Mint route.
A 403 means Mint policy denies the actor, method, or path; widen the grant in
Mint policy, never work around the boundary.

### Oracle browser consult details

Use a signed-in ChatGPT browser session for Oracle consults.
Do not use Oracle API mode.
Preview every run:

```sh
npx -y @steipete/oracle --engine browser --model gpt-5.5-pro \
  --dry-run summary --files-report \
  -p "<task>" --file "src/**" --file "!**/*.test.*"
```

Run a consult only after its preview is sensible:

```sh
npx -y @steipete/oracle --engine browser --model gpt-5.5-pro \
  --slug "<3-5-words>" \
  -p "<task>" --file "src/**" --file "!**/*.test.*"
```

Inspect a detached or timed-out run instead of rerunning it:

```sh
npx -y @steipete/oracle status --hours 72
npx -y @steipete/oracle session <id> --render
```

Current model ids, pricing, context windows, and freshness dates:
`references/model-provider-harness-index.md`.
Model facts and harness facts become stale within days.
The OpenAI GPT-5.6 Luna price cut on 2026-07-30 and DeepSeek V4 Flash 0731 release on 2026-07-31 can reorder the bench overnight.
Refresh the index with `/research` or `/harness-engineering models` when its review date passes, a new frontier release appears, or a composition decision the index cannot settle occurs.
Refresh before dispatching on remembered facts.

## Adversarial bench

High-stakes review needs a *model-family spread*, not one second opinion.
Distinct families find distinct real bugs. One P0 pass found a
startup-bricking blocker, a null-timestamp escape, and a write-path gap across
three families.

- **3–5 distinct families** (Kimi/Moonshot, DeepSeek, MiniMax, Qwen,
  GLM/Zhipu when listed). Same-family variants do not decorrelate. A wide bench
  from one family wastes capacity.
- **Discover slugs live**: `pi --provider openrouter --list-models
  <family>`. Slugs rot in days. Substitute when a family is not listed.
- **One distinct lens per critic** (correctness/data-loss, durability,
  security, perf, API-shape — `global/references/lenses.md`).
  Optionally load that lens or a domain skill into the critic: `pi --skill
  <path>`.
- **Cold, bounded, artifact-only**: Inline everything the lane needs. Include
  the diff, oracle, and context. Run
  `pi -p --no-extensions --no-tools --provider openrouter --model <slug>
  "<prompt>"` in background lanes. Synthesize the verdicts yourself. Add one
  or two native critics on their own lenses. Re-review the *delta* after you
  fix it.

Scale the bench to the stakes. Give a routine diff one well-aimed cross-family
critic instead of the full bench.

## Judgment

- One well-aimed critic beats three vague critics. Aim at the claim that would
  embarrass us in production. Add explicit "ignore style/naming" bounds.
- Treat peer output as evidence, not authority. Weigh it, accept or reject it,
  and own the result.
- Report a failed or rambling lane. Do not re-roll it silently.
- For a bounded lane whose evidence should outlive the session, write the
  receipt to Powder. Use a run, comment, or link on the card that receives the
  work. This remains optional for a quick second opinion and useful for a ship
  decision.
- Run heavy, long-running, or isolation-needing lanes on sprites (`/sprites`)
  regardless of the CLI.

## Gotchas

- Peer CLIs run cold. They have no conversation history and no local skills
  unless the harness loads them.
- Inline everything the lane needs.
- Auth rots independently per CLI. If a lane fails at once with an auth error,
  re-login locally. Do not treat the failure as a provider verdict.

## Prompting frontier lanes

For Fable and GPT-5.6 Luna lanes, and for the lead's own operation, load
`global/references/prompting-frontier.md`. Use goal-not-steps briefs fenced by
house rules. Use executable bars and delegate metric invention when a bar is
fuzzy. Verify against the REAL output; the builder never grades. Loop until the
bar passes and keep a live status artifact. Use prior traces as fuel and
budgets instead of permission asks. Give cheaper models more mechanism. Tune
the prescription to the model and reasoning effort.
