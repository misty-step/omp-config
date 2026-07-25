# Vendored external skills

Skills under this directory are copied bodies of externally-owned skills,
not locally authored content.

**`registry.yaml` in this directory is the canonical provenance ledger**
(migrated from harness-kit 2026-07-07, migration; harness-kit's copy is
archived history). Every vendored dir carries a `.sync-meta.json` fetch
record pinning it to upstream content (commit SHA). To advance a pin:
fetch upstream at the new SHA, copy the body, update `.sync-meta.json`
and the `registry.yaml` entry together. Pins are content-hash-anchored,
never branch-floating; keep the receipt and payload changes together.

## emilkowalski-skills

- Source: `emilkowalski/skills`
- Pinned commit: `f76beceb7d3fc8c43309cefad5a095a206103a4e` (MIT)
- Four aliases: `emil-emil-design-eng`, `emil-review-animations`,
  `emil-apple-design`, and `emil-animation-vocabulary`.
- Vendored 2026-07-09 (vendor sync); the first two author/review motion, Apple
  Design is a conditional physical-interface philosophy, and Animation
  Vocabulary names effects without joining generative design fanout.
