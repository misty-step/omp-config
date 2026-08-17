---
name: orient
description: Orient to the current work and give me a compact status update.
disable-model-invocation: true
---

# Orient

## 1. Orient

Inspect the conversation, task state, relevant workspace state, and latest verification. Use current evidence instead of memory. Mark an inference when direct evidence is unavailable.

Completion criterion: The completed work, current state, next actions, blockers, and material unknowns are accounted for.

## 2. Update

Return one to three short paragraphs with these bold labels:

- **Done:** State completed outcomes and their decisive verification.
- **Now:** State the current condition, active work, and any blockers.
- **Next:** State the immediate actions in order and the next completion condition.
- **Need to know:** State material risks, surprises, failed checks, assumptions, decisions, and unknowns. Omit this label when none apply.

Use ASD-STE100 style. Use short, direct, active-voice sentences. Use one term for each concept. Define an unavoidable unfamiliar term. Keep procedural sentences to 20 words and descriptive sentences to 25 words. Preserve exact identifiers and error text when they help the operator act.

Include only facts that change the operator's understanding or decisions. Start with **Done**. Return only the update. Add a Mermaid diagram after the prose only when it clarifies a non-trivial sequence, dependency, or state.

Completion criterion: The update covers **Done**, **Now**, and **Next**, stays within three paragraphs, and exposes every material fact.
