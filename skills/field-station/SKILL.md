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
Record whether the worktree is clean and compute the source identity required by
the report contract, excluding generated output and staging paths.

Do not publish or widen access unless the operator explicitly requests it. A
`public` report is a separate allowlisted projection, not a redacted internal
report.

Done when the target, immutable source identity, requested projection, previous
artifacts, output paths, and publication boundary are explicit.

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

For `public`, write staged `public.html` from the publication allowlist.
Exclude internal architecture, operations, configuration, private dependencies,
unknown vulnerabilities, and evidence paths unless explicitly approved.
If an existing `public.html` is not regenerated for the current source
identity, omit it from the staged generation. Never carry a stale public
artifact into the next generation.

Done when the report is legible as a product story, useful as an engineering
map, and every trust state can be inspected without reading source first.

## Verify the artifact

Open the staged page in a real browser at desktop and mobile widths. Check:

- hierarchy, typography, contrast, rhythm, clipping, and empty states;
- navigation and evidence links;
- agreement between visible claims and `report.json`;
- displayed source identity, generation time, artifact classification, verified
  scenarios, stale sections, contradictions, and unknowns;
- unchanged source identity since the survey;
- absence of secrets and projection-excluded material.

Repair the staged artifacts and repeat the browser check. Do not declare a
report current merely because it was regenerated.

Recompute the source identity. Only when it is unchanged, promote the complete
staged directory with an atomic directory swap and remove the prior generation.
If an atomic swap is unavailable or fails, leave the current artifacts intact,
clean the staging directory, and return blocked.

Return the report paths, source identity, requested projection, verified
scenarios, material changes, contradictions, unknowns, and publication state.

Done when the HTML has been inspected on the real browser surface, every
material claim is supported or visibly qualified, and the complete generation
has been atomically promoted.
