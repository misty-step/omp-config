---
name: audit-simplifications
description: Whole-repo read-only audit for material simplifications in data, state, control flow, and ownership.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Audit Simplifications

Read-only coverage audit of representation. Do not edit files, run tests,
implement recommendations, commit, or push. Repository reads and other
read-only inspection are allowed.

Not `improve-codebase-architecture` (module deepening, HTML, then grill). Not
`foundation` (baseline controls). Not `code-review` (repair a completed
change). This skill inventories every subsystem and hunts invalid or duplicated
representation. It does not install controls or deepen modules for their own
sake.

Default to the current repository unless the invocation names another target.
Keep one project boundary.

Write the canonical report to a scratch path outside the repository
(`local://audit-simplifications.md` or an OS temp file). Do not write into the
tree under audit.

```text
inventory -> bounded reviews -> validate -> audit the audit -> deliver
```

## 1. Coverage contract

Inspect the repository. Inventory every identifiable subsystem. Include
frontend, backend, shared infrastructure, platform bridges, generated-contract
ownership, and test or tooling infrastructure when they own material behavior.

Give each subsystem:

- a stable ID and descriptive name;
- an exact, non-overlapping ownership boundary;
- key implementation files;
- relevant public interfaces, major call sites, and tests;
- a status: `queued`, `in review`, `recommend`, or `skip`.

The inventory is the coverage contract. Broad catch-all rows do not prove
coverage.

Seed the report with: subsystem inventory, confirmed opportunities, explicit
skips, cross-cutting patterns, duplicates and superseded findings, priorities
and dependencies, and an audit log.

Completion criterion: Every identifiable subsystem has a row with a stable ID,
exact boundary, files, interfaces, and status `queued`.

## 2. Bounded reviews

Coordinate. Continue until every inventory row is `recommend` or `skip`.

Use fresh read-only `scout` workers. Give each worker one distinct subsystem
and its exact ownership boundary. Keep concurrency to the lanes you can
harvest. Use one wait mechanism. Do not interrupt a productive worker because
it is slow. Harvest, then close.

Each worker reviews its subsystem for at most two materially useful
simplifications in data structures, state representation, or organizing model.
It inspects implementation, public interfaces, major call sites, and existing
tests. It stays inside the assigned boundary. It may name a cross-subsystem
concern; it must not expand scope to solve it.

Workers look for:

- scattered booleans or nullable fields that permit invalid combinations and
  should become a state machine or discriminated union;
- repeated assumptions about object shape that need a shared typed model;
- duplicated branching that a small map, registry, reducer, or command model
  would remove;
- unclear state or behavior ownership that a small module boundary would
  clarify;
- repeated scans, transformations, or lookups where a more appropriate
  collection or index would materially simplify behavior;
- lifecycle, concurrency, or async states whose representation permits stale
  or contradictory state.

Do not force an abstraction. Prefer boring local code when it is already
clear. Do not recommend a change solely for stylistic consistency,
hypothetical extensibility, minor line-count reduction, or moving existing
branching behind a new type.

A worker returns at most two opportunities. If nothing meets the threshold,
it returns `skip`.

Each recommendation must include:

1. Verdict: `recommend` or `skip`.
2. Evidence with exact file and line references.
3. Current complexity or invalid states.
4. Proposed representation and why it is simpler.
5. Smallest credible implementation scope, including affected files and
   interfaces.
6. Regression risks and migration concerns.
7. Existing and additional validation required.
8. Confidence: `high`, `medium`, or `low`.

Completion criterion: Every inventory row has a harvested worker result.

## 3. Validate

Independently verify every finding against the current repository before
accepting it.

Reject, narrow, or demote a recommendation that is vague, duplicates another
finding, misunderstands intentional semantics, or merely relocates complexity.

Record skips as completed coverage. Deduplicate overlapping findings. Assign
each accepted recommendation to one authoritative subsystem.

If a pass reveals a real omitted subsystem, add an explicit row and audit it.
Do not hide the omission by broadening a completed boundary.

Completion criterion: Every finding is verified, owned by one subsystem, and
either accepted with complete fields or recorded as skip, reject, or demote.

## 4. Audit the audit

Run fresh independent passes for:

- repository coverage and missing subsystem boundaries;
- duplication and ownership overlap;
- materiality and over-abstraction;
- schema completeness;
- dependency-aware priority ranking.

Rank accepted recommendations by concrete impact, confidence, implementation
effort, blast radius, and prerequisites. Name the best first implementation
slices.

Completion criterion: Coverage is complete, fields are complete, duplicates
and weak abstractions are gone, and priorities are internally consistent.

## 5. Deliver

The audit is complete only when:

- every identifiable subsystem has been reviewed;
- every subsystem is `recommend` or `skip`;
- every finding has evidence, scope, risk, and validation;
- duplicates and weak abstractions have been removed;
- priorities and dependencies are consistent;
- the repository remains unchanged.

Present the report. Do not implement.
