# After the Walk

The map lives on past planning. Three moves for the phases that follow.

- **Implementation notes** (during the build) — keep a running log; every
  time the code forces a deviation from the plan, record what the plan said,
  what the code revealed, and the call made. Triage by reversibility: a
  two-way-door deviation takes the conservative reversible call and keeps
  going; anything material or hard to reverse — a human-owned tradeoff, an
  irreversible write, a scope change — stops and comes back to the map before
  work continues, tagged for the operator. Each deviation is an unknown
  unknown that escaped the walk — fold it back into the map for attempt #2.
- **The buy-in doc** (before shipping) — other people inherit your unknowns;
  package prototype, spec, and notes into one skimmable pitch that leads with
  a demo, pre-answers each reviewer's objections with evidence, and names who
  signs off on what.
- **Quiz before merge** (before merging someone else's or a long diff) — a
  merge-readiness report — mental model, non-obvious behaviors introduced,
  what to watch after deploy — ending in a quiz the user must pass; wrong
  answers point back to the section they skimmed.
