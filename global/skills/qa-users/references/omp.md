# OMP composition

The OMP root owns repository and product discovery. Before dispatch it reads project rules, product docs, routes, scripts, and live non-production entrypoint definitions, confirms access, identifies the user paths to exercise, and freezes `input.v1`. Every entrypoint must name `environment: local`, `dev`, or `staging`; production is never a target.

- Coordinator: `global/agents/qa-user.md` receives only the frozen root artifact. It has `task` authority, validates the supplied plan, preserves the effective execution overrides, dispatches one browser-only leaf per persona, and returns raw evidence. It has no read, edit, write, browser, tracker, or PR authority.
- User leaf: `global/agents/qa-user-leaf.md` has `browser` only and receives one named browser entrypoint. It acts only through user-visible controls and information; it cannot inspect page source, scripts, DOM internals, storage, network internals, developer diagnostics, product source, tracker state, or files. It returns runtime evidence, strengths, friction, and exact user steps.
- Environment: the coordinator and leaves use only predeclared `real: true` entrypoints whose environment is `local`, `dev`, or `staging`. Unsupported entrypoint kinds are blocked rather than substituted. Production targets are rejected before dispatch.
- Depth: OMP root -> `qa-user` coordinator -> one `qa-user-leaf` per persona. The coordinator does not delegate triage, RCA, tracker, or PR writes.
- Root authority: the OMP root owns exploration, input/schema and semantic validation, reproduction confirmation, optional read-only RCA, triage, suppression, exhaustive tracker query/create/read-back, deduplication, PR comments, and active work-ledger writes.
- Handoff: `fix-and-pr` requires separate explicit authorization and a read-back issue ID. It runs only after filing and read-back, with `inside_user_session: false`.
