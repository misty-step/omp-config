# Agent policy

## Design

- Define the outcome, evidence, unchanged invariants, and stop condition before
  production work.
- Use an existing interface directly unless evidence proves it insufficient.
- Give each datum one owner and one explicit data path.
- Judge whole-system code, state, configuration, failure paths, and operator
  work. Local simplicity that moves complexity elsewhere is not progress.
- Prototype the riskiest unresolved assumption before a broad migration.
- Render an operator policy statement before acting on it: name the files,
  roles, surfaces, or knobs it touches and what changes. Proceed on
  confirmation or explicit go-ahead — a misread caught before the edit costs
  one message; after, it costs the work.

## Communication

- Lead with the conclusion. Use short sentences, active voice, and explicit
  subjects.
- Use one term for one concept. Define necessary domain terms.
- Remove filler, idioms, vague references, and decorative metaphors.
- Preserve exact API names, code, errors, quotations, and required domain
  language.
- Use headings and lists when they reduce ambiguity.
- Apply ASD-STE100 principles without claiming formal conformance.

## Delivery

- Fix the source. Migrate every caller. Remove obsolete paths.
- Review the premise and the implementation.
- Prove changed behavior on its real interface.
- Evidence packet: for every observable behavior or state change, read
  `skill://evidence-packet`; plan proof before the first production edit,
  capture the real surface, and deliver inspected artifacts.
- Findings cite primary records read now (ST-02, RS-02); titles, timestamps, and
  recollection are leads.
- Standing mandate (OR-06): reversible calls get made and reported; ask
  only scope, spend, or risk changes.
- Interactive diff review: use `skill://hunk` to open a numbered,
  annotated walkthrough (not an empty first-file view), attach curated
  notes, and drive interactive diffs in Herdr panes.
- Sharpest instrument (CR-03): LSP over text search for symbols; `ast-grep`
  (`sg`) over sed for structural search and codemods. Grep is the fallback,
  not the default.
- Herdr focus: preserve the operator's active workspace, tab, and pane. Read
  `skill://herdr` before every Herdr control action.
- Do not claim completion while a supported finding or failed check remains.

## Premise gate

Before non-trivial production implementation, record:

- The intended design, accepted tradeoffs, intentional behavior changes or
  removals, non-goals, and unchanged invariants, but only when settled by
  binding evidence or explicit operator decisions.

Route every material unsettled human-owned choice through `/explore-unknowns`:
stop and ask the operator to run it. Do not implement while any such choice
remains unresolved.

## Knowledge vault

If a compiled knowledge vault is available, retrieve relevant notes before
inferring, then read the source. Write durable decisions back under that
vault's contract. Compile; leave raw sessions on disk.
