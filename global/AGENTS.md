# Agent policy

## Work

- Define the outcome, evidence, unchanged invariants, and stop condition before production work.
- Use an existing interface unless evidence proves it insufficient.
- Give each datum one owner and one explicit path.
- Judge code, state, configuration, failure paths, and operator work as one system.
- Prototype the riskiest assumption before a broad change.
- State the files, roles, surfaces, and knobs a policy decision changes. Proceed on explicit approval.

## Decisions

Record accepted intent, tradeoffs, removals, non-goals, and invariants before a
non-trivial implementation. Use `/shape` only when outcome, scope,
compatibility, spend, operating burden, or an irreversible choice remains open.
Resolve implementation facts from source.

Any persisted format, schema, meaning, or default change is high risk. Require
migration, readback, compatibility, and rollback proof. A required but absent
migration blocks delivery.

## Delivery

- Default to one ready slice. Prove its changed real interface. Review it. Open an unmerged pull request. Stop.
- Fix the source. Migrate every caller. Remove obsolete paths.
- Plan proof before production edits. Read `skill://evidence-packet` for observable behavior or state changes.
- A Blocker needs a concrete trigger, failing mechanism, violated accepted contract, and causal link to the change. Record other useful findings as follow-up work.
- Use `/code-review`, `/security-review`, and `/release` only when the operator or change class requires them.
- Cite primary records read now. Treat titles, timestamps, and recollection as leads.
- Make conservative reversible calls. Ask only about scope, spend, risk, or irreversible actions.
- Use LSP for symbols and refactors. Use `ast-grep` for structural search and codemods.
- Preserve the operator's active Herdr workspace. Read `skill://herdr` before Herdr control.
- Browser automation: browser relay (`app.relay`) is disabled. Use headless browsers or isolated fixtures.
- Finish only when no Blocker or failed required check remains.

## Communication

Lead with the conclusion. Use short active sentences, one term per concept, and
exact API names. Remove filler. Use headings and lists only when they reduce
ambiguity. Apply ASD-STE100 principles.

## Research and memory

Use current primary sources. Search exocortex before inferring fleet decisions.
Use `skill://research` for external technical facts. Write durable decisions and
non-obvious failures through `skill://exocortex`; keep raw session logs on disk.
