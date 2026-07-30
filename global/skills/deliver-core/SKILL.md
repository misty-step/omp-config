---
name: deliver-core
description: Apply the harness-neutral delivery contract from live authority through exact proof.
disable-model-invocation: true
---

# Delivery contract core

This is the canonical, harness-neutral delivery contract. The consuming
harness adds only its card, role, routing, review, gate, and closeout surfaces
after loading this skill.

## Execute the contract

1. Read the live work card or other named authority, current repository
   contracts, relevant code, existing proof, and worktree state. The live
   authority outranks remembered context. Preserve concurrent user work.
2. Name the bounded observable outcome and the cheapest credible falsifier
   before editing. The falsifier MUST be able to show the requested behavior is
   still missing or wrong. If no executable oracle exists, stop and reshape the
   work rather than delivering an uncheckable change.
3. Identify the live verification driver that can exercise the changed surface
   for a future reviewer. Establish that driver before implementing when the
   outcome needs live proof and no driver exists.
4. Make the smallest coherent change at the highest-leverage owning layer.
   Reuse the repository's existing seam. Do not add unrelated behavior,
   abstractions, or compatibility shadows.
5. Apply clean cutover and erasure: migrate every caller, delete the replaced
   implementation, stale comments, obsolete configuration, dead tests, and
   superseded rules. Keep a compatibility path only when the authority
   explicitly requires it.
   Erasure removes what the new behavior made obsolete; it never removes the
   delivered change or the proof that defends it.
6. Exercise the live driver after each meaningful milestone and again after
   review fixes. A narrow unit check cannot substitute for the live path named
   by the acceptance oracle.

## Prove and close

- Send the finished artifact and observable outcome to an independent,
  fresh-context verifier or reviewer. Give it the diff and oracle, not the
  author's reasoning trail. Resolve every blocking finding and re-prove the
  affected behavior.
- Run the repository's required gate after the live behavior works. Do not
  weaken or bypass a gate to manufacture a pass.
- Record exact proof: the authority/card, changed paths, live entrypoint,
  commands or requests, observed result, review and gate dispositions, and any
  deviation from the contract. A green aggregate without its command and
  result is not proof.
- Record residual risk and unverified paths. State `none` for the deviation
  ledger only when no deviation occurred. Keep closeout durable in the
  authority's own system; chat alone is not completion evidence.
