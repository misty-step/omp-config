---
name: deliver
description: Take one ready ticket or accepted spec through to an elevated design, proved implementation, adversarial QA, and open pull request with full evidence.
disable-model-invocation: true
argument-hint: "[ticket or spec]"
---

# Deliver

Take one ready ticket or accepted spec through to a proved, reviewed, tight,
open pull request. Elevate system design, prove behavior with adversarial QA,
and document choices.

```text
claim -> isolate -> grok & design -> test first -> implement -> adversarial QA
-> self-review & repair -> tighten -> publish PR -> audit choices
```

## 1. Claim

Resolve and claim the target ticket or spec. Register or link the durable spec
in the trusted backlog of record before implementation. Use the
highest-priority ready backlog item when no target is supplied. Skip claimed,
blocked, superseded, or unshaped work.

The work is ready only when accepted intent defines the outcome, data
ownership, invariants, interfaces, failure behavior, non-goals, and acceptance
scenarios. If a material architectural choice remains unsettled, stop and ask
the operator to run `/shape` or `/explore-unknowns`.

Completion criterion: One accepted, independently useful slice is claimed.

## 2. Isolate

Create an isolated git worktree from the default branch (using `git worktree`,
`herdr`, or `exe.dev` as appropriate). Leave the operator's branch and
unrelated work untouched. Record the exact base revision.

Completion criterion: The slice has one isolated checkout and one owner.

## 3. Grok and design elevation

Do not patch spaghetti on top of existing debt. Channel Torvalds (data
structures first, single datum ownership, invalid states unrepresentable) and
Ousterhout (deep modules, small stable interfaces, define errors out of
existence).

Before writing production code:

- map the core data model and its state transitions;
- design the deepest possible module interface that hides internal complexity;
- ensure every datum has exactly one authoritative owner and path;
- plan required deletions of dead abstractions or obsolete pass-throughs.

Completion criterion: A clean, elevated data structure and module design is
settled before implementation.

## 4. Test first

Before the first production edit, specify behavioral tests defending the
observable boundary:

- CLI exit codes and output formatting;
- API response contracts and error payloads;
- persisted state schemas;
- real-surface UI/TUI interaction flows.

Read `skill://evidence-packet`. Capture required pre-change baselines now.

Completion criterion: Behavioral tests and proof plans are written before
production edits.

## 5. Implement

Implement in dependency-ordered slices:

- fix the source directly;
- migrate every caller across the repository;
- delete obsolete code, configurations, stale tests, and shims;
- avoid unnecessary allocations, copies, or speculative abstractions.

Continue autonomously for conservative reversible choices. Stop only for
intent, scope, compatibility, or hard-to-reverse changes.

Completion criterion: The slice is complete with all callers migrated and zero
dead paths left behind.

## 6. Adversarial QA

Dispatch a fresh-context adversarial QA subagent to exercise the actual running
system: *"Give me irrefutable evidence that this works on the real surface."*

The QA subagent must start the real application and test:

- happy, boundary, invalid, and malicious inputs;
- error handling, timeouts, restart, and recovery;
- viewport, theme, and keyboard navigation variants for UI;
- concurrency, ordering, and idempotency where applicable.

Inspect every captured artifact. Automated unit tests do not substitute for
hands-on verification of the running product surface.

Completion criterion: All checks pass, and an inspected evidence packet proves
the real surface functions correctly.

## 7. Self-review and repair

Conduct a fresh-context review of the complete diff and surrounding system
against the accepted spec and design invariants. Verify that:

- data structures are clean and invalid states are unrepresentable;
- module interfaces remain small and internal complexity is hidden;
- all callers across the repository have been cleanly migrated;
- no temporary scaffolding, dead code, or placeholder comments remain.

Repair any identified defects autonomously. Rerun affected behavioral tests
and product-surface QA checks until green.

Completion criterion: The implementation is tight, tests and QA pass, and all
in-scope defects are resolved.

## 8. Tighten

Apply the deletion-first order: challenge, delete, simplify. Remove incidental
state, temporary scaffolding, pass-through wrappers, and test-only production
seams. Tidy the green result into a clean sequence of semantic commits.

Completion criterion: Clean, narrative commit history with green tests and QA.

## 9. Publish PR and audit choices

Open a clean, unmerged pull request. For every observable claim, follow
`skill://evidence-packet/DELIVERY.md` and upload the inspected packet through
the repository-approved PR attachment interface before calling the PR ready.
The PR description must carry:

- the work item and accepted spec;
- design decisions and elevated data models;
- test results and an Evidence section with openable before/after media;
- short video or GIF attachments for temporal interaction claims;
- the attached evidence record or downloadable packet bundle;
- release notes, production signals, and rollback path.

Render the PR and open every evidence link. Local paths and artifact hashes are
capture metadata, not reviewer-accessible evidence. A failed or unavailable
attachment interface blocks delivery unless the operator explicitly waives the
specific artifact.

Conclude by emitting an `audit-choices` decision ledger summarizing all
tradeoffs and non-obvious choices made during implementation.

Completion criterion: An unmerged pull request URL is returned; every required
evidence artifact opens from that PR; proof and decision accounting are
complete.
