# omp-config

Edit harness sources here. Run `./install` to deploy to `$(omp config path)`;
keep live deployed files out of manual edits. The installer merges existing
MCP authentication and replaces the deployed skills and agents.

## Skill provenance

External skills (`frontend-design`, `show-me`, `audit-choices`, `wrangler`,
`find-bugs`, `herdr`, `ast-grep`, and other vendored packages) stay verbatim.
Update from upstream or remove the whole package. Use a distinctly named
homebrew skill when different behavior is needed.

Homebrew skills should contribute useful knowledge or a distinct outcome.
Consolidate overlapping skills and remove command wrappers. When replacing a
skill, migrate callers and remove obsolete directories in the same change.
