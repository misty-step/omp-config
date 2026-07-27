# OMP adapter

OMP consumes the canonical `skills/qa-users/` directory through `global/skills/qa-users` and must not copy or fork its files.

- Coordinator: `global/agents/qa-user.md` is non-writing. It resolves the input, dispatches the existing `qa` user leaves, owns the serialized tracker-writer sequence through the selected adapter, and records explicit execution overrides. It has no `edit` or `write` authority.
- User leaf: existing `global/agents/qa.md` remains the user leaf. For a `qa-users` run, the coordinator grants it only the named application entrypoint subset (`browser` and/or the predeclared CLI/HTTP/desktop/MCP adapter), and the leaf returns evidence without tracker calls or source access. Existing verifier behavior outside `qa-users` is unchanged.
- Depth: OMP root -> `qa-user` coordinator -> `qa` leaf. The coordinator does not delegate tracker writes to a persona.
- Tracker: use the selected adapter, with Powder as the Misty Step default. Only the serialized coordinator-side writer performs exhaustive search, deduplication, creation, and read-back.
- Handoff: `fix-and-pr` is a separately authorized post-filing handoff and never runs inside `qa`.

The coordinator's adapter-level tool ceiling is `read,grep,glob,bash,browser,web_search`; it intentionally omits `edit` and `write`. The `qa` leaf's `qa-users` execution surface is narrower than its general verifier envelope and is limited to real, predeclared application entrypoints.
