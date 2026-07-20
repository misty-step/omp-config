# Vendored external skills

Skills under this directory are copied bodies of externally-owned skills,
not roster-authored content.

**`registry.yaml` in this directory is the canonical provenance ledger**
(migrated from harness-kit 2026-07-07, roster-926; harness-kit's copy is
archived history). Every vendored dir carries a `.sync-meta.json` fetch
record pinning it to upstream content (commit SHA). To advance a pin:
fetch upstream at the new SHA, copy the body, update `.sync-meta.json`
and the `registry.yaml` entry together. Pins are content-hash-anchored,
never branch-floating — see `docs/research/roster-926-import-design-brief.md`
for the convention and its prior art.

## misty-powder

- Source: `misty-step/powder` (external repo)
- Pinned commit: `8c7a16a7c1bf3748ea939691a6545bd0f73c8f40`
- Copied byte-identical from harness-kit on 2026-07-05 (roster-916); re-synced
  byte-identical from `misty-step/powder` HEAD on 2026-07-16
  (roster-papercut-fleet-awareness) to pick up the papercut intake contract
  (`report_papercut` / `powder papercut`).

## mattpocock-writing-great-skills

- Source: `mattpocock/skills` at `skills/productivity/writing-great-skills`
- Pinned commit: `d574778f94cf620fcc8ce741584093bc650a61d3` (MIT)
- Vendored 2026-07-07 (roster-926 phase A); also the judgment layer behind
  `primitives/shared/references/skill-authoring-standard.md`.

## emilkowalski-skills

- Source: `emilkowalski/skills`
- Pinned commit: `f76beceb7d3fc8c43309cefad5a095a206103a4e` (MIT)
- Four aliases: `emil-emil-design-eng`, `emil-review-animations`,
  `emil-apple-design`, and `emil-animation-vocabulary`.
- Vendored 2026-07-09 (roster-944); the first two author/review motion, Apple
  Design is a conditional physical-interface philosophy, and Animation
  Vocabulary names effects without joining generative design fanout.
