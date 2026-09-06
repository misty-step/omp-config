# Field report contract

Field Station compiles one repository identity into:

- `.field-station/report.json`, the inspectable source model;
- `.field-station/index.html`, the internal or contributor view;
- `.field-station/public.html`, only when explicitly approved.

Generated output is not source. The skill does not change `.gitignore` or
publish artifacts without operator instruction.

## Transactional refresh

Treat current output, staging, and retained drafts as generated-only. Exclude
them from source status checks, even when Git tracks them. Build the complete
generation in a sibling directory on the same filesystem and browser-check it.

Only a clean Git source pinned to one unchanged HEAD, citing only HEAD-tracked
evidence, may replace current output. Atomically swap `report.json`,
`index.html`, and approved-or-absent `public.html`. If the source changes,
discard staging and restart.

A source known to be unpinned at survey start produces
`.field-station.draft-<timestamp>`, never replaces current output, and omits
`public.html`. On failure, preserve current output and remove staging.

## Model shape

Use this stable top-level shape. Omit optional view items, not required arrays.
Keep IDs short and stable when the represented concept remains.

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

On refresh, set `previousSourceIdentity` to the previous complete, clean
identity. Unpinned drafts never become the previous identity.

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

`observed` claims require valid `scenarioIds`. In a pinned generation,
`evidenced` claims require direct artifacts tracked by HEAD. `human` names
supplied intent; `inferred` states reasoning; `unknown` states the missing
evidence. Mark claims stale when changed evidence was not re-established and
conflicted when current sources disagree.

For Git, `complete: true` requires clean source paths at start and end, unchanged
HEAD, and tracked evidence. Record dirty and untracked evidence paths and set
`complete: false`. Every incomplete or non-Git generation is an unpinned
internal draft, omits `public.html`, and does not advance staleness baselines.

## Views

Each capability records its user, entry point, common path, outcome, and
`claimIds`. Each concept records definition, lifecycle, relationships,
invariants, owner, and `claimIds`. Each component records purpose, inputs,
outputs, dependencies, owned state, interfaces, and `claimIds`.

Flows are ordered paths across capabilities, concepts, or components. Prefer
one representative end-to-end flow over a complete call graph. Operations
record verified or repository-defined commands, configuration, deployment,
observability, recovery, and destructive operations.

Changes compare only complete, clean identities and describe meaning, not commit
lists. Scenarios record stable IDs, command or interaction, surface, expected
and actual observations, runtime identity, status, and established claims.
Contradictions cite both sides. Unknowns explain why the answer matters and the
smallest evidence that would resolve it. Observed claims and scenarios link
to each other.

Render only sections with real material:

1. Overview — product, users, value, maturity, source identity, and trust.
2. Product tour — representative user path and visible outcomes.
3. System map — components, boundaries, dependency direction, and data flow.
4. Concepts — domain nouns, relationships, lifecycles, and invariants.
5. Operations — run, configure, deploy, observe, and recover.
6. Recent movement — meaningful change since the previous observation.
7. Contradictions and unknowns — unresolved truth.
8. Trust panel — projection, classification, identity, timestamp, scenarios,
   status counts, stale claims, and evidence access.

High-level statements link to their claim and evidence. Directory or dependency
inventories appear only when they explain a boundary.

## Rendering and publication

Use one HTML file with embedded CSS, optional small inline JavaScript, and no
network requests. Include semantic landmarks, skip navigation, keyboard
controls, visible focus, sufficient contrast, fluid type, reduced-motion, and
print styles. Prefer native `<details>` for evidence drawers.

Choose a visual thesis from the product domain. Avoid generic dashboard grids,
marketing gradients, fabricated screenshots, decorative diagrams, and empty
cards. The first viewport states what the product is, who it serves, why it
matters, and how trustworthy the report is.

Public output is deny-by-default. Build it from operator-approved sections and
claim IDs, not by deleting strings from internal HTML. Never include secrets,
credentials, customer data, or private endpoint values. Exclude configuration,
internal architecture, operations, recovery, vulnerabilities, unknown security
posture, evidence paths, and private dependencies unless the exact non-secret
item is approved. If no allowlist exists, omit `public.html`. A prior public
artifact not regenerated for the current identity is omitted from staging.
