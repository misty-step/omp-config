# Upstream feature request: stable declared-agent identity + exact per-spawn skill allowlist

Filed upstream as [can1357/oh-my-pi#4570](https://github.com/can1357/oh-my-pi/issues/4570), this document records the exact contract requested from OMP. The filed issue tracks per-role context filtering; this proposal names the structured identity and per-spawn override needed to make the boundary exact.

## Problem

OMP's `autoloadSkills` frontmatter on `AgentDefinition` is **additive only**:
each declared agent inherits the shared visible skill index plus its
`autoloadSkills` list. There is no mechanism to **subtract** a skill from a
specific agent's prompt, so a specialist lane cannot drop a core skill that
the orchestrator needs but the lane should not see.

The local `skill-composer` extension works around this by rewriting the
`<skills>` block in the provider request at `before_provider_request`. It
identifies the agent via a `<!-- omp-composition-agent: name -->` marker in
the prompt text — a fragile seam, since the marker is free text unbound to the
agent's frontmatter `name:`. This is a prototype; the upstream contract should
make it unnecessary.

## Requested contract

1. **Stable declared-agent identity at `before_provider_request`.** The
   extension hook must receive the active declared agent's `name` (from
   frontmatter) as a structured field, not inferred from prompt text. This
   eliminates the identity-marker workaround and the silent-failure risk when
   a marker goes stale.

2. **Exact per-spawn skill allowlist on `AgentDefinition`.** A field like
   `skills: string[]` (distinct from additive `autoloadSkills`) that defines
   the **exact** set of skills rendered in the agent's `<skills>` block. Skills
   not in this list are subtracted from the prompt, not merely hidden from
   model invocation. This supports both addition and subtraction.

3. **Per-spawn `skills` parameter.** The `task`/spawn API should accept a
   `skills` override so each spawn can narrow the agent's default allowlist
   for that specific composition, without mutating the declared agent.

## Deletion condition for the local extension

When OMP exposes all three of the above, `global/extensions/skill-composer.ts`,
`global/skill-composer-manifest.json`, and the `<!-- omp-composition-agent -->`
markers in agent prompts are deleted. The composition contract moves to
declared agent frontmatter and per-spawn parameters.

## Why #1334 is insufficient

Issue #1334 is the closed `autoloadSkills` frontmatter feature — additive
loading. It does not request subtraction, stable identity, or per-spawn
overrides.
