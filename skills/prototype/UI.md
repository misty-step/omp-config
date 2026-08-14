# UI Prototype

Read `frontend-design`. Build competing structures for one unresolved visual or
interaction question.

## Host

Prefer an existing page with real navigation, data, density, and constraints.
Replace only a read-only rendered subtree in a disposable branch or worktree.
Otherwise use a prototype-only route that cannot enter a production build.

Keep prototype controls away from production mutations.

## Vary

Build three variants, at most five. Each must differ in structure, hierarchy, or
primary interaction. State its thesis, primary action, hierarchy, and main cost.

Use existing components and tokens when they fit. Do not force variants through
one shared layout.

## Switch

Use a shareable `?variant=` value and a separate fixed switcher with:

- previous and next controls with wraparound;
- current key and name;
- left and right keyboard controls outside editable fields;
- visible focus and sufficient contrast.

## Prove and dispose

Run every variant at desktop and mobile sizes. Exercise the primary interaction
with keyboard and pointer. Capture comparison screenshots.

After selection, remove every variant, switcher, query branch, prototype route,
and isolated state. Implement and verify the chosen design normally.
