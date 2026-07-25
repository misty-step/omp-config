# Per-agent skill composition prototype

`global/extensions/skill-composer.ts` is a temporary OMP extension. It uses an
explicit identity marker emitted by the declared agent prompt and the adjacent
`global/skill-composer-manifest.json` allowlist. The provider hook rewrites only
the canonical `<skills>` metadata block; unknown agents, missing manifests, and
shape drift return the original provider payload unchanged. Shape drift is
reported as `skill composer: prompt-shape drift: ...`.

The proof mapping uses real declarations:

- `orchestrator` = `research` + `dispatch` (A+B)
- `magellan` = `project-engineering` only (lane C)
- `builder` = `dispatch` + `powder` (lane BD)

The focused test records byte counts before and after rewriting. A smaller
rewritten request is the measured cache-prefix cost; the unchanged request is
the no-composition baseline.

Upstream tracking: [oh-my-pi issue #1334](https://github.com/can1357/oh-my-pi/issues/1334).
The local extension is deleted when OMP exposes a stable declared-agent identity
at `before_provider_request` together with an exact per-spawn skill allowlist
that supports both addition and subtraction. Until then, this extension fails
closed rather than guessing from prompt text.
