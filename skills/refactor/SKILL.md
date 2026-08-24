---
name: refactor
description: Pay down targeted architectural tech debt, deepen a module, simplify data models, and deliver the improvement to an open pull request.
disable-model-invocation: true
argument-hint: "[module, subsystem, or debt target]"
---

# Refactor

Targeted architectural debt payment and module deepening. Isolate, simplify the
data model or boundary, migrate every caller, verify zero behavioral
regression, and deliver directly to an open pull request.

```text
target -> isolate -> design elevation -> implement & migrate -> verify -> publish PR
```

## 1. Target and establish invariants

Use the named module, subsystem, or hot spot. If no target is supplied, identify
the highest-friction architectural defect in the current workspace (e.g.
boolean soup, shallow pass-through wrappers, leaked internal state, or
duplicated data representations).

Before modifying code, establish the invariant contract:

- the exact behavior, callers, and consumers that must be preserved;
- the internal complexity or invalid state being eliminated;
- the deeper interface replacing the shallow abstraction;
- the verification tests proving behavior is unchanged.

Completion criterion: One explicit module boundary, its preserved invariants,
and its target simplification are stated.

## 2. Isolate

Create an isolated git worktree from the default branch. Leave the operator's
working tree and branch untouched. Record the base commit.

Completion criterion: One isolated worktree exists for the refactor.

## 3. Design elevation

Channel Torvalds (data structures first, invalid states unrepresentable, single
datum ownership) and Ousterhout (deep modules, small interfaces, define errors
out of existence).

Apply the deletion test: removing or consolidating code is progress only when
complexity concentrates behind one clear owner rather than scattering to
callers. Do not introduce speculative interfaces or new adapter layers for
hypothetical consumers.

Completion criterion: The new design eliminates the target flaw with a smaller
or deeper public API.

## 4. Implement and migrate callers

Work in the isolated worktree:

- simplify or restructure the core data structures;
- eliminate pass-through wrappers, duplicate branching, and boolean flags;
- fix the source directly;
- migrate every caller across the repository to the elevated interface;
- delete all dead code, unused types, obsolete tests, and stale configuration.

Completion criterion: Zero callers use obsolete interfaces; no deprecated
shims or dead code remain.

## 5. Verify zero regression

Run repository checks, test suites, and product surface smoke tests. If test
coverage around the modified module was thin, ensure characterization tests
defend the boundary before and after the refactor.

Capture proof that observable behavior, API responses, CLI outputs, and
persisted state remain identical.

Completion criterion: All checks pass, behavioral tests are green, and zero
functional regressions are observed.

## 6. Publish

Open a clean, unmerged pull request. The PR description must carry:

- **Problem:** The architectural flaw, boolean soup, or shallow module;
- **Elevated Design:** How data ownership and module depth were improved;
- **Deletions:** Code, types, and wrappers removed;
- **Verification Evidence:** Test results and proof of zero regression.

Output the pull request URL and a summary of decisions made.

Completion criterion: An unmerged pull request is published with clean semantic
commits and full verification proof.
