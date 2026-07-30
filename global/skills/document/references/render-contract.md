# Render contract — surfaces & sync

Run one generation and render every surface from it. "Synced docs" means markdown source of truth → consistent HTML and diagrams from the same run, not three hand-maintained copies.

## Markdown is the source of truth

- Committed under `docs/` (operator picks the exact root if not `docs/`).
- Portable, diffable, blame-able, travels with forks and offline clones.
- Front-matter provenance on every page (`templates/page.md`).
- Mermaid fenced blocks embedded inline — text, so they diff and the render
  oracle can parse them.

## HTML render

The browsable surface. Do not write a static-site generator or a bespoke aesthetic — **compose**:

- `/design` + `anthropic-frontend-design` for the visual system, typography, and avoiding templated-default tells.
- Use the "think in HTML" doctrine: layout, hierarchy, tables, diagrams, and callouts make the docs easier to inspect than prose.
- Use `/showcase`'s publish machinery if the docs become a public site.

Keep the output self-contained and navigable (sidebar/TOC, search if cheap). Render mermaid to inline SVG. Resolve internal links. If the repo has a docs toolchain (mkdocs, Docusaurus, rustdoc, or a Mintlify site), use it. Do not invent a parallel one. Match the repo.

## Diagrams

- Mermaid in markdown → rendered in HTML. Use architecture, sequence, data-flow, dependency, or state diagrams only when they answer a needed question (`references/information-architecture.md`).
- The render oracle fails the build on any unparseable diagram. Do not silently drop one.

## Output layout

```
docs/
  index.md                 # root / overview, the entry page
  <section>/<page>.md      # IA tree (provenance-stamped)
  assets/                  # generated images/screenshots if any
```

The built HTML target is the operator's call — published site, a gitignored
local `_site/`, or a GitHub Pages branch. Default to local render pending an
explicit publish decision. Never push a public site without operator sign-off.

## "Synced across surfaces"

Markdown, HTML, and (optionally) a GitHub Wiki mirror derive from one generation. If you mirror to GitHub Wiki, flatten the page tree and rewrite internal links. Keep the committed `docs/` markdown canonical. Treat mirrors as derived. Never edit them in place.
