---
disable-model-invocation: true
name: qa-users
description: QA master kit. Explore a product, mint persona briefs, freeze a plan, dispatch browser personas, and synthesize runtime evidence.
argument-hint: "[app-or-entrypoint]"
---

# /qa-users

Kit for **qa-master**. Run bounded, evidence-backed persona QA on real non-production surfaces.

## Lifecycle

1. **Explore.** Read repository docs, routes, scripts, project rules, and live non-production entrypoints. Optional browser use is limited to entrypoint smoke or reproduction confirmation. Never run a full persona mission on the master.
2. **Mint.** Derive personas from product evidence. Each persona needs `id`, `label`, `mission`, `knowledge`, `blind_spots`, `entrypoint_ids`, and the required safety flags (`source_read`, `tracker_read`, `issue_write` all false). Prefer real roles and paths over stock stereotypes.
3. **Freeze.** Validate and freeze [`input.v1`](references/input.schema.json) before any persona spawn. Every entrypoint `environment` must be exactly `local`, `dev`, or `staging`. Production is rejected.
4. **Dispatch.** Start exactly one browser-only `qa-persona` per frozen persona within concurrency and session ceilings. Each leaf gets only its brief and one assigned real browser entrypoint.
5. **Synthesize.** Cluster strengths and friction. Confirm candidates before findings. Build the evidence packet for the chief.
6. **Hand off.** Return the packet to the chief. The chief owns tracker query/create/read-back, PR comments, and work-ledger writes. Optional `fix-and-pr` stays a separately authorized post-session handoff.

Follow [`references/lifecycle.md`](references/lifecycle.md) for normative ordering detail. Preserve schemas, validators, fixtures, execution overrides, fingerprints, triage, safety, create ceilings, and read-back rules.

## Contracts

- Semantic validation uses [`input-semantic.mjs`](references/input-semantic.mjs) and fixtures.
- Output validation uses [`output-semantic.mjs`](references/output-semantic.mjs).
- Fingerprints use [`finding-fingerprint.mjs`](references/finding-fingerprint.mjs).
- Safety ceilings live in [`references/safety.md`](references/safety.md).
- OMP agent split lives in [`references/omp.md`](references/omp.md).
- Persona leaf method lives in `skill://qa-persona`.

## Authority split

| Role | May | Must not |
|---|---|---|
| qa-master | explore, mint, freeze, dispatch personas, smoke/repro browser, synthesize | edit product code; tracker/PR writes; full persona missions |
| qa-persona | browser user mission on one entrypoint | source, tracker, devtools, dispatch |
| chief | tracker/PR/ledger after packet | skip freeze or persona evidence |

## Completion

Emit a complete evidence packet: frozen overrides, persona statuses, strengths, friction, findings with evidence, and residual risk. Chat alone is not completion.
