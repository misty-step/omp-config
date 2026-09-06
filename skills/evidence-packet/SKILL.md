---
name: evidence-packet
description: Prove an observable claim through one real scenario and result.
---

# Evidence packet

Connect one claim to the smallest real scenario that could disprove it.

Record the claim, entry point, fixture, and expected observation before editing.
Capture a baseline only for a fix, comparison, state change, or performance
claim.

Repeat the scenario through the real interface after the change. Record actions,
observed result, and enough source or runtime identity to remove ambiguity. Read
final state from its owner when persistence matters.

Create media or a saved artifact only when it helps inspection or publication.
Open it before delivery and remove secrets, customer data, and unrelated state.
When GitHub is the review surface and `gh` v2.99.0+ has write access, attach
sanitized media with `gh pr create --attach`, `gh pr comment --attach`, or
`gh issue comment --attach`, and record the exact head. If no supported review
surface can publish required visual evidence, report that gap.

Return the proved claim and observation, plus any unproved claim and its exact
evidence gap.
