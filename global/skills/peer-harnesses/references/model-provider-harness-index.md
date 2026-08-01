---
model_reference_review_due: 2026-08-08
openai_reference_review_due: 2026-08-08
last_researched: 2026-08-01
substrate_reference_review_due: 2026-07-20
substrate_reference_last_researched: 2026-07-13
speech_reference_review_due: 2026-07-20
speech_reference_last_researched: 2026-07-13
---

# Model / Provider / Harness Index

Factual context for composition design. This reference supplies evidence to a
lead agent, not a routing policy. It must not prescribe role fit, preferred
team shapes, or "best for X" judgments. The lead agent chooses each
composition from the current task, current repo evidence, runtime probes,
receipts, and this factual sheet.

## Freshness Contract

- Review due: 2026-08-08.
- Treat model facts as stale after the review due date.
- Verify exact model ids, availability, prices, context windows, and benchmark
  claims from live provider docs or catalogs before changing defaults.
- Record local smoke evidence in delegation receipts. This file may point to
  receipts, but receipts remain proof that a local harness invocation ran.

## Live model facts: the Mint-brokered OpenRouter catalog

The disabled `openrouter` MCP is not a live authority or runtime route.
Current OpenRouter facts come from the Mint-brokered catalog/API route and
`omp models`; never use direct credentials.
The route is
`http://mint.tail5f5eb4.ts.net:4949/proxy/https/openrouter.ai/api/v1` with the
value-free `__mint.openrouter.default__` placeholder. Mint owns upstream
authorization.
The current OpenRouter rows below were read on 2026-08-01 through that route
and the local `omp models` catalog. OpenRouter scope applies only to those
catalog rows; do not infer local Codex, Claude Code, Antigravity, Cursor, or
Grok CLI pricing or limits from them.

## Local Harness Roster

Source: `global/models.yml` and current shell probes. Native OMP routes were
rechecked on 2026-08-01. Standalone peer commands retain their historical
probe dates and require a new command probe before dispatch.

| Provider target | Harness / CLI | Active model id | Dispatch surface | Local probe status |
|---|---|---|---|---|
| `openai-codex` | OMP native provider | `gpt-5.6-luna` | `omp -p --model openai-codex/gpt-5.6-luna --thinking <level>` | available; max sentinel passed 2026-08-01 |
| `openrouter` | OMP through Mint | `deepseek/deepseek-v4-flash-0731` | `omp -p --model openrouter/deepseek/deepseek-v4-flash-0731 --thinking high` | available; high sentinel passed 2026-08-01 |
| `codex` | Standalone Codex CLI | `gpt-5.6-luna` | `codex exec --model gpt-5.6-luna --config model_reasoning_effort="medium"` | historical discovery 2026-06-14; re-probe before dispatch |
| `pi` | Pi coding agent via OpenRouter | `openrouter/moonshotai/kimi-k2.7-code` | `pi -p --no-extensions --provider openrouter --model moonshotai/kimi-k2.7-code --thinking medium` | historical discovery 2026-06-14; re-probe before dispatch |
| `goose` | Goose CLI via OpenRouter | `openrouter/moonshotai/kimi-k2.7-code` | `goose run --provider openrouter --model moonshotai/kimi-k2.7-code --text` | historical discovery 2026-06-14; re-probe before dispatch |
| `opencode` | OpenCode CLI via OpenRouter | `openrouter/moonshotai/kimi-k2.7-code` | `opencode run --model openrouter/moonshotai/kimi-k2.7-code --variant max --format json` | historical discovery 2026-06-14; re-probe before dispatch |
| `claude` | Claude Code CLI | `claude-opus-4-8` | `claude -p --model claude-opus-4-8 --effort medium` | historical discovery 2026-06-14; Fable session route passed 2026-07-08 |
| `agy` | Antigravity CLI | `gemini-3.5-flash` | `agy --dangerously-skip-permissions --print` | historical discovery 2026-06-14 only; current availability unverified; re-probe before dispatch |
| `cursor-agent` | Cursor Agent CLI | `composer-2.5` | `cursor-agent -p --model composer-2.5` | historical discovery 2026-06-14; re-probe before dispatch |
| `grok-build` | xAI Grok Build CLI | `grok-4.5` | `grok --model grok-4.5 --reasoning-effort high -p` | sentinel passed 2026-07-08; re-probe before dispatch |
| `oracle` | Oracle browser consult | `gpt-5.5-pro-browser` | `npx -y @steipete/oracle --engine browser --model gpt-5.5-pro -p` | `npx` available 2026-08-01; browser dry-run last passed 2026-06-16 |
| `manual` | Human/imported evidence | none | manual summary | manual |

Command discovery proves availability only.
A sentinel proves one bounded invocation, not task quality, current billing,
tool-call reliability, or benchmark performance.
Oracle status proves the browser-mode dry-run path only.
The OMP roster defaults forbid Oracle API mode.


## Realtime And Speech Substrate Snapshot

Source: primary provider docs checked on 2026-07-13. This section is factual
input for product boundary decisions; it is not a default-provider policy.

OpenAI:

- Realtime guide positions `gpt-realtime-2.1` for low-latency voice agents and
  `gpt-realtime-whisper` for streaming transcription.
- Realtime conversations support function calling and out-of-band responses
  (`conversation: "none"`), which fits side-channel classification/proposal
  work that should not speak into the main conversation.
- `gpt-4o-transcribe-diarize` supports `diarized_json` speaker-aware segments
  through `/v1/audio/transcriptions`; OpenAI docs state it is not yet supported
  in the Realtime API.
- Sources:
  <https://developers.openai.com/api/docs/guides/realtime>,
  <https://developers.openai.com/api/docs/guides/realtime-conversations>,
  <https://developers.openai.com/api/docs/guides/speech-to-text#speaker-diarization>.

Google Gemini:

- Gemini Live API supports low-latency realtime voice/vision interactions,
  tool use, and audio transcriptions. Its general capability guide describes
  proactive audio and affective dialogue, but the Gemini 3.1 Flash Live model
  page says neither is supported by that model; asynchronous function calling
  is also not supported there.
- Gemini model docs list Gemini 3.1 Flash Live Preview for high-quality
  low-latency audio-to-audio dialogue and Gemini 2.5 Flash Live Preview for
  low-latency bidirectional voice/video agents with native audio reasoning.
- Sources:
  <https://ai.google.dev/gemini-api/docs/live-api>,
  <https://ai.google.dev/gemini-api/docs/models>,
  <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview>.

Deepgram:

- Flux is positioned as conversational speech recognition for voice agents with
  model-integrated end-of-turn detection and configurable turn-taking dynamics.
  Deepgram documents `flux-general-en` and the ten-language
  `flux-general-multi`, plus `EagerEndOfTurn` / `TurnResumed` events for
  speculative response generation and cancellation.
- Sources: <https://developers.deepgram.com/docs/flux/quickstart>,
  <https://developers.deepgram.com/docs/flux/configuration>.

ElevenLabs:

- Scribe v2 supports speech recognition across 90+ languages, word timestamps,
  dynamic audio tagging, and speaker diarization up to 32 speakers.
- Scribe v2 Realtime is documented for realtime low-latency transcription,
  90+ languages, and word-level timestamps. ElevenLabs' current Realtime page
  says speaker diarization is not a priority for the realtime model, so the
  batch model's speaker labels must not be inferred for Realtime.
- Sources: <https://elevenlabs.io/docs/overview/capabilities/speech-to-text>,
  <https://elevenlabs.io/realtime-speech-to-text>.

For AI-first meeting products, deterministic code should own approval, policy,
event logs, sandboxing, schemas, and evals. Shape semantic proposal generation,
speech understanding, and diarization against the model/provider capability
surface first. Use deterministic heuristics only as explicit fallback or
fixture paths.

## Substrate Assessment Addendum

Source: primary project documentation and repositories checked on 2026-07-13.

Factual substrate distinctions to preserve in composition design:

- OpenCode exposes a client/server architecture, an HTTP/OpenAPI server, a generated
  SDK, sessions, built-in and custom tools, MCP servers, and configurable tool
  permissions. Sources: <https://opencode.ai/docs/server/>,
  <https://opencode.ai/docs/tools/>, <https://opencode.ai/docs/mcp-servers/>.
- Goose ships desktop, CLI, and API surfaces; recipes are portable YAML
  workflows; its documented extension surface uses MCP; and it supports
  subagents, multiple model providers, tool permissions, and sandbox mode.
  Source: <https://block.github.io/goose/>.
- Pi provides a multi-provider LLM API, agent core, TUI, coding-agent CLI,
  SDK, JSON/RPC modes, tree sessions, extensions, and skills. Its official
  README states that it has no built-in permission system and runs with the
  launching process's permissions by default. Sources:
  <https://github.com/earendil-works/pi>,
  <https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md>,
  <https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md>.
- OMP is a Pi fork with built-in LSP and DAP operations, subagents, and optional
  worktree or FUSE-backed task isolation. Sources:
  <https://github.com/can1357/oh-my-pi>,
  <https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/DEVELOPMENT.md>.
- OpenHands provides an SDK, CLI, local GUI, cloud product, and Agent Server.
  Its workspace abstraction covers local processes, containers, and remote
  servers, while remote Agent Servers are documented for Kubernetes, VMs,
  on-premises, or cloud deployment. Sources:
  <https://github.com/OpenHands/OpenHands>,
  <https://github.com/OpenHands/software-agent-sdk>,
  <https://docs.openhands.dev/sdk/arch/workspace>,
  <https://docs.openhands.dev/sdk/guides/agent-server/overview>.
- Continue's official docs describe its 2.0.0 release as final and its
  repository as no longer actively maintained and read-only; the same docs
  retain CLI, VS Code, and JetBrains surfaces. Source:
  <https://docs.continue.dev/>.

The security boundary is external to every row above: do not put model-provider
keys or GitHub write credentials inside a sandbox that can execute
repository-controlled code.

Kimi K2.7 Code sentinel dispatch receipts on 2026-06-14:

- Pi: `efd464ab-bed2-465c-9a89-b644822733ae`, succeeded after roster command
  added `--no-extensions`.
- Goose: `4f0b6928-7abc-4080-a0cb-1b195a7dd74a`, succeeded.
- OpenCode: `9601cf81-428f-4718-980f-15ee161b7b6e`, succeeded.

## Focused Lane Harness Projection

Compose a narrow lane as an OMP agent definition (`.omp/agents/<name>.md`,
project or user scope) or as an explicit
`agent(prompt, agent=..., model=...)` call. Promote recurring compositions to
a declared agent in omp-config.

The selected Harness owns execution. omp-config owns declarations and
ephemeral projection only. Powder owns durable work evidence. omp-config writes
a bounded local dispatch receipt. A failed provider returns evidence to the
lead. The lead decides whether to replace the lane.

## Open-Model / OpenRouter Catalog Snapshot

Pi, Goose, and OpenCode can attempt OpenRouter model ids through their
configured dispatch surfaces. The table retains earlier dated catalog
snapshots and adds current rows read through the Mint-brokered OpenRouter
catalog/API plus `omp models` on 2026-08-01.
A row does not mean that every harness smoke-tested the model. It is not a
recommendation. Record a delegation receipt before treating a non-roster model
as locally proven. OpenRouter rows describe OpenRouter listings only. Do not
infer local Codex, Claude Code, Antigravity, Cursor, or Grok CLI pricing or
limits from them. `~...latest` ids are OpenRouter catalog aliases. Detailed
sections below add source notes for selected rows. This table is the scannable
catalog snapshot.

| OpenRouter id | Created | Context | Max completion | Input | Output | Cache read | Modalities | Supported parameters excerpt |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `x-ai/grok-4.5` | 2026-07-08 | 500,000 | unknown | `$2.00/M` | `$6.00/M` | `$0.50/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning`, `response_format` |
| `anthropic/claude-sonnet-5` | 2026-06-30 | 1,000,000 | 128,000 | `$2.00/M` | `$10.00/M` | `$0.20/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `z-ai/glm-5.2` | 2026-06-16 | 1,048,576 | 128,000 | `$0.42/M` | `$1.32/M` | `$0.078/M` | text -> text | `tools`, `tool_choice`, `parallel_tool_calls`, `structured_outputs`, `reasoning`, `reasoning_effort` |
| `google/gemini-3.6-flash` | unknown | 1,048,576 | 65,536 | `$1.50/M` | `$7.50/M` | `$0.15/M` | text+image -> text | `reasoning`, `reasoning_effort` |
| `google/gemini-3.5-flash-lite` | unknown | 1,048,576 | 65,536 | `$0.30/M` | `$2.50/M` | `$0.03/M` | text+image -> text | `reasoning`, `reasoning_effort` |
| `moonshotai/kimi-k2.7-code` | 2026-08-01 | 262,144 | 262,144 | `$0.73/M` | `$3.50/M` | `$0.15/M` | text+image -> text | `tools`, `tool_choice`, `parallel_tool_calls`, `structured_outputs`, `reasoning`, `reasoning_effort` |
| `anthropic/claude-fable-5` | 2026-06-09 | 1,000,000 | 128,000 | `$10.00/M` | `$50.00/M` | `$1.00/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `qwen/qwen3.7-plus` | 2026-06-03 | 1,000,000 | 65,536 | `$0.32/M` | `$1.28/M` | `$0.064/M` | text+image -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `minimax/minimax-m3` | 2026-05-31 | 1,048,576 | 512,000 | `$0.30/M` | `$1.20/M` | `$0.06/M` | text+image+video -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `anthropic/claude-opus-4.8` | 2026-05-27 | 1,000,000 | 128,000 | `$5.00/M` | `$25.00/M` | `$0.50/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `qwen/qwen3.7-max` | 2026-05-21 | 1,000,000 | 65,536 | `$1.25/M` | `$3.75/M` | `$0.25/M` | text -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `x-ai/grok-build-0.1` | 2026-05-20 | 256,000 | unknown | `$1.00/M` | `$2.00/M` | `$0.20/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `x-ai/grok-4.3` | 2026-04-30 | 1,000,000 | unknown | `$1.25/M` | `$2.50/M` | `$0.20/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `openai/gpt-5.5` | 2026-04-24 | 1,050,000 | 128,000 | `$5.00/M` | `$30.00/M` | `$0.50/M` | file+image+text -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `deepseek/deepseek-v4-pro` | 2026-04-24 | 1,048,576 | 384,000 | `$0.435/M` | `$0.87/M` | `$0.003625/M` | text -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `deepseek/deepseek-v4-flash-0731` | unknown | 1,048,576 | 384,000 | `$0.14/M` | `$0.28/M` | `$0.0028/M` | text -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `openai/gpt-5.6-luna` | unknown | 1,050,000 | 128,000 | `$0.10/M` | `$0.60/M` | `$0.01/M` | text+image -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `moonshotai/kimi-k2.6` | 2026-04-20 | 262,144 | 262,144 | `$0.65/M` | `$3.41/M` | `$0.14/M` | text+image -> text | `tools`, `tool_choice`, `parallel_tool_calls`, `structured_outputs`, `reasoning` |
| `z-ai/glm-5.1` | 2026-04-07 | 202,752 | 128,000 | `$0.966/M` | `$3.036/M` | `$0.1794/M` | text -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `x-ai/grok-4.20` | 2026-03-31 | 2,000,000 | unknown | `$1.25/M` | `$2.50/M` | `$0.20/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `minimax/minimax-m2.7` | 2026-03-18 | 204,800 | 196,608 | `$0.18/M` | `$0.72/M` | unknown | text -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `openai/gpt-5.3-codex` | 2026-02-24 | 400,000 | 128,000 | `$1.75/M` | `$14.00/M` | `$0.175/M` | text+image+file -> text | `tools`, `tool_choice`, `structured_outputs`, `reasoning` |
| `qwen/qwen3-coder-next` | 2026-02-04 | 262,144 | 262,144 | `$0.11/M` | `$0.80/M` | `$0.07/M` | text -> text | `tools`, `tool_choice`, `structured_outputs` |

Live `omp models` readback on 2026-08-01 confirms `moonshotai/kimi-k2.7-code`
with 262,144 context and max completion, `$0.73/M` input, `$3.50/M` output,
and `$0.15/M` cache reads. The catalog also reports minimal, low, medium, and
high reasoning levels. Treat provider catalog values as expiring evidence.

## Verified Model Facts

### Anthropic Claude 5 family (Fable 5 / Mythos 5, Sonnet 5)

- `claude-fable-5`: released 2026-06-09; OpenRouter lists 1M context,
  input `$10.00/M`, output `$50.00/M`, cache read `$1.00/M` (2026-07-08).
  Fable 5 and Mythos 5 are the same underlying model; Fable is the GA lane
  with additional dual-use safety measures, Mythos is approved-organization
  access only. Mythos-class sits above Opus in capability.
- `claude-sonnet-5`: released 2026-06-30; OpenRouter lists 1M context,
  `$2.00/M` in, `$10.00/M` out (2026-07-08); reported intro pricing —
  standard `$3/$15` after 2026-08-31 per pricing coverage (verify at that
  date).
- Local availability: `claude-fable-5` verified live as this machine's
  Claude Code session model on 2026-07-08.
- Sources: https://www.anthropic.com/news/claude-fable-5-mythos-5,
  platform.claude.com pricing docs, OpenRouter catalog readback 2026-07-08.

### Anthropic Claude Opus 4.8

- Active local id: `claude-opus-4-8`.
- Official API id: `claude-opus-4-8`.
- Release: 2026-05-28.
- Provider claim: Anthropic describes Opus 4.8 as its most capable generally
  available model at release.
- Context / output: Anthropic docs state Opus 4.8 supports 1M context on the
  Claude API, Amazon Bedrock, and Vertex AI; Microsoft Foundry lists 200k.
  Docs state 128k max output tokens.
- Platform surface: Anthropic docs state Opus 4.8 supports the same tools and
  platform features as Opus 4.7.
- Source: https://www.anthropic.com/news/claude-opus-4-8 and
  https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6.

### Moonshot Kimi K2.7 Code

- Active local id for Pi, Goose, and OpenCode: `openrouter/moonshotai/kimi-k2.7-code`.
- OpenRouter id: `moonshotai/kimi-k2.7-code`.
- `omp models` readback on 2026-08-01 reports 262,144 context and 262,144
  maximum output tokens, `$0.73/M` input, `$3.50/M` output, and `$0.15/M`
  cache reads.
- OpenRouter modalities: text+image input to text output.
- Reasoning levels: minimal, low, medium, and high.
- OpenRouter supported parameters include `tools`, `tool_choice`,
  `structured_outputs`, `reasoning`, and `reasoning_effort`.
- Older 2026-06-14 and 2026-07-11 snapshots are historical and superseded by
  this 2026-08-01 readback; do not use them for current limits or pricing.
- Source: `omp models` readback on 2026-08-01.

### Moonshot Kimi K2.6

- Retained local variant id: `openrouter/moonshotai/kimi-k2.6`.
- OpenRouter id: `moonshotai/kimi-k2.6`.
- OpenRouter created date: 2026-04-20.
- OpenRouter context length: 262,144 tokens.
- OpenRouter max completion tokens: 262,142.
- OpenRouter pricing on 2026-06-14: input `$0.68/M`, output `$3.41/M`,
  cache read `$0.34/M`.
- OpenRouter modalities: text+image input to text output.
- OpenRouter supported parameters include `tools`, `tool_choice`,
  `parallel_tool_calls`, `structured_outputs`, `reasoning`, and
  `reasoning_effort`.
- Source: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
  `moonshotai/kimi-k2.6` on 2026-06-14.

### Moonshot Kimi K2.5

- Retained local variant id: `openrouter/moonshotai/kimi-k2.5`.
- OpenRouter id: `moonshotai/kimi-k2.5`.
- OpenRouter created date: 2026-01-27.
- OpenRouter context length: 262,144 tokens.
- OpenRouter max completion tokens: 262,144.
- OpenRouter pricing on 2026-06-14: input `$0.375/M`, output `$2.025/M`;
  cache read was not listed in the API row.
- NVIDIA forum reports provider-specific K2.5 deprecation/replacement pressure
  around K2.6. Treat provider behavior as platform-specific until verified.
- Source: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
  `moonshotai/kimi-k2.5` on 2026-06-14, plus
  https://forums.developer.nvidia.com/t/kimi-k2-5-replacement/368480.

### DeepSeek V4 Pro

- Local Pi variant id: `openrouter/deepseek/deepseek-v4-pro`.
- OpenRouter id: `deepseek/deepseek-v4-pro`.
- OpenRouter created date: 2026-04-24.
- OpenRouter context length: 1,048,576 tokens.
- OpenRouter max completion tokens: 384,000.
- OpenRouter pricing on 2026-06-14: input `$0.435/M`, output `$0.87/M`,
  cache read `$0.003625/M`.
- OpenRouter modalities: text input to text output.
- OpenRouter supported parameters include `tools`, `tool_choice`,
  `structured_outputs`, and `reasoning`.
- DeepSeek docs list `deepseek-v4-pro` with 1M context and pricing details;
  prior discount notes may have changed, so verify live before quoting
  non-OpenRouter prices.
- Source: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
  `deepseek/deepseek-v4-pro` on 2026-06-14, and
  https://api-docs.deepseek.com/quick_start/pricing.

### DeepSeek V4 Flash 0731

- First-party DeepSeek scope: the July 31, 2026 public beta uses API name
  `deepseek-v4-flash`. `DeepSeek-V4-Flash-0731` is the deployed version name,
  not a DeepSeek-direct API alias with the `-0731` suffix. It keeps the preview
  architecture and size, uses only re-post-training, upgrades only Flash, and
  adds the native Responses API and Codex adaptation.
- First-party DeepSeek API scope: the pricing page lists 1M context, 384K
  maximum output, JSON and tool calls, 2,500 concurrency, `$0.0028/M`
  cache-hit input, `$0.14/M` cache-miss input, and `$0.28/M` output for
  `DeepSeek-V4-Flash-0731`.
- Official model-card scope: DeepSeek V4 Flash 0731 supports low, high, and
  max effort. Reported scores are Terminal Bench 2.1 82.7, NL2Repo 54.2,
  Cybergym 76.7, DeepSWE 54.4, Toolathlon Verified 70.3, Agents' Last Exam
  25.2, AutomationBench Public 25.1, DSBench-FullStack 68.7, and DSBench-Hard
  59.6. Public code-agent tasks used an unreleased DeepSeek Harness minimal
  mode at max effort; DSBench-FullStack and DSBench-Hard are internal sets.
- OpenRouter scope: the current Mint-brokered catalog row is
  `deepseek/deepseek-v4-flash-0731` with 1,048,576 context, 384K maximum
  output, `$0.14/M` input, `$0.28/M` output, `$0.0028/M` cache reads, text-only
  input, reasoning, tools, and structured outputs (catalog read on 2026-08-01).
- Local OMP scope: the pinned route is
  `openrouter/deepseek/deepseek-v4-flash-0731:high`, and local metadata exposes
  high only.
- A representative bounded repository-read probe on 2026-08-01 used only the
  exact route `openrouter/deepseek/deepseek-v4-flash-0731:high`, the `read` and
  `grep` tools, and a repository task reading `global/config.yml`; it
  successfully extracted the exact `smol`, `task`, `vision`, and `commit`
  bindings. This bounded probe does not prove all workloads.
- A local high sentinel passed on 2026-08-01. First-party weights and API
  support low/high/max, but a max request returned correctly and may have
  been clamped; do not claim local max support.
- Independent evaluation scope: Artificial Analysis reports Intelligence Index
  50 for DeepSeek V4 Flash 0731 at max effort. This is near-parity evidence,
  not local task-quality proof; evaluation methodology and transfer to this
  harness remain unverified. Source:
  https://artificialanalysis.ai/models/deepseek-v4-flash.
- Sources: https://api-docs.deepseek.com/updates/,
  https://api-docs.deepseek.com/quick_start/pricing, and
  https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731.

### MiniMax M3

- Local open-model variant id: `openrouter/minimax/minimax-m3`.
- OpenRouter id: `minimax/minimax-m3`.
- OpenRouter created date: 2026-05-31.
- OpenRouter context length: 1,048,576 tokens.
- OpenRouter max completion tokens: 512,000.
- OpenRouter pricing on 2026-06-14: input `$0.30/M`, output `$1.20/M`,
  cache read `$0.06/M`.
- OpenRouter modalities: text+image+video input to text output.
- OpenRouter supported parameters include `tools`, `tool_choice`,
  `structured_outputs`, and `reasoning`.
- Source: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
  `minimax/minimax-m3` on 2026-06-14.

### Qwen3 Coder Next

- Local open-model variant id: `openrouter/qwen/qwen3-coder-next`.
- OpenRouter id: `qwen/qwen3-coder-next`.
- OpenRouter created date: 2026-02-04.
- OpenRouter context length: 262,144 tokens.
- OpenRouter max completion tokens: 262,144.
- OpenRouter pricing on 2026-06-14: input `$0.11/M`, output `$0.80/M`,
  cache read `$0.07/M`.
- OpenRouter modalities: text input to text output.
- OpenRouter supported parameters include `tools`, `tool_choice`,
  and `structured_outputs`.
- Source: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
  `qwen/qwen3-coder-next` on 2026-06-14.

### Z.ai GLM 5.2

- Candidate id: `openrouter/z-ai/glm-5.2` — supersedes 5.1 as the current
  GLM lane candidate.
- OpenRouter id: `z-ai/glm-5.2`; created 2026-06-16; context 1,048,576;
  max completion 128,000; pricing on 2026-07-08: input `$0.42/M`, output
  `$1.32/M`, cache read `$0.078/M`; text -> text; supports `tools`,
  `tool_choice`, `parallel_tool_calls`, `structured_outputs`, `reasoning`,
  `reasoning_effort`.
- Source: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
  `z-ai/glm-5.2` on 2026-07-08.

### Z.ai GLM 5.1

- Candidate id: `openrouter/z-ai/glm-5.1`.
- OpenRouter id: `z-ai/glm-5.1`.
- OpenRouter created date: 2026-04-07.
- OpenRouter context length: 202,752 tokens.
- OpenRouter pricing on 2026-06-14: input `$0.98/M`, output `$3.08/M`,
  cache read `$0.182/M`.
- OpenRouter modalities: text input to text output.
- OpenRouter supported parameters include `tools`, `tool_choice`,
  `parallel_tool_calls`, `structured_outputs`, `reasoning`, and
  `reasoning_effort`.
- Source: `curl -fsSL https://openrouter.ai/api/v1/models` filtered to
  `z-ai/glm-5.1` on 2026-06-14.

### xAI Grok 4.5

- Released 2026-07-08 (public API 2026-07-09 per launch coverage); not
  available in the EU until mid-July per the same coverage.
- Active local id: `grok-4.5` — the Grok Build CLI's default model
  (`grok models` readback, 2026-07-08).
- OpenRouter id: `x-ai/grok-4.5`; created 2026-07-08; context 500,000
  (xAI direct and OpenRouter agree); pricing input `$2.00/M`, output
  `$6.00/M`, cache read `$0.50/M`; xAI lists a long-context (>200K) tier at
  `$4/$12`. Aliases: `grok-4.5-latest`, `grok-build-latest` (xAI), and
  OpenRouter `~x-ai/grok-latest` tracks it as of 2026-07-08.
- Effort tiers: low/medium/high (default high) — the 4.3-era
  `--effort max --reasoning-effort xhigh` flags do not apply.
- Positioning per launch coverage (provider claim, not local proof):
  Opus-class quality, faster/cheaper/more token-efficient; trained with
  Cursor; #1 on the Harvey Legal Agent Benchmark at release.
- Local sentinel dispatch through Grok Build passed 2026-07-08
  (`grok --model grok-4.5 --always-approve -p` returned the expected
  sentinel).
- Sources: xAI `api.x.ai/v1/language-models` readback,
  `curl -fsSL https://openrouter.ai/api/v1/models`, `grok models`,
  and launch coverage — all 2026-07-08.

### xAI Grok Build CLI (harness facts)

- Local version 0.2.91 (`grok --version`, 2026-07-08); default model
  `grok-4.5`.
- Harness affordances verified from `--help`: `--best-of-n <N>` (parallel
  attempts, best-of selection, headless), `--check` (appended
  self-verification loop, headless), `--agents <JSON>` inline subagent
  definitions plus `--agent <name|file>`, `--json-schema` constrained
  structured output, `--worktree`, plan/permission modes, cross-session
  memory (`grok memory`, `--experimental-memory`).
- Assessment input, not policy: with 4.5 as default this is now a credible
  coding/agentic lane, not just a chat surface — verify per task with a
  sentinel dispatch before relying on it for substantive lanes.

### xAI Grok 4.3

- Local id: `grok-4.3` — retained as a cheaper 1M-context fallback
  (OpenRouter `$1.25/M` in, `$2.50/M` out on 2026-07-08).
- `grok-4.20` / `grok-4.20-multi-agent`: OpenRouter lists 2M context; xAI
  direct lists 1M — treat the discrepancy as unresolved provider drift.
- Source: https://docs.x.ai/developers/models/grok-4 and the OpenRouter
  catalog readback on 2026-07-08.

### OpenAI GPT-5.6 Luna Through Codex and OpenRouter

- Native OpenAI scope: the active local id is `gpt-5.6-luna`. Sibling IDs
  `gpt-5.6-sol` and `gpt-5.6-terra` remain in the local Codex cache; this
  roster selects Luna and does not select Terra.
- OpenAI announcement scope: on 2026-07-30, OpenAI reduced Luna pricing by
  80% to `$0.20/M` input and `$1.20/M` output. Luna remains available in Codex,
  ChatGPT Work, and the API.
- Native OpenAI API scope: the model page lists `$0.20/M` input, `$0.02/M`
  cached input, `$1.20/M` output, and `$0.25/M` cache writes. Inputs above
  272K use 2x input and 1.5x output pricing. The API provides 1.05M context,
  922K maximum input, 128K output, text and image input, reasoning, and broad
  Responses tools.
- OpenRouter scope: the current Mint-brokered catalog row is
  `openai/gpt-5.6-luna` with 1,050,000 context, 128K maximum output,
  `$0.10/M` input, `$0.60/M` output, `$0.01/M` cache reads, and `$0.125/M`
  cache writes (catalog read on 2026-08-01). Keep these provider-specific
  OpenRouter prices distinct from native OpenAI prices.
- Local OMP scope: `omp models` reports 272K effective local context, 128K
  output, low/medium/high/xhigh/max effort, text and image input, and current
  native rates of `$0.20/M` input and `$1.20/M` output. A native Luna max
  sentinel passed on 2026-08-01.
- Independent evaluation scope: Artificial Analysis reports Intelligence Index
  51 for Luna at max effort, 172.1 output tokens per second, and 130M generated
  evaluation tokens. Its comparison with DeepSeek V4 Flash 0731 is near-parity
  evidence, not local task-quality proof; evaluation methodology and transfer
  to this harness remain unverified. Source:
  https://artificialanalysis.ai/models/gpt-5-6-luna.
- Sources: https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/
  and https://developers.openai.com/api/docs/models/gpt-5.6-luna.

### Google Gemini 3.6 Flash and Gemini 3.5 Flash Lite Through OpenRouter

- Current Mint-brokered `omp models` catalog readback on 2026-08-01 reports
  `openrouter/google/gemini-3.6-flash` with 1,048,576 context, 65,536 maximum
  output tokens, text+image input, minimal/low/medium/high reasoning levels,
  `$1.50/M` input, `$7.50/M` output, and `$0.15/M` cache reads.
- A low sentinel for `openrouter/google/gemini-3.6-flash:high` passed on
  2026-08-01.
- The same catalog readback reports
  `openrouter/google/gemini-3.5-flash-lite` with 1,048,576 context, 65,536
  maximum output tokens, text+image input, minimal/low/medium/high reasoning
  levels, `$0.30/M` input, `$2.50/M` output, and `$0.03/M` cache reads.
- A low sentinel for `openrouter/google/gemini-3.5-flash-lite` passed on
  2026-08-01.

### Historical Google Gemini 3.5 Flash Through Antigravity

- Historical local id recorded on 2026-06-14: `gemini-3.5-flash`.
- Historical 2026-07 coverage reported GA since I/O 2026; `$1.50/M` input,
  `$9.00/M` output, 1M context, and native Search grounding.
- Gemini 3.5 Pro was not GA in that historical 2026-07 coverage; it surfaced
  through Antigravity/LMArena testing without an official model card or pricing.
- These Antigravity records are historical only and do not establish current
  availability; re-probe before dispatch.
- Sources: 2026-07 coverage (tokenmix.ai, VentureBeat); verify against
  `ai.google.dev` model docs before changing a default.

### Cursor Composer 2.5

- Active local id: `composer-2.5`.
- Local dispatch surface: Cursor Agent CLI `cursor-agent -p --model composer-2.5`.
- Source for local availability: `global/models.yml` plus a direct
  `cursor-agent --version`/headless smoke on 2026-06-07.
- Public model-card/pricing/context facts were not verified in this refresh.
  Do not infer pricing, context, or benchmark facts from the local model id.

## Refresh Procedure

Use `/harness-engineering models` or `/research` when this file is stale or
when a user asks for current model/provider/harness choices.

1. Read `global/models.yml`, harness settings, and this file.
2. Probe local providers with `command -v` and the provider's documented
   non-billable version/help command. Use a bounded sentinel only when needed.
3. Query live provider catalogs/docs for exact model ids, context windows,
   max output, pricing, tool support, release dates, and deprecation notes.
4. Update this file with hard facts only.
5. Update omp-config model settings only when you change a runnable default or
   variant.
6. Run omp-config `bin/check` and the affected provider's direct smoke probe.

Do not add subjective labels such as role fit, taste, or task suitability to
this file. Put task-specific composition rationale in the run's receipts,
context packet, or final debrief.
