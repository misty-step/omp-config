# Safety and tool ceilings

Persona leaves are users, not reviewers. Their tool allowlist contains only the browser tool for the named application entrypoint. They receive no source-reader, editor, tracker, issue-writer, shell, search, or generic filesystem authority. An entrypoint MUST be predeclared with `real: true`, `kind: browser`, and `environment` equal to `local`, `dev`, or `staging`; the leaf cannot use another surface or target.

The coordinator MUST enforce these ceilings, not rely on persona prose:

- `source_read: false`, `tracker_read: false`, and `issue_write: false` are required by `persona.v1`.
- A leaf may act only on the assigned `entrypoint_id` present in the frozen input and marked `real: true` with an allowed environment.
- A leaf acts only through user-visible controls and information. It cannot inspect page source, scripts, DOM internals, storage, network internals, or developer diagnostics.
- A leaf records runtime evidence and returns control; it cannot create, edit, close, or comment on tracker items.
- A fresh RCA leaf starts only after the OMP root confirms a reproduction. RCA is read-only and cannot broaden the entrypoint set or mutate app/tracker state.
- Coordinators have task-only authority and no application, tracker, or file mutation authority; they may dispatch only the approved browser persona leaves and return evidence to the root.
- The OMP root owns the one serialized tracker writer, which alone may query, create, or read back tracker issues. No coordinator, persona, or RCA leaf may call those operations.
- Credentials remain in the harness or credential broker. Input, evidence, and reports contain references and identifiers, never secret values.

If a tool or entrypoint cannot enforce one of these boundaries, stop the run and report a blocked safety condition rather than silently widening authority.
