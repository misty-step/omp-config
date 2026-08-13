# OMP engineering doctrine

## Five-step engineering algorithm

Phaedrus adopted this deletion-first order, commonly called the Musk Algorithm, for OMP engineering and work management on 2026-08-13. Treat it as a heuristic, not an appeal to authority.

1. **Challenge requirements.** Treat every requirement as potentially wrong. Cite the accountable human and rationale when one exists. Otherwise cite the binding source, such as law, protocol, production evidence, or a code invariant. Never invent attribution. Treat unsupported requirements as hypotheses that need clarification or evidence.
2. **Delete first.** Try to remove the feature, component, abstraction, compatibility path, process, test, ticket, or step. Restore a deletion when evidence proves it necessary. If fewer than 10 percent of attempted deletions need restoration, challenge more aggressively.
3. **Simplify second.** Simplify or optimize only the necessary system that remains. Never perfect an interface, process, or implementation that should not exist.
4. **Accelerate third.** Reduce cycle time only after the requirement and direction survive challenge. Faster execution increases waste when the premise is wrong.
5. **Automate last.** Automate only a stable, necessary, measured process. Automation must not preserve ambiguity, workaround paths, duplicate authority, or process waste.

The order is mandatory. Later steps never justify skipping earlier steps.

## Hard systems review

Use the requested "Torvalds" lens as a hard systems-review method, not as an invented attribution or a substitute for evidence. For each proposed layer, ask:

- What exact outcome or invariant requires it?
- Which existing process, protocol, filesystem, environment, or library interface already carries the required behavior?
- Why is direct use of that interface insufficient?
- What state, authority, transition, failure mode, and operator task does the layer add?
- Can the layer disappear while the outcome remains correct?

Prefer direct native interfaces over wrappers that mirror a dependency's configuration, state, or lifecycle. Never build a framework around an existing interface unless measured evidence proves that the direct boundary is insufficient.

## Simplicity and elegance

Judge simplicity across the whole system, not inside one function or file.

- Prefer one authority for each datum and one obvious data path.
- Prefer explicit inputs over ambient personal state, implicit discovery, fallback chains, recursive copying, and mutable caches.
- When behavior remains correct, prefer the design that removes more production code, associated tests, configuration, state, failure paths, and operator work than it adds.
- Keep necessary external seams narrow. Secrets and host policy remain deployment inputs; deterministic product behavior remains product-owned.
- Do not add flexibility for a hypothetical caller. Add the smallest concrete path when the caller exists.
- An elegant design makes invalid states difficult, failures local, and deletion easy when a requirement disappears.

Before implementing a new subsystem, sketch the direct design and the deletion design. If the underlying tool already exposes the required interface, use it and stop.

## Premise gate

Before a production implementation, record:

- The required outcome and its accountable human or binding evidence source.
- The observed problem and baseline measurement.
- The part, process, or requirement that can be deleted.
- The cheapest experiment that can falsify the proposed mechanism.
- The whole-system success measure and kill criterion.
- The behavior and invariants that must remain unchanged.

Return the work to refining when evidence invalidates its mechanism. Do not preserve implementation momentum as a reason to continue.

## Grooming rules

- Archive or close completed records. Delete only obsolete, duplicate, unsupported, or solution-shaped work after preserving its rationale and evidence.
- Keep one outcome item for each unresolved problem. Do not create a ticket only to triage other tickets.
- Record an invalidated hypothesis and its evidence before removing its implementation item.
- Require explicit dependencies. Enforce or formally change the declared sequence.
- Keep one active architecture bet and one measurement lane. Do not run overlapping speculative programs.
- Rank deletion and direct correctness work before consolidation, acceleration, or automation.

## Specification rules

- Separate outcomes and invariants from proposed mechanisms.
- Attach each material constraint to a named human or binding evidence source.
- Use executable baselines and budgets for claimed efficiency work.
- Measure whole-system cost. Tool count, line count, and abstraction count are supporting metrics only.
- Prototype the riskiest assumption before changing all adapters or callers.
- State what evidence stops the work before implementation starts.

## Review rules

Review the premise before the implementation and the implementation before delivery. Ask what can disappear while behavior remains correct. Treat an early stop as a successful experiment when it prevents a larger wrong change.
