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

## Harness census live execution (2026-08-09)

- **Requested identity as outcome:** Do not treat a requested model as observed output. Require a parsed adapter attestation before quality scoring.
- **Reliability leakage:** Do not score reliability failures or retry policy refusals. Require an unresolved capability result and a non-retryable refusal.
- **Comparison identity corruption:** Do not pair arms by row bytes, task count, or shifted database columns. Compare the shared task digest in both tables.
- **Wrong freeze boundary:** Freeze runtime packages, images, adapters, and task inputs. Exclude mutable workspaces, results, and ledgers from stage identity.
- **Unsafe resume:** Do not rerun a pending task from a modified workspace. Verify its frozen source identity before provider work.
- **Claimed authority:** Do not record network or credential controls that the live worker did not use. Probe the launched container and stored configuration.
- **Premature baseline:** Do not resolve a native baseline before all selected task receipts agree. Do not create receipts for unselected tasks.
- **Split ledger:** Do not let an implicit run database compete with the campaign ledger. Require one canonical receipt store.
- **Runtime identity drift:** Do not accept loose version text, unsupported provider entries, or mid-campaign model changes. Keep one reliability taxonomy and refuse drift.