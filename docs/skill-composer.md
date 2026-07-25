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

The proof mapping uses real skill declarations read from `global/skills/`:

- `orchestrator` = `research` + `dispatch` (A+B)
- `magellan` = `project-engineering` only (lane C)
- `builder` = `dispatch` + `powder` (lane BD)

A real OMP-rendered `<skills>` block is captured in
`tests/fixtures/real-orchestrator-skills.txt` from a live session. It confirms
OMP renders multi-line descriptions (folded YAML scalars) with blank lines
between entries — the parser handles this shape, not a hand-written
approximation.

The focused test (`tests/skill-composer.test.ts`) asserts the **exact** rewritten
`<skills>` block equals the expected set for each lane (not just `toContain`),
proving subtraction: lane C's block contains `project-engineering` only and
omits the orchestrator's `research`/`dispatch` descriptions.

## Prompt-cache impact

The cache test records both datapoints:

- **No-rewrite baseline**: composition disabled (no manifest) — `beforeBytes`
  equals `afterBytes`, delta = 0.
- **Rewritten**: composition enabled — `afterBytes` < `beforeBytes`; the delta
  is the cache-prefix cost of the smaller composed prompt.

A smaller rewritten request is the measured cache-prefix benefit; the unchanged
request is the no-composition baseline.

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
actual feature request is documented in
`docs/upstream-skill-composition-request.md` and must be filed against
`can1357/oh-my-pi` with the title: "Stable declared-agent identity + exact
per-spawn skill allowlist (addition and subtraction)".

**Filing status:** This document IS the feature request. It must be filed as a
GitHub issue on `can1357/oh-my-pi` and linked here once filed. The local
extension is deleted when OMP exposes the contract above.
