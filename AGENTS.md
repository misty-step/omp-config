# omp-config

Edit harness sources here. Run `./install` to deploy to `$(omp config path)`;
keep live deployed files out of manual edits. The installer merges existing
MCP authentication and replaces the deployed skills and agents.

## Skill provenance

External skills (`frontend-design`, `show-me`, `wrangler`, `herdr`, and
`ast-grep`) stay verbatim.
Update from upstream or remove the whole package. Use a distinctly named
homebrew skill when different behavior is needed.

Homebrew skills explain non-obvious knowledge or a distinct outcome, favoring
why over a prescribed itinerary. Keep interactive assistance separate from
scheduled review and delivery systems. When replacing a skill, migrate callers
and remove obsolete directories in the same change.
