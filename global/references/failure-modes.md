# Critic Failure Modes

Use this reference when no narrower skill reference owns the failure modes. Add task-specific modes to the relevant skill reference when one exists.

## General modes

- **Unnamed risk:** Work starts without general and task-specific failure modes.
- **Inline-only avoidance:** Negative instructions stay in a prompt and disappear after the task.
- **Self-approval:** The producer treats confidence, a summary, or a passing local check as independent evidence.
- **Weak critic scope:** A critic repairs, broadens scope, or reviews a different artifact instead of hunting named violations.
- **Unsupported finding:** A critic reports a concern without a location, oracle, reproduction, or other checkable evidence.
- **Additive bias:** The work adds wrappers, abstractions, fallbacks, comments, tests, or process without removing obsolete material.
- **Compensating growth:** A deletion triggers a larger replacement system even though observable behavior stays the same.
- **Protocol duplication:** A new review workflow duplicates an existing routing or review protocol.

## Task-specific prompts

Name only the modes that can affect the current product.

- **Communication:** unsupported claims, missing decisions, buried actions, or ambiguous ownership.
- **Plan:** missing dependencies, unowned steps, absent oracle, or no stop condition.
- **Design:** leaked boundaries, unnecessary concepts, unmeasured tradeoffs, or missing failure behavior.
- **Code:** broken invariants, untested paths, trust-boundary errors, dead scaffolding, or stale callers.
- **Review:** missed changed paths, weak evidence, scope drift, or an unverified finding.

## Erasure angle

Include erasure in every critic brief. Ask: “What can be deleted while preserving observable behavior?”

- Check code, concepts, wrappers, fallbacks, comments, tests, docs, rules, and process steps.
- Measure the applicable before-and-after change with token count or AST node count, or measure it against a line budget.
- Treat the metric as evidence, not as a substitute for behavior proof.
- The primary agent inspects for compensating additions after each deletion and removes them when behavior remains preserved.
- Use `global/references/delete-first.md` for the broader deletion and simplification sequence.

## exe.dev agent skill (2026-08-10)

- Add an MCP server or wrapper CLI even though exe.dev defines SSH as its API.
- Put exe.dev guidance in always-loaded `AGENTS.md` instead of one model-invoked skill.
- Trigger on quoted or comparative mentions, or leave the skill enabled in no-operations presets.
- Vendor the upstream skill without a declared license and immutable registry receipt.
- Treat account authentication as mutation authority or bypass Estate's typed artifact when it owns the action.
- Copy credentials to a VM or allow direct control-plane HTTPS proof outside Mint.
- Accept an unknown host key, forward an SSH agent by default, or select an unintended local identity.
- Invent flags, parse terminal prose, or select a VM without one exact `.vms[].vm_name` match.
- Change a VM, account, integration, support grant, sharing rule, or attachment scope without exact authority.
- Erasure failure: duplicate the remote docs catalog or add configuration, agents, tools, and process beyond the routed skill.