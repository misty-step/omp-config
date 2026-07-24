# Hatchet adversarial review stage

Review commit `d5d6966317ccd3f38f5b3577f4843c7215a825da` for the `omp-config-tools-wildcard-resolution` card. You are read-only, and your cwd is already `/tmp/omp-config-wildcard-canary`.

1. Confirm HEAD is exactly `d5d6966317ccd3f38f5b3577f4843c7215a825da` and record `git status --porcelain`.
2. Inspect only that commit's changed diff and these directly relevant files: `bin/check`, `bin/config_contract.py`, `global/agents/*.md`, `global/skills/dispatch/references/agent-compositions.json`, `global/skills/dispatch/references/primitive-routing.md`, and focused tests or fixtures invoked by `bin/check`.
3. Check for one supported full-tool representation, preserved restricted definitions, visible rejection of unknown tool names, catalog/parser drift, and any card criterion that a later live-verification stage must still prove.
4. Run only the focused `python3 bin/check` gate and narrow read-only commands against the listed files. Never search `/`, home, Powder, unrelated repositories, or unrelated files. Do not use `find`.
5. Do not edit, commit, merge, push, format, lint, run broad suites, or invoke live Task; live behavior belongs to the dedicated next stage.
6. Confirm HEAD and worktree status are unchanged.
7. After the final check, call `hatchet_terminal` exactly once with outcome `accepted` when no blocker remains or `blocked` otherwise, the unchanged full HEAD, and artifact refs containing each concrete finding or exact passing command plus `worktree:unchanged`. This tool is the only completion channel. Do not print terminal JSON or call `yield`; after the tool accepts the terminal, end the turn.
