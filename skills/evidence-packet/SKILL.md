---
name: evidence-packet
description: Prove an observable claim through one real scenario and result.
---

# Evidence packet

Connect one claim to the smallest real scenario that can disprove it.

Before editing, record the claim, entry point, fixture, and expected observation.
Capture a baseline only for a fix, comparison, state change, or performance
claim.

After the change, repeat the scenario through the real interface. Record the
actions, observed result, and enough source or runtime identity to avoid
ambiguity. Read final state from its owner when the claim concerns persistence.

Create media or a saved artifact only when it helps another person inspect the
claim or the operator requests publication. Open it and remove secrets, customer
data, and unrelated state before delivery.

When an observable claim depends on visual proof or recordings and GitHub is the
review surface, attach sanitized media directly with
`gh pr create --attach path/to/media.png#Alt`, `gh pr comment --attach`, or
`gh issue comment --attach` (local Markdown references rewrite in place). Record
the exact head revision beside the claim in the PR or comment.

Publish a sanitized authenticated here.now Site (`skill://here-now`) for that
exact head when the observable claim depends on an interactive web application,
live HTML artifact, external review without GitHub repository access, or
non-GitHub platforms. Record the head on the Site and in the PR/record. Use
`anyone_with_link` so an external reviewer needs no account. Open the live URL
without publisher credentials before linking. If publish is unavailable, the
PR has an evidence gap until the operator publishes or waives.

Return the proved claim and observation. Name any unproved claim and the exact
evidence gap.

Done when the claim is proved on the real surface or explicitly remains open.
