# Field report contract

Field Station compiles repository evidence into two artifacts:

- `.field-station/report.json` — the inspectable source model;
- `.field-station/index.html` — a self-contained internal or contributor view.

A public projection, when explicitly approved, is
`.field-station/public.html`. Generated artifacts may be committed or ignored;
the skill does not change `.gitignore` or publish them without operator
instruction.

## Transactional refresh

Treat the output directory as generated-only. Exclude it and every staging path
from source identity, change, freshness, and evidence calculations even when
Git tracks them. Build the complete next generation in a sibling staging
directory on the same filesystem. Browser-check the staged HTML and recheck the
source identity before changing current output.

Promote `report.json`, `index.html`, and the approved-or-absent `public.html` as
one directory generation through an atomic directory swap. If the platform
cannot swap the staged directory safely, return blocked without replacing the
current generation. On any failure, preserve current output and remove staging.


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
      "revision": "git SHA or explicit non-git identity",
      "clean": true,
      "sourceDigest": "SHA-256",
      "excludedPaths": [".field-station", ".field-station.next-*"],
      "checkedAt": "RFC 3339 timestamp"
    },
    "previousSourceIdentity": null,
    "generatedAt": "RFC 3339 timestamp",
    "requestedProjection": "internal | contributor | public"
  },
  "artifacts": {
    "report.json": {"classification": "internal", "state": "current", "sourceIdentity": "current source identity"},
    "index.html": {"classification": "internal | contributor", "state": "current", "sourceIdentity": "current source identity"},
    "public.html": {"classification": "public", "state": "current | absent", "sourceIdentity": "current source identity or null"}
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
On a refresh, replace `previousSourceIdentity: null` with an object containing
the previous `revision` and `sourceDigest`.


## Claims and evidence

Views reference central claims instead of copying factual prose.

```json
{
  "id": "claim-session-storage",
  "statement": "Sessions are stored in PostgreSQL.",
  "status": "observed | evidenced | human | inferred | unknown",
  "freshness": "current | stale | conflicted",
  "scenarioIds": ["scenario-id"],
  "evidence": [
    {
      "kind": "runtime | code | config | docs | test | git | human",
      "path": "repository/relative/path",
      "lines": "42-91",
      "revision": "source revision",
      "sourceDigest": "source content digest",
      "note": "what this evidence establishes"
    }
  ]
}
```

`observed` requires one or more valid `scenarioIds`. `evidenced` requires current
direct artifacts. `human` names the supplied source. `inferred` states the
reasoning without upgrading it to fact. `unknown` states the exact missing
evidence.

A claim is `stale` when evidence it depends on changed after the previous source
identity and it was not re-established. It is `conflicted` when current sources
disagree. Generation time alone never makes a claim current.

`revision` records repository provenance but is not the complete identity.
Compute `sourceDigest` from sorted records of relative path, normalized Git
mode/type, and content: bytes for regular files and link target for symlinks.
Include every tracked source file plus each untracked or ignored file used as
evidence.
Always exclude VCS metadata, generated output, staging paths, dependency trees,
and build caches. Record clean or dirty state separately and record every
excluded path. Generated-artifact-only commits therefore do not stale source
claims.

Recompute the digest after rendering. If it changed, do not replace the current
artifacts: restart and re-survey until the end identity matches, or return
blocked. For non-Git sources, apply the same path-and-content digest and record
the method.

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

Changes compare `previousSourceIdentity` with `sourceIdentity` and describe
meaning, not a commit list. Each item names affected views and claim IDs. When
no previous source identity exists, say this is the baseline observation.

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
