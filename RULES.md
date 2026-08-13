# Deletion-first engineering order

Apply this order to every requirement, design, backlog item, process, refactor, and automation.

1. **Challenge requirements.** Treat every requirement as suspect. Cite an accountable human or a binding evidence source. Never invent attribution. Treat unsupported requirements as hypotheses.
2. **Delete first.** Test whether each part, process, abstraction, compatibility path, ticket, or feature should exist. Prefer removal over repair. If fewer than 10 percent of deletions need restoration, test more deletions.
3. **Simplify second.** Simplify or optimize only what survives deletion. Never optimize a component or workflow that should not exist.
4. **Accelerate third.** Shorten cycle time only after the direction survives challenge and deletion. Never move faster on an unproven path.
5. **Automate last.** Automate only a stable, measured, necessary process. Never hardwire waste, ambiguity, or a workaround.

For system design, use an existing direct interface unless evidence proves it insufficient. Prefer one authority, explicit inputs, and the smallest whole-system code, state, configuration, failure, and operating surface. Reject ambient personal state, recursive configuration inheritance, fallback chains, and speculative compatibility.
