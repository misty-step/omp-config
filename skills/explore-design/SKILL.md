---
name: explore-design
description: Compare at least six distinct production-grade UI directions for one surface.
disable-model-invocation: true
argument-hint: "[component, page, or product surface]"
---

# Explore design

One polished mock hides alternatives. A catalog makes product taste and
interaction tradeoffs visible before implementation.

## Ground

Inspect the real surface, user, jobs, content, states, constraints, and current
design system. Identify the data and interactions every direction must support.

Done when all directions share one functional contract.

## Diverge

Define at least six distinct theses across information density, navigation,
interaction model, visual hierarchy, and tone. Each thesis states its user
benefit and tradeoff. Cosmetic variants do not count.

Build each direction with plausible content and the same important states.
Parallelize only independent directions. Keep production code unchanged.

Done when six directions differ in structure or interaction, not color alone.

## Compare

Assemble one self-contained HTML catalog in an OS temporary path. Let the
operator view every direction under the same viewport and state. Include a
short table of thesis, strength, risk, and implementation cost.

Present selection, rejection, or combination choices. After selection, return
the chosen interaction rules, design tokens, and production handoff for
`/frontend-design` or `/deliver`.

Done when all directions open and the selected direction is specific enough to
build.
