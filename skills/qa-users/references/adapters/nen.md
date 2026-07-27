# Nen adapter

Nen consumes the canonical `skills/qa-users/` directory through `nen/skills/qa-users` and must not copy or fork its files.

- Coordinator: `agents/qa-users-coordinator.md` is the only dispatcher and tracker writer. It validates input, freezes execution overrides, dispatches app-user leaves, and serializes tracker query/create/read-back operations.
- App-user leaf: `agents/qa-user.md` has only the named application-entrypoint tools. It cannot read product source, read tracker state, edit/write files, dispatch children, or file issues. It returns runtime evidence and user-path observations.
- Fresh RCA: use a read-only `nen.scout` child only after the coordinator records a confirmed reproduction. RCA cannot mutate application or tracker state.
- Depth: Nen root -> `qa-users-coordinator` -> `qa-user` or `nen.scout`; no deeper dispatch.
- Tracker: Powder is the selected Misty Step adapter. Coordinator tracker authority is restricted to the exact query/create/read-back operations declared by the host; persona and RCA tools do not include them.
- Handoff: `fix-and-pr` requires explicit authorization and a read-back issue ID, and runs only as a separate post-session handoff.

Nen role declarations keep the coordinator and app-user tool envelopes explicit. Execution overrides are recorded in `output.v1`, not inferred from role defaults.
