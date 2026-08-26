---
name: frontend-design
description: Build or refine a UI through one product-specific visual direction and browser critique.
license: Apache-2.0; modified from Anthropic's frontend-design skill
---

# Frontend design

A strong interface expresses the product's hierarchy and interaction model. It
is not a collection of fashionable effects.

## Direct

Inspect the real surface, content, users, states, and existing design system.
State one visual thesis: hierarchy, typography, spacing, color, motion, and the
one distinctive product idea. Preserve functional contracts.

Done when the direction explains every major visual choice.

## Build

Reuse current primitives. Add dependencies only when the direction requires
capability the current system lacks. Implement responsive, accessible states
with complete content and interactions. Avoid decorative effects that weaken
hierarchy or performance.

Done when the affected surface works at its real route.

## Critique

Run the UI headlessly at desktop and mobile sizes. Exercise primary interaction
with keyboard and pointer. Inspect screenshots for hierarchy, clipping,
contrast, rhythm, focus, loading, empty, error, and reduced-motion behavior.
Repair the source and repeat.

Done when the real surface supports the thesis and its required states.
