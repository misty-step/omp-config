---
name: pulse
description: Generate an evidence-backed HTML report of a software system's current state, production health, verification, structural direction, stability, design, and independent persona assessments.
disable-model-invocation: true
argument-hint: "[target-path] [--window=30d]"
---

# Pulse

Generate one self-contained HTML engineering-health report for the target.
Answer three questions first:

1. What needs action?
2. What changed?
3. What evidence is missing?

Then show the complete record.

```text
scope -> inventory -> probe -> verify -> compare -> map -> assess -> decide -> render -> inspect
```

## Contract

Use the selected **Indexed Domains** report structure:

```text
controlling verdict
-> report identity
-> persistent domain index
-> eight continuous domain records
-> evidence appendix
```

The eight domains are:

1. Current snapshot
2. Production health
3. Infrastructure and recovery
4. Automated verification
5. Evolution and complexity
6. Defects and stability
7. System design
8. Persona assessment

The report is a generated document. It is not a live dashboard.

### Datum contract

Every reported datum retains:

- `value`
- `unit`
- `scope`
- `window`
- `baseline`
- `delta`
- `source`
- `captured_at`
- `evidence_quality`

Use one evidence quality:

- **Observed**: A primary source supplied the value.
- **Inferred**: The report derived the value or judgment from observed inputs.
- **Unavailable**: The report attempted a valid source, but no value was available.
- **Not applicable**: The signal does not apply to this target type.

Apply these rules:

- Keep unavailable evidence visible. Never convert it to zero.
- Keep source/deployed identity separate from Previous/Current trend columns.
- Show the absolute values beside every delta.
- Use a trend only when the scope and measurement method are comparable.
- Label the first compatible snapshot `Baseline only` when no prior value exists.
- Record every exclusion beside the affected total.
- Keep severity separate from confidence and evidence quality.
- Do not average unrelated domains into one health score.

Completion criterion: every collected or missing value satisfies the datum
contract before rendering begins.

## 1. Set scope and identity

Resolve the target path and comparison window. The default window is `30d`.
Record:

- repository and branch;
- source commit revision;
- worktree state: clean or dirty, with the included changed paths;
- source content identity: a SHA-256 digest over the included path list and
  worktree bytes, with secrets excluded;
- deployed revision or content identity, when a deployed target exists;
- capture time and collision-safe UTC capture ID;
- target type, such as service, CLI, library, or static site;
- included paths and explicit exclusions;
- the most recent compatible Pulse artifact, when one exists.

Use the prior Pulse artifact as the preferred comparison baseline. Use a Git
snapshot at the start of the window only when the same metric can be reproduced
with the same scope and method.

### Baseline payload

Embed one versioned machine-readable payload in every report:

```html
<script type="application/json" id="pulse-baseline">
{
  "schema": "pulse.baseline.v1",
  "capture_id": "...",
  "target_id": "...",
  "source_identity": {"commit": "...", "dirty": true, "content_sha256": "..."},
  "scope": {"included": [], "excluded": [], "digest": "..."},
  "methods": {"snapshot.product_lines": "loc-category-v1"},
  "data": {"snapshot.product_lines": {}},
  "findings": {"torvalds.TV-001": {}}
}
</script>
```

Use stable namespaced datum keys such as `verification.changed_code_coverage`
and stable persona finding keys such as `torvalds.TV-001`. Record the unit,
scope digest, and measurement method for each datum.

Compare a prior datum only when:

- the payload schema is supported;
- `target_id` matches;
- the datum key and unit match;
- the scope digest or declared compatible scope matches;
- the measurement method is compatible.

Compare a prior finding only when the persona, rubric version, and stable finding
key match. A Git snapshot can supply reproducible source metrics only. It cannot
supply prior persona scores, runtime values, or finding history.

When no compatible value exists, report the prior value and delta as
`Baseline only` or `Unavailable`. Do not synthesize a prior value.

A clean source can use its commit as the revision identity. Identify a dirty
source with the commit, dirty paths, and content digest. `HEAD` identifies the
commit only.

Treat source-versus-deployed identity as an identity control. Do not present it
as a time-series baseline.

Completion criterion: the capture ID, commit, dirty state, content identity,
runtime identity, target type, comparison baseline, scope, and exclusions are
explicit.

## 2. Measure the current snapshot

Measure the system as it exists now.

Separate these line counts:

- product source;
- test source;
- generated source;
- vendored source;
- documentation;
- fixtures and sample data.

Also record:

- language breakdown;
- source files and directories;
- direct and transitive dependencies when the project tooling exposes them;
- executables, services, entrypoints, stores, queues, schemas, and migrations;
- public APIs and configuration knobs when they can be counted reliably.

Use existing project tools. Do not add a dependency only to collect a report
metric. Mark an unsupported metric `Unavailable`.

Treat size as inventory. Do not call growth bad or deletion good without
supporting evidence.

Completion criterion: current inventory is complete for the available project
tooling, and each total states its scope and exclusions.

## 3. Probe production health

Start with externally visible behavior. Identify the authoritative deployed
target from estate records, project configuration, or provider state.

For a service, collect the four golden signals:

- latency, including a tail percentile such as p99;
- traffic or workload volume;
- explicit, implicit, and policy-defined errors;
- saturation of the constrained resource.

Also collect:

- black-box probe results and response proof;
- availability or SLO state when defined;
- deployed revision and configuration identity;
- exceptions, crashes, panics, or recent error families;
- recent deployment events that align with a health change.

For a CLI, library, or static site, adapt the live check to the real interface.
Mark service-only signals `Not applicable`.

If exception monitoring or logs have no authoritative project identity, record
`Unavailable`. Do not report zero exceptions.

Completion criterion: every applicable user-facing surface has a current probe
or a visible evidence gap.

## 4. Inspect infrastructure and recovery

Build an observed inventory of the runtime environment:

- hosts, droplets, containers, functions, and regions;
- databases, queues, object stores, and durable volumes;
- networks, DNS, certificates, and external services;
- deployed revision per runtime unit;
- declared-versus-observed configuration drift;
- capacity and the constrained resource;
- backup age and result;
- most recent successful restore exercise.

A backup does not prove recovery. Keep restore evidence separate.

When infrastructure does not apply, state `Not applicable`. When it applies but
cannot be read, state `Unavailable`.

Completion criterion: the report shows what runs the system, where it runs, its
revision identity, its drift, and its recovery evidence.

## 5. Measure automated verification

Use the project's native test and coverage tooling. Record:

- passed, failed, skipped, quarantined, and flaky tests;
- unit, integration, system, and end-to-end suites when distinguishable;
- line, branch, and function coverage when supported;
- changed-code coverage;
- uncovered high-risk or frequently changed paths;
- coverage movement against the compatible baseline;
- test duration and instability movement;
- existing static analysis, type checking, race detection, sanitizers, and
  build status.

Coverage measures executed code. It does not prove test quality. Do not invent a
universal target. Give more attention to low coverage in critical or frequently
changed code.

Completion criterion: test results, available coverage dimensions, changed-code
coverage, instability, and unavailable verification evidence are explicit.

## 6. Measure evolution and complexity

Compare the current and baseline snapshots with the same method.

Record:

- additions, deletions, renames, and net change by code category;
- weekly or snapshot movement across the window;
- complexity median, p95, maximum, and named outliers when supported;
- oversized functions, files, packages, and interfaces;
- dependency and import cycles;
- direct and transitive dependency movement;
- fan-in, fan-out, coupling, and boundary crossings when supported;
- churn concentration and frequently changed files;
- ownership concentration;
- entrypoint, public API, and configuration growth;
- feature, fix, refactor, removal, operations, and documentation work.

Use work-ledger or pull-request labels for change classification. If only commit
text is available, label the classification `Inferred`.

Interpret each movement with evidence. Growth can represent useful capability or
structural spread. Deletion can represent simplification or lost behavior.

Completion criterion: the report shows system size and structural pressure over
time without converting one proxy into a quality claim.

## 7. Measure defects and stability

Use validated defect, incident, deployment, and test-history sources.

Record:

- bugs opened, closed, and reopened;
- net defect flow;
- defect age by severity;
- escaped production defects;
- recurring defects and repeated root causes;
- regression tests linked to resolved defects;
- production incidents;
- failed deployments, rollbacks, hotfixes, and deployment rework;
- change fail rate;
- failed-deployment recovery time;
- flaky-test movement;
- error-rate and exception-family movement.

Do not use the raw issue count as the stability conclusion. If the issue tracker
does not distinguish validated defects, state the limit.

Completion criterion: the report shows defect intake, resolution, recurrence,
escaped failures, failed changes, and recovery movement.

## 8. Map system design

Produce four source-grounded views:

1. **Context**: users, operators, external systems, and trust boundaries.
2. **Runtime**: services, executables, stores, queues, and primary data paths.
3. **Deployment**: observed infrastructure, networks, environments, and revision
   identities.
4. **Dependency**: source-derived module or package relationships.

Use one stable node identity across views. Overlay these signals when they map to
the same node:

- recent churn;
- complexity;
- coverage gaps;
- production errors;
- ownership;
- dependency cycles;
- persona findings.

Render observed nodes and links only. When only aggregate counts exist, show an
`Inferred representative` view and state that raw identities are unavailable.
Never invent a component, path, owner, or connection.

Completion criterion: all four views exist as observed diagrams, inferred
representative views, or explicit evidence gaps.

## 9. Run independent persona assessments

Build one immutable assessment assignment before dispatch. Validate that it
contains:

- target and target type;
- actual problem;
- current or proposed design;
- binding constraints and intentional non-goals;
- source commit, dirty state, source content digest, and scope digest;
- capture ID;
- exact evidence locations and unavailable evidence.

Serialize the assignment once and record its digest. Pass the same assignment
and digest to both reviewers. Dispatch two independent read-only reviews in
parallel when the task interface supports it. Do not let one review see the
other's result before both finish.

### Torvalds lens

Use a stable rubric:

- data structures and relationships;
- directness of the hot path;
- allocation and copying;
- unnecessary indirection;
- special cases;
- error invariants.

### Ousterhout lens

Use a stable rubric:

- module depth;
- interface breadth;
- information leakage;
- configuration leakage;
- errors designed out of existence;
- cognitive load imposed on callers.

Each review must return:

- a high-level verdict;
- a score from 1 to 10 using the stable rubric;
- the prior comparable score and delta;
- evidence-backed findings with current file and symbol references;
- severity and confidence;
- repeated unresolved finding identities;
- resolved finding identities with proof;
- ordered actions.

Scores show movement. Findings carry the conclusion. Do not add decorative
quotes.

Completion criterion: both independent reviews provide complete rubrics,
comparable scores, cited findings, finding history, and actions.

## 10. Derive the verdict and actions

### Required evidence matrix

Set required evidence before deriving any state. `Inferred` evidence does not
satisfy a required observed signal.

| Domain | Service | CLI or local tool | Library | Static site |
| --- | --- | --- | --- | --- |
| Current snapshot | source identity, content digest, scope | source identity, content digest, scope | source identity, content digest, scope | source identity, content digest, scope |
| Production health | black-box probe, deployed identity, applicable golden signals, exception source | real command or install probe, installed identity, error output source | Not applicable unless an operated runtime exists | deployed URL, content identity, external probe |
| Infrastructure and recovery | runtime inventory, drift, durable-state backup and restore evidence | installed projection identity and source-recovery evidence | Not applicable unless distributed as an operated artifact | host/provider identity, deployment identity, rollback or restore evidence |
| Automated verification | native test result and available coverage dimensions | native test result and available coverage dimensions | native test result and available coverage dimensions | build/link check and applicable functional test |
| Evolution and complexity | current scoped inventory; compatible prior data may be `Baseline only` | same | same | same |
| Defects and stability | validated defect source, incident source, deployment history | validated defect or release-regression source | validated defect or release-regression source | validated defect and deployment-error source |
| System design | applicable context, runtime, deployment, and dependency views | context, command/runtime, installation, and dependency views | context, package/runtime, distribution, and dependency views | context, runtime or Not applicable, deployment, and dependency views |
| Persona assessment | validated immutable assignment and both completed reviews | same | same | same |

Apply `Not applicable` only when the target boundary makes the signal
irrelevant and the report states the reason. Apply `Unavailable required
evidence` when a required signal lacks observed evidence.

Derive each domain state from its supported evidence:

```text
Failing > Unavailable required evidence > Regressing > Healthy > Baseline only
```

The worst supported state controls the report verdict. Do not average states.

Lead with:

- the controlling state and evidence;
- current production truth;
- source-versus-deployed revision state;
- three to five ordered actions;
- the domains affected by each action.

Phrase actions as direct tasks. Name the evidence that will prove completion.

Completion criterion: every verdict statement links to observed or clearly
labeled inferred evidence, and every action names a proof condition.

## 11. Render the Indexed Domains report

Create a collision-safe capture ID before rendering:

```text
<UTC timestamp to seconds>-<128-bit random run ID>
```

Write `artifacts/pulse-<capture-id>.html`, unless the target defines another
report directory. Write to a temporary file in that directory, then rename it
atomically to the unique destination. Never use a check-then-write reservation.
If the destination still exists, generate a new run ID.

Render one standalone HTML file. Inline CSS, JavaScript, and SVG. Load no runtime
asset from the network.

### Structure

Render in this order:

1. controlling verdict and ordered actions;
2. capture ID and time, source commit, dirty state, source content digest,
   deployed identity, window, and scope;
3. persistent domain index;
4. eight continuous domain records;
5. evidence appendix.

The persistent index:

- stays beside the report on desktop;
- becomes a compact sticky index on narrow screens;
- supports pointer activation, `Enter`, and visible focus;
- moves the selected domain into the visible viewport;
- marks the activated item immediately;
- updates the active item and narrow-screen selector as the reader scrolls;
- selects the evidence appendix at the maximum scroll position;
- never hides the other domain records.

Each metric table uses these columns:

```text
Signal | Previous | Current | Delta | Reading | Evidence
```

On narrow screens, convert each row to a labeled record. Keep each cell label
and its complete value in one vertical block. Do not alternate text fragments
between label and value columns. Do not create page-level horizontal overflow.

### Component system

Use the selected restrained component contract:

- shadcn-neutral color tokens and open-code component markup;
- system sans for headings and body;
- monospace only for values, revisions, and identifiers;
- standard Button, Card, Badge, Alert, Table, Separator, Progress, Tabs, and
  Collapsible forms;
- Base UI interaction semantics for tabs, disclosures, focus, and roving
  keyboard selection;
- inline Lucide SVG icons for semantic actions and states;
- one blue interaction accent;
- red, amber, green, and violet only for evidence state;
- 10 px radius, 1 px borders, and no decorative motion.

When the target already provides React, Base UI, Lucide, and a bundler, use the
installed packages and bundle the report to one HTML file. Otherwise, copy only
the required shadcn markup, Base UI behavior, and Lucide SVGs into the report.
Do not add a runtime dependency to the target.

### Language

Use ASD-STE100-style controlled English:

- use short sentences;
- use one term for one concept;
- use active voice;
- name the actor and action;
- remove idioms and ornamental language;
- preserve exact technical names and evidence labels.

Completion criterion: the file contains the selected structure, complete domain
records, evidence semantics, responsive behavior, and no external runtime
assets.

## 12. Verify and deliver

Open the generated file in a real browser.

At desktop and 390 px widths:

- inspect the first fold;
- activate index links by pointer and `Enter`;
- activate tabs and disclosures;
- confirm visible focus;
- confirm the selected domain enters the visible viewport;
- confirm `scrollWidth` does not exceed the viewport width;
- inspect all four system views;
- inspect both persona assessments;
- inspect Previous/Current labels and source/deployed identity;
- inspect every unavailable and not-applicable state;
- confirm all values and provenance remain readable.

Capture and inspect screenshots. Do not place evidence media in the repository.

Return:

- the absolute report path;
- the `file://` URL;
- the collision-safe capture ID;
- the controlling verdict;
- the ordered action list;
- each evidence gap;
- the source commit, dirty state, source content digest, runtime identity, and
  identity confidence.

Completion criterion: the final report opens offline, every domain is complete,
all interactions work, desktop and mobile layouts pass, and every claim has
reviewable evidence or a visible evidence gap.
