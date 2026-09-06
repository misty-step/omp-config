---
name: deliver
description: Take one ready slice to a proved, reviewed, unmerged pull request.
disable-model-invocation: true
argument-hint: "[ticket or accepted spec]"
---

# Deliver

Take one accepted slice to a proved, reviewed, unmerged pull request. Release
and production mutation belong to `/release`.

## Claim

Take one independently useful slice from the trusted record. Use `/shape` when
material intent, compatibility, scope, or architecture remains open. Isolate
the work from the operator's checkout and record the base revision.

For a refactor, name the constraint being removed, preserved behavior, owners,
callers, migration, and proof. For interaction polish, run the real surface and
record one frequent or costly interaction's steps, delay, errors, and evidence.

## Build

Plan proof before editing. Use current owners and interfaces unless evidence
shows they fail. Fix the source, migrate every caller, delete obsolete
adapters, shims, state, configuration, and temporary paths. Prefer deleting a
user step, state, choice, wait, or failure before optimizing speed. Preserve
accepted behavior and accessibility. Add tests only for uncovered observable
contracts.

## Prove

Run affected deterministic gates, start the changed system, and exercise its
real interface. Cover changed success, boundary, and failure paths; add
recovery, concurrency, or hostile-input checks only when touched. Repeat a
polished interaction with the same fixture and reject changes that move cost to
another user, operator, or failure path. For an expensive matrix or provider
run, first pass one cheap case through setup, scoring, evidence validation, and
artifact publication.

## Review

Review residual risk that gates cannot decide: intent, domain behavior,
boundaries, non-local effects, and touched concurrency, recovery, security, or
operating risks. Dispatch one bounded review to `reviewer`; use
`/security-review` for a changed trust boundary. Repair confirmed blockers,
then rerun affected gates and the real scenario on the final head.

Record recurring locally decidable findings for `/custom-linters` or
`/foundation`, and keep their implementation outside this slice.

## Publish

Open an unmerged pull request with an imperative `type(scope): outcome` title.
Include intent, decisions, deletions, checks, real-surface proof, rollback, and
residual risk. Use `show-me` for a small diff, call tree, component tree, or
Mermaid diagram when structure changed. Attach sanitized media through the
repository's supported review surface when visual evidence matters.

Return the exact final head, proof, review result, rollback path, and remaining
risk so the operator can decide whether to invoke `/release`.
