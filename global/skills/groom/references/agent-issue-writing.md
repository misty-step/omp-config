# Agent-Ready Issue Writing

## Principle

Treat the issue as a prompt for a senior coding agent.
Give the agent its goal, local context, quality bar, and boundaries.
Do not replace judgment with a rigid step-by-step script.

## What to include

### Problem

State what is wrong or missing. Add concrete evidence when available.

### Outcome

State what must be true when the issue is done.

### Context

Include only the context needed to make good decisions:
- user workflow
- architecture seam
- existing patterns
- relevant linked issues or docs

Use domain names and behavioral contracts before file paths.
Paths are touchpoints, not the source of truth; they go stale faster than the behavior.

### Acceptance criteria

Write criteria that map to tests, commands, or visible behaviors.
Use these good tags:
- `[behavioral]`
- `[test]`
- `[command]`

### Boundaries

Say what must not change. This is often more valuable than extra implementation steps.

### Verification

Provide runnable commands when possible.

### Touchpoints

List likely files, modules, routes, tests, or data paths when known.
Treat them as starting points, not fixed limits.

### Agent Autonomy

Label the expected execution mode when it matters:

- **AFK:** The issue has a full specification, an executable or inspectable
  oracle, and no new product judgment is needed.
- **HITL:** The issue needs a human decision, credential, design review,
  production access, or external confirmation before implementation can finish
  safely.

Do not mark an issue AFK until the issue body shows its dependencies, boundaries,
and verification.

## What to avoid

- Avoid vague requests such as “clean this up”.
- Avoid tickets with multiple outcomes. An epic with one coherent outcome, an
  oracle, and ordered children is fine. A ticket without done criteria is not.
- Avoid hidden dependencies in comments only.
- Avoid instructions that describe exact shell steps instead of the desired result.
- Avoid “etc”, “as needed”, and other scope leak phrases.
- Avoid acceptance criteria that cannot be observed or tested.
- Avoid stale line-number directives as the only source of truth.
- Avoid AFK labels on work that still needs product or architecture decisions.

## Type-specific guidance

### Bug

Include:
- repro
- expected vs actual
- impact
- regression clues if known

### Feature

Include:
- user or operator value
- triggering surface
- rendering or API constraints
- deterministic facts the model must not invent

### Refactor

Include:
- invariants to preserve
- code smells or coupling to remove
- tests or checks that must stay green

### Research

Include:
- the decision to make
- what evidence to gather
- the expected output artifact
- what counts as sufficient confidence

## Recommended issue skeleton

```md
## Problem

## Outcome

## Context

## Acceptance Criteria
- [behavioral] Given ...
- [test] Given ...
- [command] When `...`, then ...

## Touchpoints
- `path/to/file`

## Verification
```bash
pnpm test ...
pnpm typecheck
```

## Boundaries

## Related
```

## AI-agent modification

Optimize for first-pass execution:
- Prefer one issue per coherent diff.
- Split broad plans into vertical tracer bullets that agents can demonstrate or
  verify independently.
- Keep prompts goal-oriented, not step-prescriptive.
- State deterministic constraints explicitly.
- Separate exploration from implementation when uncertainty is high.
- Rewrite oversized issues before assigning them.

## Sources

- https://developers.openai.com/api/docs/guides/prompt-engineering
- https://developers.openai.com/api/docs/guides/function-calling
- https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/troubleshoot-copilot-coding-agent
