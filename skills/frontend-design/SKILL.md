---
name: frontend-design
description: Design, materially revise, or polish a UI with a product-specific visual system and browser critique.
license: Apache-2.0; modified from Anthropic's frontend-design skill
---

# Frontend Design

Create one coherent visual direction for the product.

## Ground

Inspect the real surface, content, brief, and existing design system. Identify:

- audience and primary job;
- brand and platform constraints;
- current components, tokens, and accessibility requirements.

Use the existing system when it fits. When the brief leaves an axis open, choose
it and state the reason.

## Direct

Before code, define:

- **Thesis:** the product-specific visual idea.
- **Color:** 4–6 functional tokens.
- **Type:** display, body, and utility roles.
- **Layout:** hierarchy; add a wireframe only when structure is unresolved.
- **Signature:** one memorable product-specific element.
- **Motion:** one justified moment, or none.

Reject a direction that fits an unrelated product unchanged. Use cards,
numbering, dividers, gradients, and animation only when they carry meaning.

## Build

Reuse current primitives. Add a framework, font, dependency, or abstraction only
when the direction requires it and current interfaces cannot supply it.

Spend boldness once. Remove decoration that does not clarify hierarchy, state,
or action. Use direct labels, actions, errors, and empty states.

Preserve:

- responsive narrow and wide layouts;
- keyboard operation and visible focus;
- semantic structure, contrast, and reduced motion;
- visible interactive states without overflow.

## Critique

Run the UI in a browser at desktop and mobile sizes. Exercise the primary
interaction with keyboard and pointer. Compare the result with the thesis and
brief. Fix the visible defects; source inspection is not proof.
