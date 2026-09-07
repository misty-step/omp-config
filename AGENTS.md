# omp-config

Edit harness sources here. Run `./install` to deploy owned components to
`$(omp config path)`; keep live deployed files out of manual edits. The
installer overlays source-owned config keys, merges matching MCP
authentication, and clean-replaces selected owned skill and agent packages
without deleting foreign packages.

## Skill provenance

External skills (`frontend-design`, `show-me`, `wrangler`, and `herdr`) stay
verbatim. Wrangler is the Cloudflare package at
`cloudflare/skills@d924cd8`. Update from
upstream or remove the whole package. Use a distinctly named homebrew skill
when different behavior is needed.

Homebrew skills explain non-obvious knowledge or a distinct outcome, favoring
why over a prescribed itinerary. Keep interactive assistance separate from
scheduled review and delivery systems. When replacing a skill, migrate callers
and remove obsolete directories in the same change.
