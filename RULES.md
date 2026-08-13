# Deletion-first engineering order

Apply these steps, in order, to each requirement, design, backlog item, process, refactor, and automation. A later step does not justify skipping an earlier step.

1. **Challenge requirements.** Treat each requirement as potentially wrong. Cite the accountable person and rationale. If no accountable person and rationale exist, cite binding evidence such as law, protocol, production evidence, or a code invariant. Do not invent attribution. Treat unsupported requirements as hypotheses that need clarification or evidence.
2. **Delete first.** Try to delete each feature, component, abstraction, compatibility path, process, test, ticket, or step. Prefer removal to repair. Restore a deleted item only when evidence proves the item necessary. If fewer than 10 percent of attempted deletions need restoration, challenge more aggressively.
3. **Simplify second.** Simplify or optimize only the necessary system that remains. Do not perfect or optimize an interface, process, implementation, component, or workflow that should not exist.
4. **Accelerate third.** Reduce cycle time only after the requirement and direction survive challenge and deletion. Do not accelerate an unproven path. Speed increases waste when the premise is wrong.
5. **Automate last.** Automate only a stable, necessary, measured process. Do not automate waste, ambiguity, workaround paths, duplicate authority, or process waste.

For system design, use an existing interface directly unless evidence proves direct use insufficient. Use one authority and explicit inputs. Minimize whole-system code, state, configuration, failure paths, and operator work. Reject ambient personal state, recursive configuration inheritance, fallback chains, and speculative compatibility.
