# ADR 0002: Separate root doctrine from child rules

- Status: Accepted
- Date: 2026-07-29

## Context

OMP loads `AGENTS.md` as root context.
Normal task children remove inherited `AGENTS.md` context files.
OMP forwards `RULES.md` rules to those children as `alwaysApply` content.
The old instruction spine mixed root judgment, universal invariants, role methods, and procedures.

## Decision

`global/AGENTS.md` defines the root chief role and engineering doctrine.
`global/RULES.md` contains short invariants that every normal task child must receive.
Agent declarations contain role-specific authority, tools, and evidence contracts.
Skills contain reusable procedures, references, scripts, and fixtures.
Prompt templates contain short workflows that the operator starts.
Extensions and tool policies enforce requirements that prompt text cannot enforce.
Sealed launch prompts include root doctrine and sticky rules as separate sections.

## Consequences

Normal task children receive universal safety and communication rules without the root chief role.
The root keeps integration and final judgment.
A hard child requirement must live in `RULES.md`, an agent declaration, or executable enforcement.
Instruction owners must not duplicate the same contract across these surfaces.

## Reversal condition

Revisit this split if OMP changes task-child context forwarding or provides a sealed, exact composition manifest for each child.
