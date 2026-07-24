# Hatchet live verification stage

Exercise the exact live acceptance for `omp-config-tools-wildcard-resolution` at the required current HEAD. You are read-only in the repository.

1. Record the full HEAD and clean worktree status. Run the repository's focused agent-composition gate, including the case that injects an unknown tool name and visibly rejects it. Capture the exact command and rejection text.
2. The adapter has projected the target `global/agents` catalog and the missing `deliver` skill into this recipe's isolated agent directory before OMP discovery. Verify the projection through native Task. Do not run `bin/install`, replace recipe config, or alter the operator's stable OMP root.
3. Through the native live `task` tool, run representative child agents from the projected catalog: `hephaestus` for full built-ins and `cerberus` for a restricted set. Ask each child to introspect its own exact effective tool names from its live tool definitions and return a sorted list. Do not infer catalogs from markdown.
4. Compare the live lists with the supported built-in registry and each declaration. Full access must have one supported representation; restricted access must contain exactly its declaration plus documented always-included/executor tools. Unknown names must not silently reduce either catalog.
5. Confirm repository HEAD and status are unchanged. Do not edit, commit, merge, push, format, lint, or run broad suites.
6. After every live check, call `hatchet_terminal` exactly once with outcome `verified` only if every step passes, otherwise `failed`, and the unchanged full HEAD. Artifact refs must contain the exact focused command/result, visible unknown-name rejection, both exact child tool lists, OMP child evidence, and `worktree:unchanged`. This tool is the only completion channel. Do not print terminal JSON or call `yield`; after the tool accepts the terminal, end the turn.
