# Landmark floor

Use Landmark as the release-intelligence source of truth via `/foundation` factory surfaces.

## Required evidence for versioned products

1. `landmark describe --json` succeeds in the repo, or equivalent manifest exists.
2. Automated versioning path is named (command, workflow, or release kit step).
3. Release notes generation path is named and produces user-facing notes.
4. Changelog path is named (file and/or generated surface).
5. CI or release workflow invokes the above on the real default branch path.

## Non-releasing repos

Mark Landmark dimensions `n/a` only when the repo does not ship versions and the
audit states why (spike, notes vault, private scratch, pure mirror).

## Anti-patterns

- Claiming Landmark integration from a stale markdown mention.
- Hand-edited version strings with no tool path.
- Release notes that exist once and never regenerate.
