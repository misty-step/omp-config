# OMP engineering doctrine

Phaedrus adopted the mandatory deletion-first order in `RULES.md` for OMP engineering and work management on 2026-08-13. This order is commonly called the Musk Algorithm. Use the order as a heuristic, not as authority.

## Hard systems review

Use the requested Torvalds lens only as a review method. Do not use the name as attribution or evidence. For each proposed layer, ask:

- Which exact outcome or invariant requires the layer?
- Which process, protocol, file system, environment, or library interface already supplies the required behavior?
- Why is direct use of that existing interface insufficient?
- Which state, authority, transition, failure mode, and operator task does the layer add?
- Can the layer disappear while the required outcome stays correct?

Use direct native interfaces. Do not build a wrapper that mirrors dependency configuration, state, or lifecycle. Add a framework only when measured evidence proves direct use insufficient.

## Whole-system simplicity

Judge the whole system, not one function or file.

- Give each datum one authority and one clear data path.
- Use explicit inputs. Avoid ambient personal state, implicit discovery, fallback chains, recursive copying, and mutable caches.
- When behavior stays correct, select a design that removes more production code, tests, configuration, state, failure paths, and operator work than it adds.
- Keep necessary external seams narrow. Keep secrets and host policy in deployment inputs. Keep deterministic product behavior product-owned.
- Add the smallest concrete path for an existing caller. Do not add flexibility for a hypothetical caller.
- Make invalid states difficult, failures local, and deletion easy when a requirement disappears.

Before you implement a subsystem, sketch a direct design and a deletion design. If a tool already supplies the required interface, use that interface and stop.

## Premise gate

Before production implementation, record:

- The required outcome and the accountable person or binding evidence source.
- The observed problem and baseline measurement.
- The part, process, or requirement that can be deleted.
- The cheapest experiment that can falsify the proposed mechanism.
- The whole-system success measure, stop criterion, unchanged behavior, and unchanged invariants.

Return the work to refinement when evidence invalidates the mechanism. Do not use implementation momentum as a reason to continue.

## Work controls

- Archive or close completed records. Before you delete obsolete, duplicate, unsupported, or solution-shaped work, preserve the rationale and evidence for that work.
- Keep one outcome item for each unresolved problem. Do not create a ticket only to triage other tickets.
- Record an invalidated hypothesis and its evidence before you remove its implementation item.
- Declare each dependency. Enforce the declared sequence or formally change it.
- Keep one active architecture hypothesis and one measurement effort. Do not run overlapping speculative programs.
- Rank deletion and direct correctness before consolidation, acceleration, or automation.
- Separate outcomes and invariants from proposed mechanisms.
- Attach each material constraint to a named person or binding evidence source.
- Use executable baselines and budgets for claimed efficiency work.
- Measure whole-system cost. Use tool, line, and abstraction counts only as supporting metrics.
- Prototype the riskiest assumption before you change all adapters or callers.
- State before implementation starts what evidence will stop the work.

## Review

Review the premise before the implementation. Review the implementation before delivery. Ask what can disappear while the required outcome stays correct. Treat an early stop as a successful experiment when it prevents a larger wrong change.
