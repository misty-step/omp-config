---
name: install-anti-slop
description: Install the bundled anti-slop Oxlint plugin in a TypeScript or JavaScript repository.
disable-model-invocation: true
---

# Install anti-slop

Anti-slop rules reject type laundering and generated-looking indirection before
review. Integrate them with the repository's existing lint path; do not create a
second lint system.

## Inspect

Read repository policy, dirty state, package manager, Oxlint or Vite+
configuration, existing ignores, and any current anti-slop copy. Preserve
unrelated work.

Done when the existing lint owner and destination are clear.

## Install

Run from the target repository:

```sh
node <skill-directory>/scripts/install.mjs [relative-destination]
```

The default destination is `tools/oxlint/anti-slop`. The script refuses to
replace it. Compare an existing copy before any forced replacement.

Query current compatible `oxlint` and `@oxlint/plugins` versions. Install both as
development dependencies with the current package manager. Register the copied
plugin in the existing configuration. Enable every exported `anti-slop` rule at
`error`.

Merge existing ignores. Exclude the copied plugin and project-local installed
agent assets from lint and format. Keep owned dot-directories in scope. For
Vite+, update both `lint` and `fmt` ownership.

Done when one repository-owned command loads every rule.

## Verify

Run the repository's lint, typecheck, and full Vite+ check when present. Fix
owned findings only when migration is in scope. Keep rule severity and type
safety intact.

Return copied path, dependency versions, configuration changes, checks, and
remaining findings.

Done when the normal repository gate enforces the plugin.
