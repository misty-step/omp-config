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

## Olympus simple operational cutover (2026-08-04)

- Do not replace a deleted subsystem with another queue, ledger, receipt, wrapper, or configuration path.
- Do not remove preproduction, combine agent hosts, or weaken exact-revision, authority, credential, budget, drain, or durability gates.
- Keep Habitat auto-selection, owner assignment, cooldown, and daily-cap behavior while removing runtime policy editing.
- Never await Asclepius from the Argus execution path. Route persisted review results through independent reconciliation.
- Dispatch CI repair only for the current open `auto/*` head with a current failed check and trusted repository authority.
- Keep GitHub as pull-request and merge authority. Do not duplicate branch protection or required-check policy in another store.
- Prove every agent on its own Sprite in preproduction before exact-digest production promotion.
- Require a net reduction in lines, modules, tables, jobs, or dependencies. Reject compensating growth.
