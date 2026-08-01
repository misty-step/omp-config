---
name: dispatch
description: |
  Compose and supervise focused subagents for substantive work. Select the
  declared role, model/provider/reasoning level, hidden skills, MCPs, tools,
  verifier, and lane contract. Use when work can be delegated, a specialist
  skill is needed, or the operator asks to route, compose, delegate, review,
  investigate, build, verify, or groom. Trigger: /dispatch, /route, /delegate.
argument-hint: "[task|card] [--manifest|--team]"
---

# /dispatch

Keep the chief executive on intent, research, team design, supervision, and integration.
Do not run a specialist workflow in the chief session when a focused lane can own it.

The chief session sees only `research` and `dispatch` from the authored global catalog.
Hidden skills remain technically reachable because OMP visibility is not an access boundary.
Treat that as an implementation limit, not permission.
Load a hidden specialist skill in the chief session only when the operator explicitly invokes it or when you edit that primitive.


## Live authority

Before substantive dispatch:

1. Read `references/model-capabilities.md` for model, provider, and reasoning policy.
2. Read `references/primitive-routing.md` for skill, MCP, tool, and role routes.
3. Use `references/agent-compositions.json` for exact declared-agent bundles.
   `bin/check` rejects drift between this catalog and `global/agents/*.md`.
4. Read the target repository and its work ledger rule before mutation.

Use fallback chains for resilience only.
Never use a fallback chain as a capability ranking or a second opinion.


## Composition rule

Each lane is one intentional composition:

1. **Role** — choose the narrowest declared or bundled agent that owns the work shape.
2. **Model** — choose the provider-native model that best fits the cognitive work.
3. **Reasoning** — choose the lowest level that preserves the required judgment.
4. **Skills** — use the declared `autoloadSkills` bundle plus task-specific hidden
   skills named in the lane brief.
5. **MCPs and tools** — use only the live systems and tool envelope the lane needs.
6. **Contract** — define outcome, authority, scope, oracle, output, dependencies, and
   non-goals.


Use a declared agent when its authority and bundle fit.
Use an ad-hoc task lane for a one-time composition.
Add a declared agent only when the composition recurs or needs a durable authority boundary.

OMP task subagents inherit the session's discovered skill catalog.
OMP does not support a strict per-task skill allowlist.
`autoloadSkills` preloads a focused bundle.
Hidden task-specific skills require an explicit `Read skill://<name> first` instruction.
The pending composer extension must provide true per-agent add-and-subtract catalogs.


## Dispatch procedure

1. Classify each independent slice as architecture, implementation, research,
   review, verification, incident, backlog, design, or mechanical work.
2. Select the narrowest role from `references/primitive-routing.md`.
3. Select the model and reasoning level from `references/model-capabilities.md`.
4. Add hidden skills, MCPs, and tools that the slice needs.
   Do not load nearby capabilities for convenience.
5. Add an independent verifier for medium-risk M+ work, all high-risk work, and
   all unknown-risk work.
6. Dispatch independent lanes together.
   Keep shared architecture and final judgment in the chief session.
7. Supervise active lanes.
   Correct drift, replace failed routes, reconcile conflicts, and inspect evidence before integration.

For XL implementation or design work, dispatch `daedalus` first to produce the
dependency graph.
Then fan out one `builder` or `designer` lane per independent slice.
Keep recursion within the configured depth.


## Required manifest

Return these fields in this order before spawning a substantive lane:

1. `role/agent`
2. `model:reasoning`
3. `skills to load`
4. `MCPs and tools`
5. `verifier lane`
6. `contract and evidence return`

Name the role, model, reasoning level, and primitive loadout in every substantive delegation brief.
A generic prompt to a generic worker is not a composition.


## Chief-session boundary

The chief executive owns:

- operator intent and acceptance;
- shared architecture and cross-lane contracts;
- team composition and supervision;
- conflict resolution and final judgment;
- integration and the final live proof.

Specialist lanes own execution.
Use `reviewer` for code-review programs, `code-critic` for one adversarial
read-only review, `cassandra` for incidents and digital forensics, `qa` for live
verification, `builder` for accepted implementation, `daedalus` for
architecture, `magellan` for broad research, `curator` for full-board grooming,
and `solomon` for contested decisions.


## Completion

A dispatch is complete only when every lane returns its named artifact or evidence.
The chief resolves contradictions.
The integrated outcome must pass the live oracle.
Subagent confidence is not evidence.
