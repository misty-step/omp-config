# Foundation checklist

Score every dimension `pass`, `gap`, or `n/a`. Cite paths or URLs as evidence.
Aesthetic/brand-kit adoption is intentionally absent.

## Core files

| Dimension | Pass rule |
|---|---|
| VISION.md | Root `VISION.md` exists and answers what/why/excellence for a cold agent |
| README.md | Root README states purpose, quickstart, and links to docs/site/repo proof |
| DESIGN.md | Optional. Record present/absent only; do not require or create for brand law |

## Public proof

| Dimension | Pass rule |
|---|---|
| Pitch | One short outsider pitch appears in README and/or marketing site |
| Screenshots/GIFs | At least one current screenshot or GIF in README and/or marketing site |
| Marketing site | Public marketing page exists with deploy path, or waiver for private-only tools |
| Docs site | `docs/` or published docs URL exists and is linked from README or marketing |

## Release floor

| Dimension | Pass rule |
|---|---|
| Landmark present | Repo has Landmark config/manifest appropriate to its type |
| Automated versioning | Version bumps are tool-driven, not manual folklore |
| Release notes | User-facing notes generate on release |
| Changelog | Changelog or equivalent release history is generated or updated on release |
| CI wiring | Release workflow is real in GitHub Actions or documented equivalent |

## Access faces

SSOT: `global/references/application-floor.md` item **Faces**.
Shape: functional core → robust API → required faces over the API.

| Dimension | Pass rule |
|---|---|
| Functional core + API | Domain rules live behind one durable API (or library API for pure libs); no second business-logic copy in a face |
| CLI | Primary core verbs reachable from a CLI with honest `--help` / doctor path |
| UI | Operator-facing UI for core verbs, or waiver (library/daemon-only with reason) |
| Skill | Shipped skill (repo or omp-config) teaches agents the real CLI/API; not a parallel protocol |
| MCP | Optional. `pass` if core verbs covered; `n/a` if absent by choice; `gap` only if present but incomplete/stub |

Required faces: CLI, UI, skill. Optional: MCP, SDK.
Incomplete face = gap. Prefer absent MCP over stub MCP.

## Severity guide

1. Missing VISION/README or false public claims
2. Required face missing (CLI, UI, or skill) without waiver; or stub MCP kept as if complete
3. No Landmark release path on a versioned product
4. No pitch or proof media on a public product
5. Docs surface missing or unlinked
6. Marketing site missing when the product is meant to be public
