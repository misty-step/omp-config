---
name: product-description
description: Describe and verify the user-visible contract of a software product.
disable-model-invocation: true
argument-hint: "[product or surface]"
---

# Product description

Describe what a user can observe, to the depth needed to understand or change
the product.

## Scope

Name the product, users, surface, source revision, included behavior, output
location, and verification access. Infer available facts from source before
asking.

Done when the useful boundary of the description is explicit.

## Describe

For each material feature, record its purpose, entry point, common path, visible
states, user actions, outcomes, and unresolved questions. Add persistence,
errors, recovery, interruptions, accessibility, variants, or a state diagram
only when that feature owns those behaviors.

Use consistent product language. Keep implementation detail only when it changes
what the user observes.

Done when the documents cover the selected user-visible contracts without
empty template sections.

## Verify

Exercise uncertain or consequential claims on the running product. Mark what was
observed, source-proven, inferred, or unavailable. Record suspected defects
once, with a reproduction when available.

Return the documents, verified revision or runtime identity, evidence gaps, and
confirmed discrepancies.

Done when each stated contract is supported or carries an explicit gap.
