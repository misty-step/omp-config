---
name: qa-users
description: Run bounded persona-driven QA against real local, dev, or staging entrypoints; preserve strengths and friction, confirm runtime findings, deduplicate tracker or PR work, and return evidence to the root.
---

# qa-users

Run a bounded, evidence-backed user session. The OMP root owns discovery, validation, triage, deduplication, and tracker or PR writes.

## Start with discovery

On direct invocation, the root first explores the repository and product docs, routes, scripts, project rules, and live non-production entrypoints with its available tools. It identifies real browser entrypoints and their environment (`local`, `dev`, or `staging`), the product paths worth exercising, and existing project QA conventions. Ask the operator only for persona, access, or entrypoint facts that tools cannot establish. Never target production.

Freeze the resulting `input.v1` before dispatch. The frozen input is the authority for personas, missions, named browser entrypoints, environments, and execution limits; do not infer or add a surface during a session.

## Contract

The root MUST validate and freeze [`input.v1`](references/input.schema.json) before dispatch. Every `entrypoints[]` object MUST declare `environment` as exactly `local`, `dev`, or `staging`; the root rejects every other value and every production target. Semantic validation MUST use [`input-semantic.mjs`](references/input-semantic.mjs) and its fixture contract to reject duplicate `personas[].id` values, duplicate `entrypoints[].id` values, undeclared `execution_overrides.entrypoints` values, invalid defined override entrypoint lists, and persona `entrypoint_ids` values outside the effective entrypoint ID set. JSON Schema cannot express those object-ID and cross-array membership rules.

Before emitting a report, output semantic validation MUST use [`output-semantic.mjs`](references/output-semantic.mjs). Every report MUST include frozen effective execution overrides, including values inherited from a harness default. List resolved harness, provider, model, reasoning, concurrency, session length, seed, entrypoint set, threshold, create ceiling, and selected tracker in `execution_overrides`; require `execution_overrides.provenance.<field>.source` for every field, with `cli` taking precedence over `input`, and `input` over `harness-default`.

## Run lifecycle

Follow [`references/lifecycle.md`](references/lifecycle.md) in order. The input, mode precedence, dry-run guarantees, effective overrides, and threshold rules are normative in [`references/execution-overrides.md`](references/execution-overrides.md). Preserve schemas, validators, fixtures, execution overrides, fingerprints, triage, safety, create ceilings, tracker pagination, and read-back.

The root must first establish the live non-production application surface, then dispatch exactly one browser-only `qa-user-leaf` per configured persona, bounded by `concurrency` and `session_length_seconds`. A leaf uses only its assigned, predeclared browser entrypoint marked `real: true` and carrying an allowed environment. It cannot read product source, read tracker state, file issues, edit source, or invent an entrypoint. Unsupported entrypoint kinds are blocked rather than substituted.

Each leaf returns runtime evidence, exact user steps, strengths, and friction. Each confirmed finding records `affected_entrypoint`, expected behavior, observed behavior, evidence, severity/confidence, category, and a root cause only when runtime evidence directly establishes it. A candidate enters triage only after confirmation. A failed persona status MUST include `failure_reason`.

## Root triage and handoff

The root alone validates and freezes input, confirms reproductions, starts any fresh read-only RCA, applies triage and suppression, and preserves strengths and suppressed friction with reasons. Exactly one serialized root tracker writer exhaustively scans every tracker page or cursor, blocks on ambiguity or truncation, deduplicates using the canonical SHA-256 fingerprint from [`references/finding-fingerprint.mjs`](references/finding-fingerprint.mjs) plus `affected_entrypoint`, files only actionable evidence-backed findings within `maximum_creates`, and reads every created issue back. Accepted and deduplicated findings MUST carry `tracker_issue_id` after filing or matching. Follow [`references/tracker.md`](references/tracker.md).

Return the complete evidence packet to the OMP root. The root deduplicates findings against existing work, then records actionable results as PR comments or in the active work ledger using the repository's selected tracker. Personas and the coordinator never invoke tracker operations or write PRs.

`fix-and-pr` is optional and separately authorized. It runs only after issue filing and read-back, with `inside_user_session: false`; it is a post-session handoff, never a persona action.

## OMP composition

Read [`references/omp.md`](references/omp.md) for the coordinator and browser-leaf authority boundary. The coordinator has `task` only. Browser leaves have `browser` only. The OMP root retains repository exploration, validation, triage, deduplication, and tracker or PR writes.
