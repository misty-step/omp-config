---
name: audit-choices
description: Expose consequential choices an implementation made without accepted intent.
disable-model-invocation: true
license: MIT; from dzhng/skills audit-choices
argument-hint: "[change or target]"
---

# Audit choices

This audit is read-only and non-blocking.

Read the accepted intent and the named implementation scope. Report only choices
where the available evidence allowed materially different product, compatibility,
cost, operating, or irreversible outcomes. Ignore routine implementation,
style, and hypothetical alternatives.

For each choice, state the evidence, implemented answer, consequence, and
whether it follows accepted intent or needs an operator decision.

Return the material choices and the smallest question that settles each open
one. Suggest `/shape` only when repeated ambiguity points to a missing decision.

Done when no reported choice is merely taste.
