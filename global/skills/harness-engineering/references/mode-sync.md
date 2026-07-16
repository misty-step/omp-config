# /harness-engineering external imports

Synchronize external skill exemplars into Roster without making them
first-party source.

## Source Of Truth

`primitives/skills/.external/registry.yaml` declares external sources, immutable
pins, paths, include filters, and alias prefixes. Vendored payloads and their
`.sync-meta.json` receipts are committed Roster state.

## Lifecycle

1. Fetch the source at its full pinned SHA; never import from a floating branch.
2. Copy selected skill folders byte-identically under
   `primitives/skills/.external/<alias>/`, preserve the upstream license, and
   write `.sync-meta.json` with repo, SHA, source suffix, and fetch clock.
3. Update the registry declaration in the same diff.
4. `roster check` verifies alias uniqueness and registry/receipt/directory
   consistency offline; compare vendored bytes with the pinned checkout during
   the import review.
5. Reference the imported skill by its source-qualified identity from a pack or
   role. `roster dispatch` projects it only for the selected agent session.

An import changes only its named source. Preserve unrelated vendored skills;
`roster check` rejects orphan directories rather than silently pruning them.

## Design Rule

Imported skills are external exemplars/tools. Keep source ownership in the alias
(`vercel-*`, `every-*`) unless a shaped ticket proves the behavior belongs in a
first-party Roster primitive. Registry validation must fail on global alias
collisions instead of relying on projection order.
