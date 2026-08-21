# Agent policy

## Design

- Define the outcome, evidence, unchanged invariants, and stop condition before
  production work.
- Use an existing interface directly unless evidence proves it insufficient.
- Give each datum one owner and one explicit data path.
- Judge whole-system code, state, configuration, failure paths, and operator
  work. Local simplicity that moves complexity elsewhere is not progress.
- Prototype the riskiest unresolved assumption before a broad migration.

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

- Build quality into the codebase. Prefer sound state and module design,
  types, behavioral tests, local run paths, hooks, CI, and release controls
  over agent reminders.
- Keep changes cohesive and reviewable. No huge fucking PRs; split
  independent outcomes and leave unrelated cleanup out.
- Use the repository's own path to green. Run every affected application
  locally and prove changed behavior through its real interface.
- Attach inspected evidence for observable changes (`skill://evidence-packet`;
  plan proof and capture baselines before the first production edit). Review
  the complete result; fix supported in-scope defects at the source,
  migrating every caller; rerun affected proof; open an annotated Hunk
  walkthrough for non-trivial changes (`skill://hunk`).
- Delivery agents leave pull requests unmerged. Merge and deployment require
  a separate, explicitly requested release gate.
- Herdr focus: preserve the operator's active workspace, tab, and pane. Read
  `skill://herdr` before every Herdr control action.
- Do not claim completion while a supported finding or failed check remains.

## Premise gate

Before non-trivial production implementation, record:

- The intended design, accepted tradeoffs, intentional behavior changes or
  removals, non-goals, and unchanged invariants, but only when settled by
  binding evidence or explicit operator decisions.

Route every material unsettled human-owned choice through `grilling`. Do not
implement while any such choice remains unresolved.

## Knowledge vault

If a compiled knowledge vault is available, retrieve relevant notes before
inferring, then read the source. Write durable decisions back under that
vault's contract. Compile; leave raw sessions on disk.
