---
name: field-station
description: Generate or refresh an evidence-backed repository field report.
disable-model-invocation: true
argument-hint: "[repository path] [internal|contributor|public]"
---

# Field Station

Compile one repository identity into an inspectable report. The report is a
derived view of evidence, never a replacement for source or human intent.
For a product-only request, populate the product capabilities and scenarios and
omit system or operations sections without material evidence.

## Bind

Resolve the repository, requested projection, output paths, prior report, and
prior `public.html`. Record the root, Git revision or non-Git identity, worktree
state, and dirty paths. A report is pinned only when one unchanged clean Git
HEAD supplies every cited tracked evidence file. Dirty, non-Git, or untracked
evidence produces an unpinned internal draft.

Publication is deny-by-default. A `public` report is an explicitly allowlisted
projection, never a redacted internal report.

## Survey

Read [`references/field-report.md`](references/field-report.md) before building
the model. Inspect evidence for:

- product entry points, users, capabilities, terminology, and visible outcomes;
- domain concepts, transitions, invariants, and ownership boundaries;
- runtime components, dependencies, external systems, and data flows;
- commands, configuration, deployment, observability, and recovery;
- tests, examples, recent movement, and source/documentation contradictions.

Trace one representative path end to end. Exercise a safe local surface when
available and record command, runtime identity, and observation. Preserve gaps.
Keep secrets, credentials, customer data, private endpoints, and unrelated
workspace state out of every artifact.

## Generate

Build the complete next generation in a sibling staging directory. Write
`report.json` first under the reference contract, classifying claims as
`observed`, `evidenced`, `human`, `inferred`, or `unknown`. Attach evidence
paths and lines to consequential claims and link observed claims to scenarios.
Preserve the prior observation only for change and staleness calculations.

Write a self-contained staged `index.html` from `report.json`. Read
`skill://frontend-design` and choose a visual thesis from the real domain.
Keep the page functional from `file://`: no build step, network, tracking, or
external fonts. Include only report sections containing real material.

Generate `public.html` only from the publication allowlist and only for a
pinned source. Exclude internal architecture, operations, configuration,
private dependencies, unknown vulnerabilities, and evidence paths unless the
operator explicitly approves the exact non-secret item. Never carry a stale
public artifact into the next generation.

## Verify and promote

Open staged HTML at desktop and mobile widths. Check hierarchy, contrast,
navigation, evidence links, claim agreement, trust state, source identity,
scenarios, contradictions, unknowns, and absence of secrets. Check pinned
generations for unchanged HEAD, clean source paths, and HEAD-tracked evidence.
Check unpinned drafts for an internal label, complete dirty paths, absent
`public.html`, and cited untracked or ignored evidence.

If a pinned source changes or a check fails, discard staging and restart from the
new state. Promote only a rechecked pinned generation through an atomic swap.
For an unpinned source, preserve `.field-station.draft-<timestamp>` and leave
current output intact.

Return report paths, source identity, projection, scenarios, material changes,
contradictions, unknowns, and publication state.
