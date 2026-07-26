# Per-agent skill composition prototype

`global/extensions/skill-composer.ts` is a temporary OMP extension. It uses an
explicit identity marker emitted by the declared agent prompt and the adjacent
`global/skill-composer-manifest.json` allowlist. The provider hook rewrites only
the canonical `<skills>` metadata block; unknown agents, missing manifests, and
shape drift return the original provider payload unchanged. Shape drift is
reported as `skill composer: prompt-shape drift: ...`.

Drift and unknown-agent paths fail closed: the original provider payload is
preserved byte-for-byte and the full additive skill index remains in place.
This is an allowlist bypass in practice — composition is disabled, not
narrowed — so drift must be treated as an operational signal, not a silent
skip. The hook logs every drift to `pi.logger.error`.

## Live proof

The composition wire contract is proven against a **real captured OMP payload**,
not a reconstruction. The carrier in `tests/fixtures/live-orchestrator-instructions.txt`
is the actual `instructions` string OMP 17.1.x emitted at `before_provider_request`
during an `omp -p` session (openrouter carrier, `PI_CODING_AGENT_DIR` pointed at
this repo's `global/`). It contains the real orchestrator identity marker and the
real multi-line `<skills>` block. The `live-captured orchestrator carrier composes
on the real wire` test feeds that carrier through `composeProviderRequest` and
asserts the marker is stripped and the block is narrowed to the manifest set.

The proof mapping uses real skill declarations read from `global/skills/`:

- `orchestrator` = `research` + `dispatch` (A+B)
- `magellan` = `project-engineering` only (lane C)
- `builder` = `dispatch` + `powder` (lane BD)

### Provider carrier shapes

OMP emits different system-prompt carriers per provider family (verified from
the OMP 17.1.x source and the live capture):

| Provider family | Carrier field | Shape |
| --- | --- | --- |
| OpenAI / OpenRouter (responses) | `instructions` | `string` (joined systemPrompt) |
| Anthropic | `system` | `[{text: chunk}, ...]` — multi-element, no `type` field |
| Gemini | `systemInstruction` | `{parts: [{text}, ...]}` — multi-element |
| Pre-format | `systemPrompt` | `string` or `string[]` |

The composer scans **every element** of every carrier field, finds the single
element carrying the identity marker, and rewrites only that element. A
multi-element Anthropic `system` array (one `{text}` per cache-breakpoint chunk)
is composed correctly: the marked chunk is rewritten and every other chunk is
preserved byte-for-byte. The `multi-element Anthropic system array carrier is
composed` and `Gemini systemInstruction multi-part carrier is composed` tests
defend this.

## Prompt-cache impact

Both datapoints are measured against real payloads:

- **Live orchestrator** (real captured `instructions` carrier, composition on):
  78414 → 78368 bytes (Δ 46). The delta is near-zero because the orchestrator's
  visible skills already match the manifest — composition only strips the marker
  and reorders. This is the honest baseline: composition is a no-op for an agent
  whose additive index already equals its allowlist.
- **Builder lane** (5 autoloadSkills `deliver,ci,powder,factory-apps,research`
  narrowed to manifest `dispatch,powder`, real descriptions): 2112 → 723 bytes
  (Δ 1389, 65.8% smaller). This is the subtraction cache-prefix saving: the
  narrowed prompt is a shorter cache prefix, so a higher share of the prefix
  hits the provider's prompt cache on subsequent turns.

The no-rewrite baseline (composition disabled via absent manifest) records
`beforeBytes === afterBytes`, Δ 0. The byte delta is the cache-prefix cost/benefit
of composition; cached-token deltas and hit rates require a real multi-turn
session with cache headers, which this offline prototype does not record.

## Upstream feature request

The deletion condition for this extension is an upstream OMP contract that
provides:

1. A **stable declared-agent identity** at `before_provider_request` — not
   inferred from prompt text.
2. An **exact per-spawn skill allowlist** on `AgentDefinition` that supports
   both addition and subtraction (not just additive `autoloadSkills`).
3. A **per-spawn `skills` parameter** so each spawn can override the agent's
   default allowlist.

The previously-linked issue #1334 is the closed `autoloadSkills` frontmatter
feature (additive loading only) and does **not** request this contract. The
actual feature request is staged in `docs/upstream-skill-composition-request.md`.

**Filing status:** stage rules forbid running `gh` from a Hatchet stage, so the
request cannot be filed as a GitHub issue from here. The complete, ready-to-file
request lives in `docs/upstream-skill-composition-request.md`; the workflow or
card owner must file it against `can1357/oh-my-pi` with the title "Stable
declared-agent identity + exact per-spawn skill allowlist (addition and
subtraction)" and link the issue URL here. The local extension is deleted when
OMP exposes the contract above.
