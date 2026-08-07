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

## Severity guide

1. Missing VISION/README or false public claims
2. No Landmark release path on a versioned product
3. No pitch or proof media on a public product
4. Docs surface missing or unlinked
5. Marketing site missing when the product is meant to be public
