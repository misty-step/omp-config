# Foundation checklist

Score **every** dimension every run: `pass`, `gap`, `n/a`, or `waived`.
Cite paths, commands, URLs, or receipts. Absence without reason is `gap`.

Product law: `global/references/application-floor.md`.  
This file is the operational scorecard for `/foundation`.

## Proof

Five classes — do not substitute:

| Class | Counts as evidence |
|---|---|
| Declaration | Path, command name, policy, waiver row exists |
| Deterministic gate | Gate command ran; report/artifact proves outcome |
| Live probe | Real boundary exercised; receipt |
| Capability eval | Fresh task output + grader |
| Fresh judgment | Artifact-only critic report |

`pass` needs the strongest class the dimension implies. Declaration alone does
not pass a gate, live, eval, or judgment row.

## Core files

| Dimension | Pass rule |
|---|---|
| VISION.md | Root `VISION.md` answers what / why / excellence for a cold agent |
| README.md | Purpose, quickstart, links to docs/site/proof |
| DESIGN.md | Record present/absent only; not required for brand law |

## Public proof and docs

| Dimension | Pass rule |
|---|---|
| Pitch | One outsider pitch in README and/or marketing site |
| Screenshots/GIFs | Current screenshot or GIF in README and/or marketing site |
| Marketing site | Public page + deploy path, or waiver (private-only tool) |
| Docs surface | `docs/` or published docs URL linked from README or marketing |
| Operator walkthrough | UI/serve mode has an operator path a stranger can follow |

## Access faces

Functional core behind one robust API. Required faces over that core:

| Dimension | Pass rule |
|---|---|
| Functional core + API | Domain rules live in one durable API (or library API); faces do not reimplement business logic |
| CLI | Core verbs on a CLI with honest help |
| UI | Operator UI for core verbs, or waiver (library/daemon-only) |
| Skill | Shipped skill teaches the real CLI/API; not a parallel protocol |
| MCP | Core verbs covered end-to-end; stub or read-only core = `gap` |
| SDK | `pass` if external consumers need it; else `n/a` with reason |

## Gates and quality

| Dimension | Pass rule |
|---|---|
| Fast gate | Repo-owned command fits normal edit cycles |
| Full gate | Repo-owned command holds merge/release invariants |
| CI wiring | CI runs the full gate on the protected branch; gate not weakened to pass |
| Supply chain | Lockfile + vuln/license/secret scan policy with evidence, or waiver |
| Changed-line coverage | Threshold or ratchet declared and reported, or waiver |
| Mutation | Command/threshold/survivors exist when applicable, or `n/a` with reason |

## Tests and live proof

| Dimension | Pass rule |
|---|---|
| Unit tests | Behavior tests exist for core logic |
| Integration tests | Real internal collaborators; external edges emulated/contracted |
| End-to-end tests | User-visible flows at the real boundary when a user surface exists |
| HTML real-engine tiers | For HTML/JS/CSS: (a) syntax-gate artifacts, (b) headless smoke zero console errors, (c) golden paths desktop + ~390px — or `n/a` if no such surface |
| Live probe | At least one real CLI/API/UI/runtime probe with receipt for shipped surfaces |

## Architecture and typing

| Dimension | Pass rule |
|---|---|
| Deep modules | Boundaries favor deep modules; no shallow pass-through layering as the design |
| Infra agnosticism | Deploy targets are not the architecture; host coupling is not load-bearing |
| Static typing | Go or Rust by default; TypeScript only when the platform forces it; weaker stacks name constraint + why |

## Release and onboarding

| Dimension | Pass rule |
|---|---|
| Landmark / release notes | Automated version + user-facing notes/changelog path, or `n/a` for non-releasing repos |
| Frictionless onboarding | One obvious zero-to-running path (copy-paste where possible) |
| Doctor | Command or path fails loud when deploy/runtime is dead |
| Running services | Daemons/agents/indicators required by the product are installed **and** verified live |

## Factory and operations

| Dimension | Pass rule |
|---|---|
| Work ledger | Durable work store bound (Powder here) with queryable project/repo identity, or waiver |
| Canary | Mode + live identity when the service is monitored; else `n/a` with reason |
| Backup/restore | Policy + restore evidence when stateful; else `n/a` |
| Data lifecycle | Classification/retention/deletion when personal/customer data exists; else `n/a` |
| Performance budgets | Declared where latency/cost is product-critical; else `n/a` |
| Accessibility | Standard + evidence where UI is human-facing; else `n/a` |

## Model seams (when present)

| Dimension | Pass rule |
|---|---|
| Capability eval | Each real model decision has a held-out task + grader, or single `n/a` row with reason |
| Fresh judgment | Irreducible architecture/product judgment has artifact-only critic path, or `n/a` with reason |

## Severity order (remediate in this order)

1. False public claims; missing VISION/README; broken onboarding (“installed” ≠ running)
2. Missing required face or stub MCP; no full gate / CI gate weakened
3. No real-engine proof on HTML surfaces; no live probe on shipped surface
4. No Landmark/release path on a versioned product
5. Docs/marketing/pitch/proof gaps
6. Factory/ops/eval rows still open

## Waiver metadata

For every `waived` row record: owner, reason, current evidence, review date, expiry.
Expired waiver = `gap`.
