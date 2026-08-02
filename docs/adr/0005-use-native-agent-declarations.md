# ADR 0005: Use native agent declarations for dispatch

- Status: Accepted
- Date: 2026-08-01

## Context

OMP 17.2.3 can dispatch named agent declarations through the native `task` tool.
Each declaration owns an ordered model ladder, one reasoning level, one tool envelope, one skill bundle, and one child allowlist.
The native spawn API cannot change those fields for one task.
A separate process protocol can provide per-call selection, but it duplicates OMP lifecycle, validation, receipts, and concurrency.
That duplication increased failure surface and prompt overhead without improving the normal dispatch path.

## Decision

Keep five broad native agents: `architect`, `builder`, `verifier`, `researcher`, and `designer`.
Keep `qa-user` and `qa-user-leaf` only for the required persona QA depth.
Dispatch all other work directly from the chief through native `task`.
Keep task-specific methods and hidden skill names in the task brief.
Keep every broad agent child allowlist empty.
Do not add a scheduler, process wrapper, generated agent, or task-specific declaration for model selection.
Accept the declared model ladder and authority envelope as the native runtime contract.
Let the authored `designer` declaration shadow OMP's bundled declaration in the global runtime.
Disable the bundled `designer` in sealed launches unless the authored declaration is copied into the allowlist.

## Consequences

The runtime uses OMP lifecycle, concurrency, cancellation, receipts, and agent discovery without a second protocol.
The roster stays small while task briefs can select specialist methods.
Per-task model, tool, and skill overrides are unavailable.
A model fallback provides availability resilience only; it does not provide an independent review.
The chief must use a fresh `verifier` lane when the risk requires independent evidence.

## Reversal condition

Reconsider this decision only when OMP exposes an in-process spawn API with validated per-call model, authority, skill, tool, MCP, receipt, and lifecycle controls.
The replacement must reduce total concepts and preserve native task supervision.
