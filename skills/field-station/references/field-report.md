# Field report contract

Field Station compiles repository evidence into two artifacts:

- `.field-station/report.json` — the inspectable source model;
- `.field-station/index.html` — a self-contained internal or contributor view.

A public projection, when explicitly approved, is
`.field-station/public.html`. Generated artifacts may be committed or ignored;
the skill does not change `.gitignore` or publish them without operator
instruction.

## Transactional refresh

Treat current output, staging, and retained draft directories as generated-only.
Exclude them from source status checks even when Git tracks them. Build the
complete next generation in a sibling staging directory on the same filesystem
and browser-check the staged HTML.

Only a Git source pinned to one clean, unchanged HEAD and using only
HEAD-tracked repository evidence can replace the current generation. Promote
its `report.json`, `index.html`, and approved-or-absent `public.html` through an
atomic directory swap. If a source believed pinned changes during generation,
discard staging and restart from the new state; never retain the inconsistent
generation as current or draft.

A source known to be unpinned at survey start produces a uniquely named internal
draft directory, never replaces current output, and must omit `public.html`. On
failure, preserve current output and remove staging.


## Model shape

Use this stable top-level shape. Omit optional view items, not required arrays.
Keep IDs short and stable across refreshes when the represented concept remains
the same.

```json
{
  "schemaVersion": 1,
  "repository": {
    "name": "string",
    "root": "string",
    "sourceIdentity": {
      "revision": "Git HEAD or non-Git base identity",
      "clean": true,
      "complete": true,
      "dirtyPaths": [],
      "untrackedEvidencePaths": [],
      "excludedPaths": [".field-station", ".field-station.next-*", ".field-station.draft-*"],
      "checkedAt": "RFC 3339 timestamp"
    },
    "previousSourceIdentity": null,
    "generatedAt": "RFC 3339 timestamp",
    "requestedProjection": "internal | contributor | public"
  },
  "artifacts": {
    "report.json": {"classification": "internal", "state": "current | draft", "sourceIdentity": "source identity"},
    "index.html": {"classification": "internal | contributor", "state": "current | draft", "sourceIdentity": "source identity"},
    "public.html": {"classification": "public", "state": "current | absent", "sourceIdentity": "complete clean source identity or null"}
  },
  "summary": {
    "oneLiner": "string",
    "users": ["string"],
    "value": "string",
    "maturity": "string or unknown",
    "claimIds": ["claim-id"]
  },
  "capabilities": [],
  "concepts": [],
  "components": [],
  "flows": [],
  "operations": {},
  "changes": [],
  "claims": [],
  "scenarios": [],
  "contradictions": [],
  "unknowns": [],
  "publication": {
    "approvedSections": [],
    "approvedClaimIds": [],
    "excludedReasons": []
  }
}
```
On a refresh, replace `previousSourceIdentity: null` with the previous complete,
clean source identity. An unpinned draft never becomes the previous identity.


## Claims and evidence

Views reference central claims instead of copying factual prose.

```json
{
  "id": "claim-session-storage",
  "statement": "Sessions are stored in PostgreSQL.",
  "status": "observed | evidenced | human | inferred | unknown",
  "freshness": "current | stale | conflicted | unpinned",
  "scenarioIds": ["scenario-id"],
  "evidence": [
    {
      "kind": "runtime | code | config | docs | test | git | human",
      "path": "repository/relative/path",
      "lines": "42-91",
      "revision": "Git HEAD or non-git base identity",
      "dirty": false,
      "note": "what this evidence establishes"
    }
  ]
}
```

`observed` requires one or more valid `scenarioIds`. In a pinned generation,
`evidenced` requires direct artifacts tracked by HEAD. `human` names the supplied
source. `inferred` states the reasoning without upgrading it to fact. `unknown`
states the exact missing evidence.

A claim is `stale` when evidence it depends on changed between two complete,
clean source identities and it was not re-established. It is `conflicted` when
current sources disagree. Generation time alone never makes a claim current.

For Git, use HEAD as the complete pin only when source paths are clean at both
the start and end, HEAD is unchanged, and every repository file cited as
evidence is tracked by that HEAD. Exclude current output, staging, and retained
draft paths from cleanliness checks. When dirty, record `clean: false`,
`complete: false`, and the repository-relative dirty path list. When evidence
uses an untracked or ignored file, record its path and set `complete: false`
even if Git otherwise reports a clean worktree.

Every incomplete generation is internal, marks every claim `unpinned`, omits
`public.html`, and does not participate in later change or staleness
calculations. HEAD is provenance for an incomplete Git generation, not a
complete pin. Every non-Git source is incomplete and follows the same draft
rules. Do not synthesize a content digest in the prompt workflow.

## View records

Each capability records its user, entry point, common path, outcome, and
`claimIds`. Each concept records its definition, lifecycle or state transition,
relationships, invariants, owner component, and `claimIds`. Each component
records its purpose, inputs, outputs, dependencies, owned state, public
interfaces, and `claimIds`.

A flow is an ordered path across capabilities, concepts, or components. Prefer
one representative end-to-end flow over a complete call graph. Operations
records only verified or repository-defined prerequisites, run commands,
configuration boundaries, deployment, observability, recovery, and destructive
operations.

Changes compare only complete, clean `previousSourceIdentity` and
`sourceIdentity` values and describe meaning, not a commit list. When no
previous complete identity exists, say this is the baseline observation. A
dirty draft may describe working changes, but they remain unpinned and do not
advance the baseline.

Scenarios have stable IDs and record command or interaction, surface, expected
observation, actual observation, runtime identity, status, and established
`claimIds`. Every observed claim and scenario link to each other. Contradictions
cite both sides. Unknowns state why the answer matters and the smallest evidence
that would resolve it.

## Report sections

Render only sections with real material:

1. **Overview** — product, users, value, maturity, source identity, and trust.
2. **Product tour** — the representative user path and visible outcomes.
3. **System map** — components, boundaries, dependency direction, and data flow.
4. **Concepts** — domain nouns, relationships, lifecycles, and invariants.
5. **Operations** — run, configure, deploy, observe, recover.
6. **Recent movement** — meaningful change since the previous observation.
7. **Contradictions and unknowns** — unresolved truth, not cleanup prose.
8. **Trust panel** — projection, artifact classification, full source identity,
   timestamp, scenarios, status counts, stale claims, and evidence access.

Every high-level statement links or expands to its claim and evidence. Directory
or dependency inventories belong only where they explain a boundary.

## Rendering contract

Write one HTML file with embedded CSS, optional small inline JavaScript, and no
network requests. Use semantic landmarks, skip navigation, keyboard-operable
controls, visible focus, sufficient contrast, fluid type and spacing,
`prefers-reduced-motion`, and print styles. Evidence drawers should use native
`<details>` where possible.

Choose a visual thesis from the product domain. Avoid generic dashboard grids,
marketing gradients, fabricated screenshots, decorative architecture diagrams,
and empty cards. Inline SVG is acceptable for a real flow or boundary map. The
first viewport must answer what the product is, who it serves, why it matters,
and how trustworthy the report is.

## Publication boundary

Public output is deny-by-default. It requires operator-approved sections and
claims in `publication`. Build it from that allowlist, not by deleting strings
from the internal HTML.

Never include secrets, credentials, customer data, or private endpoint values
in any artifact; operator approval cannot override this boundary.

Also exclude configuration values, internal architecture, operations, recovery
details, vulnerabilities, contradictions, unknown security posture, evidence
paths, and private dependencies from public output unless the operator
explicitly approves the exact non-secret item. If no allowlist exists, return
the missing approval and do not create or publish `public.html`.
If a prior `public.html` exists and is not regenerated from the current source
identity and allowlist, omit it from staging. The atomic generation swap removes
it with the prior generation; never report or publish it as current.
