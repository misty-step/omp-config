---
name: field-station
description: Generate or refresh an evidence-backed, beautiful repository field report.
disable-model-invocation: true
argument-hint: "[repository path] [internal|contributor|public]"
---

# Field Station

Turn one repository at one source identity into an inspectable field report: part
product narrative, part system atlas, part operating guide, and part knowledge
base. The report is a derived view of current evidence, never a replacement for
source or human intent.

## Bound the expedition

Resolve the target repository from the argument or current directory. Default
to the `internal` projection and `.field-station/` output directory. Record the
repository root, Git revision or non-Git identity, requested projection, output
paths, whether a prior report exists, and whether a prior `public.html` exists.
Record whether the worktree is clean and list dirty paths, excluding generated
output, staging, and retained draft paths. A report is pinned only when it uses
one unchanged clean Git HEAD and every repository file cited as evidence is
tracked by that HEAD. Dirty and non-Git sources, and reports that cite untracked
or ignored files, are unpinned internal drafts; they cannot replace current
output or become public projections.

Do not publish or widen access unless the operator explicitly requests it. A
`public` report is a separate allowlisted projection, not a redacted internal
report.

Done when the target, source state, requested projection, previous artifacts,
output paths, and publication boundary are explicit.

## Survey current evidence

Read [`references/field-report.md`](references/field-report.md) before building
the model. Inspect evidence rather than documenting the directory tree:

- product entry points, user-visible capabilities, and real terminology;
- domain concepts, state transitions, invariants, and ownership boundaries;
- runtime components, dependency direction, external systems, and data flows;
- commands, configuration, deployment, observability, and recovery paths;
- tests and examples that reveal supported behavior;
- recent movement since the previous source identity, when available;
- contradictions between implementation, documentation, configuration, and
  runtime behavior.

Trace at least one representative path end to end. Exercise the real product
when a safe local path exists; capture the command, runtime identity, and
observation. If execution is unavailable, preserve the gap instead of replacing
it with inference.

Keep secrets, credentials, customer data, private endpoints, and unrelated
workspace state out of every artifact.

Done when each material capability, concept, component, and operational claim
has evidence, an explicit inference, or an explicit unknown.

## Build the repository model

Create a sibling staging directory for the complete next generation. Write its
`report.json` first using the contract in `references/field-report.md`. Separate:

- `observed`: exercised on a real surface;
- `evidenced`: directly supported by current repository artifacts;
- `human`: intent explicitly supplied by a maintainer;
- `inferred`: synthesis that is not directly asserted;
- `unknown`: missing or conflicting evidence.

Attach repository-relative evidence paths and line ranges to consequential
claims. Link every `observed` claim to the scenario that established it.
Preserve the prior observation only to compute change and staleness; never let
generated prose outrank current evidence. Mark changed dependencies stale until
re-observed or re-evidenced.

Done when the JSON parses, names its source identity, contains no unsupported
fact presented as observed, links every observed claim to a scenario, and
exposes contradictions and unknowns rather than smoothing them over.

## Render the field report

Read `skill://frontend-design`, then write a self-contained staged `index.html`
from the staged `report.json`. Use one product-specific visual thesis derived
from the repository's actual domain. Optimize for progressive
disclosure: a ten-minute product and system briefing at the top, exact evidence
at the bottom of each path.

The HTML must work from `file://` without a build step, network dependency,
tracking, or external font. Include the sections required by the report
contract only when they contain real material. Provide keyboard navigation,
visible focus, semantic landmarks, responsive layouts, reduced-motion support,
and printable output.

Only when the source is pinned, write staged `public.html` from the publication
allowlist. Otherwise omit `public.html` and record that the requested public
projection was refused. Exclude internal architecture, operations,
configuration, private dependencies, unknown vulnerabilities, and evidence
paths unless explicitly approved. If an existing `public.html` is not
regenerated for the current source identity, omit it from the staged generation.
Never carry a stale public artifact into the next generation.

Done when the report is legible as a product story, useful as an engineering
map, and every trust state can be inspected without reading source first.

## Verify the artifact

Open the staged page in a real browser at desktop and mobile widths. Check:

- hierarchy, typography, contrast, rhythm, clipping, and empty states;
- navigation and evidence links;
- agreement between visible claims and `report.json`;
- displayed source state, generation time, artifact classification, verified
  scenarios, stale or unpinned sections, contradictions, and unknowns;
- for a pinned source, unchanged HEAD, clean source paths, and only HEAD-tracked
  repository evidence;
- for an unpinned source, an internal draft label, complete dirty path list, and
  every cited untracked or ignored evidence path;
- absence of secrets and projection-excluded material.

Repair the staged artifacts and repeat the browser check. Do not declare a
report current merely because it was regenerated.

For a source pinned at survey start, confirm HEAD is unchanged, source paths
remain clean, and every repository evidence path remains tracked. If any check
fails, discard staging and restart the survey from the new state; if the source
does not stabilize, preserve current output and return blocked. Promote only a
successfully rechecked pinned generation with an atomic directory swap.

For a source known to be unpinned at survey start, ensure `public.html` is
absent, rename staging to a unique internal draft path, and leave current
artifacts intact. If draft preservation fails, clean staging and return blocked.

Return the report paths, source identity, requested projection, verified
scenarios, material changes, contradictions, unknowns, and publication state.

Done when the HTML has been inspected on the real browser surface, every
material claim is supported or visibly qualified, and the complete generation
is either atomically promoted from a clean revision or preserved as an unpinned
internal draft without replacing current output.
