# ADR 0001: Own first-party primitives locally

- Status: Accepted
- Date: 2026-07-29

## Context

`omp-config` used sibling `file:` packages for `research-core`, `deliver-core`, and `qa-users`.
A new checkout needed two sibling repositories before installation could succeed.
The operator chose one repository as the current authority.
A later extraction can occur after another harness needs the same stable contract.

## Decision

`omp-config` owns all three primitives as real directories under `global/skills/`.
The package manifest has no sibling `file:` dependencies.
The installer has no sibling preflight step.
The source gate verifies local ownership and the `qa-users` integrity contract.
OMP-specific agents and routes remain in this repository.

## Consequences

A standalone checkout can install and verify without sibling repositories.
One commit can change a primitive and its OMP adapter together.
Other harnesses do not receive these changes automatically.
Future extraction must preserve the local skill contract and add explicit consumer adapters.

## Reversal condition

Extract a harness-neutral package when two active harnesses need the same stable primitive and local ownership causes repeated divergence.
