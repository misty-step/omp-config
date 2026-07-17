# ui-skills.com import — 3-lane fidelity smoke — 2026-07-17

Purpose: philosophy-roster regression required by `bench-eval.md`, run once per
newly vendored philosophy before it enters the Bench table. Three focused
blind lane-fidelity smokes, not a whole-bench capability verdict. Each cold
lane received only its fixture, the artifact output shape, and its one
philosophy `SKILL.md` — no sibling context, no shared reasoning trail.

## Source

Swept ui-skills.com's full registry (~120 entries) against the existing
11-lane Bench roster. 3 non-redundant additions vendored via
`primitives/skills/.external/registry.yaml`: `zeke-swiss-design`,
`dammyjay-interface-design`, `danilaa-compact-landing`. 5 candidates evaluated
and rejected with reasons (audit/linter redundant with `emil-review-animations`,
commercial lead-gen wrapper, near-verbatim redundant with existing lanes, two
dead links with territory already covered by `leon-brutalist-skill`) — not
vendored.

## Lane 1: `zeke-swiss-design`

Fixture: header + hero for a Rust CLI docs site (`ferrule`, an OCI image diff
tool). Fixed: real product, light+dark.

Artifact: exact IBM Plex Sans stack per skill (no substitution); stone-scale
tokens used at opacity only (`/70`, `/40`) — zero mid-scale stone hues; Cobalt
`#003B8E` chosen as the single accent with skill-consistent reasoning (Swiss
Red rejected as "shouting" for a trust-signaling tool); asymmetric 7/5 grid
split named as the Swiss move over a centered hero; `font-light` headings,
`tabular-nums`, curly quotes, `rounded-none` throughout (skill gotchas
honored). One-line self-test: "structure *is* the design, so the grid and the
whitespace read before any color does."

Verdict: **PASS**. Lane obeys the opacity-only hierarchy rule, the one-accent
rule, and the rectilinear-geometry gotcha precisely; output is recognizably
Swiss International Style, not a generic clean page.

## Lane 2: `dammyjay-interface-design`

Fixture: main dashboard for an on-call incident-response tool. Fixed: real
product, light+dark.

Artifact: full Product Domain Exploration (8 domain concepts, 7 world-sourced
colors, one named signature — "the page pulse," a severity-keyed breathing
indicator unique to a pager product) plus all 3 named defaults explicitly
refused with alternatives. Mandatory checkpoint block filled (Intent /
Hierarchy / Palette / Depth / Surfaces / Typography / Spacing), each with a
stated WHY. Ran the philosophy's own self-checks (swap/squint/signature/token
tests) and passed all four.

Verdict: **PASS**. Lane correctly refuses the generic Kanban-board/stat-grid
defaults it was trained on and produces a focal-element hierarchy with six
compounding, named wins — the exact "why" discipline the skill mandates.

## Lane 3: `danilaa-compact-landing`

Fixture: landing page for a curl-to-typed-client-code CLI tool. Fixed: real
product, light+dark.

Artifact: Pocket Console direction family chosen, then explicitly mutated
against the skill's own stated canonical-recipe default at four-plus axes
(measure 620px not 440px, condensed-sans+mono not Geist+Geist Mono, machined
low-radius not the 6-10px balanced default, scan-reveal not staggered rise).
Product-native signature artifact named and described in full (a live
curl→typed-code console with a language-selector rail). Zero-shift motion
rules correctly applied — fixed-height panes, transform/opacity only, gated
under `prefers-reduced-motion`.

Verdict: **PASS**. Lane demonstrates the fingerprint methodology itself
(mutate axes, name the divergence), not just a static aesthetic — the
distinguishing behavior of this philosophy versus a fixed style guide.

## Structural gate

`cargo run --locked -p roster-cli -- check`: `ok (748 primitive files)`.
Alias uniqueness confirmed (`zeke-`, `dammyjay-`, `danilaa-` each single-use).
`primitives/skills/design/SKILL.md` and
`~/.omp/agent/skills/design/SKILL.md` (omp-config projection) confirmed
byte-identical after edit; same for `references/external-design-references.md`.

## Result

All three lanes: **PASS**. Bench table and external-design-references.md
updated in both the Roster source and the live omp-config projection (no
`sync` command exists post-v0.2; edits applied identically by hand and diffed
to confirm parity).
