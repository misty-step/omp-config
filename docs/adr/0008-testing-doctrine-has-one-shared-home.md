# ADR 0008: Testing doctrine has one shared home

- Status: Accepted
- Date: 2026-08-06

## Context

Test doctrine was scattered across `quality/references/tests.md`,
`review-tests`, `verify-live`, `ci`, and `skill-authoring-standard`. Each
surface restated overlapping rules: fresh mock state, deterministic and
offline tests, no copy-pinned assertions, and the seeded-bug falsifier. The
duplication created a divergence risk and made a doctrine change a multi-file
edit.

Kent C. Dodds published `testing-principles.md` for the kody repository. The
document is contributor documentation, not a skill. It is valuable but
technology-specific: it names Vitest, Playwright, Cloudflare, and the
`node:sqlite` D1 facade.

The harness needed one canonical, technology-agnostic statement of what a good
test is. It also needed the placement decided, not assumed. Matt Pocock's
`writing-for-agents` mechanics states the placement rule: shared reference
that two user-invoked skills both need lives in a plain file outside the
skill system, and any skill can point at it.

## Decision

Create `global/references/testing-principles.md` as the single shared
reference for test doctrine. Adapt the kody document, rewrite it in
ASD-STE100 Simplified Technical English, and make it technology-agnostic so it
applies in Go, Rust, TypeScript, and other languages.

Codify the placement roles:

- A **skill** is an invoked procedure with steps and completion criteria.
  Skills do not restate doctrine they can point at.
- A **shared reference** under `global/references/` is a plain doctrine file
  outside the skill system. Any skill can point at it. `testing-principles.md`
  is this class.
- An **`AGENTS.md` line** is always-loaded root doctrine or a context pointer.
  It carries one pointer to the testing doctrine.
- A **`RULES.md` line** is an always-applied child invariant. No testing-doctrine
  line is added there; the doctrine is judgment, not a safety invariant.
- **`docs/adr/`** records durable decisions such as this one.

Wire the doctrine by pointer only:

- `quality/references/tests.md` becomes the `/quality tests` branch. It keeps
  the inventory, selection rules, heavy-class targets, rigor probes, evidence,
  and completion contracts. It drops the principle prose that the shared
  reference now owns.
- `review-tests` gains a pointer and three doctrine-derived checks: fragmented
  journey, copy-pinned assertions, and blanket output silencing.
- `ci`, `verify-live`, and `skill-authoring-standard` gain pointers.
- `global/AGENTS.md` gains one pointer line under Quality strategy.

## Consequences

One file owns test doctrine. A doctrine change is a one-place edit, and every
pointing skill inherits it. `bin/check` already validates that backticked
`global/references/...` pointers exist, so wiring mistakes fail the gate.

The `/quality tests` branch stays lean and domain-specific. Its heavy-class
detail does not re-enter the shared reference.

## Reversal condition

Revert to per-skill doctrine only when a shaped eval proves the shared
reference causes wrong routing: skills over-firing, tests judged against the
wrong branch, or premature completion. Do not revert only because the document
grows.
