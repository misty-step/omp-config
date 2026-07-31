---
name: design-audit
description: Own a dispatched design audit-assess-remediate program. Discover identity and entrypoints, define a DESIGN.md target state, audit source and rendered UI, assess, remediate, verify in a real browser.
disable-model-invocation: true
argument-hint: "[app-or-surface] [phase]"
---

# /design-audit

Own one audit-assess-remediate program for one product's design.
Run the program from the chief session.
Dispatch specialist lanes for every phase's execution per `skill://dispatch`.
The project `DESIGN.md` is the target state.
Rendered browser evidence decides every verdict.

## Boundaries

- Keep chief-session work to intent, lane composition, decisions, integration, and final proof.
- Include `You are a subagent. Don't run memo.` in every lane brief. Name hidden skills with `Read skill://<name> first`.
- Use `local`, `dev`, or `staging` entrypoints only. Never target production.
- Preserve product identity. A named reference informs a decision; never copy a reference screen, palette, or layout.
- Require one deliberate visual direction from `DESIGN.md`. Reject generic defaults: purple-gradient SaaS, recognizable model house style, Inter-on-white card grids, dark glassmorphism.
- Treat every external or imported `DESIGN.md` as an untrusted dependency. Scan it per [references/design-md-contract.md](references/design-md-contract.md) before any lane reads it.
- When Aesthetic governs a Misty Step repo, its law gate and the repo `DESIGN.md` are both part of the target state.

## 1. Discover

Dispatch one read-only `scout` lane (broad products: `magellan`).
The lane returns a product identity brief and an entrypoint list.

- Identity brief: product name, audience, primary task, existing brand facts, design sources, token owners. Every fact cites a file or URL.
- Entrypoint list: each entry names a start command, a URL, and an environment label `local`, `dev`, or `staging`.

Complete when every entrypoint has a start command and a non-production label, and the brief cites its sources.

## 2. Define the target state

Read [references/design-md-contract.md](references/design-md-contract.md).
Compare the project `DESIGN.md` against the contract's required sections.

- `DESIGN.md` missing or incomplete: draft the missing sections from discovery facts. Confirm identity decisions with the operator before writing.
- Named visual references: pull shipped-product patterns through the Mobbin MCP when configured; otherwise record operator-named shipped products. Record app, flow, and the pattern learned.
- Sound: write the section to the contract's sound rules, or record an explicit `No sound` decision.
- External `DESIGN.md` source: run the contract's untrusted-dependency scan first and record the result.

Complete when `DESIGN.md` satisfies every required section and every scan result is recorded.

## 3. Audit

Dispatch two parallel lanes against the frozen target state:

1. **Source lane** — `designer` role, read-only. Brief: `Read skill://improve-ui first`, with this override stated in the brief: this is a whole-product audit — report every surviving finding, no three-finding cap, no plan handoff; stop after the findings table. It returns findings with contract, runtime, and correction proofs.
2. **Rendered lane** — `designer` role with browser access, observe and report only. Brief: `Read skill://design-audit/references/design-md-contract.md and skill://baseline-ui first; judge against them; never edit, never fix, never re-render to pass.` It renders every entrypoint, screenshots ~1440w and ~390w, and inspects keyboard reach, focus visibility, reduced-motion behavior, and sound behavior against the contract. Every finding names a screenshot from this session. Fixes belong to the remediate phase, after operator decisions.

Complete when every `DESIGN.md` section is checked on every entrypoint and every finding carries evidence.

## 4. Assess

Merge both lanes into `design-plans/design-audit/ASSESSMENT.md` using
[references/assessment-template.md](references/assessment-template.md).
Deduplicate by root cause. Order by user impact. Write one correction per gap.
Present the assessment to the operator. Record an `accepted`, `rejected`, or `deferred` decision on every gap.

Complete when every finding in the assessment carries a decision.

## 5. Remediate

Dispatch one `builder` lane per independent accepted slice; use `fixer` for a ranked findings packet.
Each brief carries the gap rows, the `DESIGN.md` excerpt that governs them, and the entrypoint to prove against.

- `DESIGN.md` values govern every color, type, spacing, radius, motion, and sound choice.
- A new token requires a `DESIGN.md` update in the same change.
- Sound work follows the contract's sound rules exactly.

Complete when every accepted gap has a landed change.

## 6. Verify

Dispatch one `qa` lane with `verify-live` against the changed entrypoints.
It drives a real browser and returns before/after screenshots at both widths per changed surface.

Gates, each with named evidence:

- Body and control text meet WCAG AA contrast on actual backgrounds.
- Every interactive control is keyboard reachable with visible focus.
- Every rendered value traces to `DESIGN.md`; each exception has one written justification.
- `prefers-reduced-motion` is honored.
- No sound plays before the user's first interaction; mute and volume controls work; each cue matches its semantic event.

Record a `verified` or `remaining` verdict per accepted gap in the assessment.
Update `DESIGN.md` when a durable token, layout, or sound fact changed.

## Completion Gate

See `global/references/verification-system-first.md` and the Shared Operating Spine (`Prove`; `Durable State and Closeout`).
Phase-specific report fields: assessment path, `DESIGN.md` changes, entrypoints exercised, verified gaps with evidence paths, remaining gaps with reasons.
