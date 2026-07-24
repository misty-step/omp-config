# Hatchet implement stage

Implement only. Do not call Powder, native Task, subagents, web search, or live verification. Do not search outside the exact paths below.

The root cause is already established: installed `discovery/helpers.ts` parses `tools: '*'` as the unknown literal `*`; it never expands it. OMP supports full built-ins by omitting the optional `tools` field. Restricted agents keep explicit CSV lists.

1. Read only `global/agents/*.md`, `global/skills/dispatch/references/agent-compositions.json`, `global/skills/dispatch/references/primitive-routing.md`, `bin/check`, and the focused checker tests under `tests/`.
2. Remove `tools: '*'` from `argus`, `cassandra`, `curator`, and `hephaestus`, and remove the mirrored `tools` field for those four from `agent-compositions.json`. Preserve every restricted list exactly.
3. Update `bin/check` and focused tests so omitted `tools` is the one valid full-builtins representation and every explicit name is checked against OMP's existing built-in tool authority rather than a copied second catalog. An unknown name must fail with its agent and name visible. Update the routing reference to state this contract.
4. Run only the focused checker command(s). Do not format, lint, run a broad suite, or perform live child introspection.
5. Commit once with `git -c user.name='OMP Hatchet Implement' -c user.email='omp-hatchet-implement@local' commit ...`. Never merge, push, or rewrite history.
6. After the commit and checks, call `hatchet_terminal` exactly once with outcome `completed`, the new full HEAD, and artifact refs for the commit, exact gate result, and files. This tool is the only completion channel. Do not print terminal JSON or call `yield`; after the tool accepts the terminal, end the turn.
