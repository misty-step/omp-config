# Operations quality

Use this branch for seven fixed operational subdomains: `reporting`, `visibility`,
`observability`, `incident-preparedness`, `runbooks`, `drills`, and
`evidence-retention`.

Load [operations-artifacts.md](operations-artifacts.md) when writing or validating
run records, findings, trend rows, or baselines. Load
[operations-trends.md](operations-trends.md) when storing, reporting, ratcheting,
retaining, or recovering operations evidence. These files are the sole source for
those contracts.

## Modes and boundaries

Use the shared `/quality` modes for audit, remediation, and verification. The
operations-only `--trends` mode recomputes the trend report from stored rows,
audits nothing, and writes no run record. Run-record mode values and key rules
live in [operations-artifacts.md](operations-artifacts.md#operational-modes).

Do not use this branch for one live production failure. Route that work to a
fresh `verifier` with `verify-live` and this operations branch. Do not design
gate mechanics here. `/ci` owns gates; this branch consumes their reports as
evidence.

## Domain targets and probes

### reporting

- **Target:** Every repo-owned gate run emits a reviewable artifact under
  `.evidence/` ([Report tier](../../../references/quality-gates.md)), and the
  latest artifact is newer than the latest merge to the default branch.
- **Score:** Percentage of gates that emitted a durable artifact on their last
  run.
- **Probe:** Run the repo-owned gate once. Confirm that the artifact appears
  with its run digest.
- **Evidence:** Record the artifact path, digest, command, and output. Route a
  missing or weak gate to a `builder` loading `ci`.

### visibility

- **Target:** A ledger card, feed row, or release record traces the last shipped
  change without chat context. State queries answer from durable surfaces only.
- **Score:** Percentage of the last five shipped changes traceable end to end.
- **Probe:** Select the latest merged change. Query the ledger and feed. Record
  each query and result verbatim.
- **Evidence:** Preserve the query output and route a missing ledger or feed
  step to a `builder` for the documented workflow.

### observability

- **Target:** Every deployed surface answers a health or readiness probe, has a
  queryable error timeline, and has alerts that name the failure they catch.
- **Score:** Percentage of deployed surfaces meeting all three conditions.
- **Probe:** Query health, incidents, checks, and recent errors through the
  Canary CLI/API. Keep the Canary MCP disabled. Hit every health endpoint live
  and record status codes.
- **Evidence:** Store query results, endpoint status codes, and alert mappings.
  Route missing integration to a `builder` using the preferred
  `harness-engineering` stack. Infrastructure mutation requires explicit
  operator authorization.

### incident-preparedness

- **Target:** A cold agent with only the repository can name the owner, rollback
  command, and incident route for the primary surface. The last incident has
  an RCA record.
- **Score:** Binary owner, rollback, route, and RCA results for each primary
  surface.
- **Probe:** Dispatch a fresh `researcher` with only the repository and ask,
  “How do you roll back the primary surface?” Grade the answer against the
  real path. Do not execute the rollback.
- **Evidence:** Keep the graded answer and path citations. Route documentation
  gaps to a `builder`. Route a live incident immediately to a fresh
  `verifier` with `verify-live`.

### runbooks

- **Target:** Each deployed surface has an executable runbook with real
  commands. A dry run of each runbook passes on staging or locally.
- **Score:** Percentage of runbooks whose dry run passed in this audit.
- **Probe:** Use a `verifier` with `verify-live` to execute each runbook in
  dry-run or staging mode. Record every command and exit status.
- **Evidence:** Store the command transcript and environment. Route repairs to
  a `builder` that regenerates the runbook from real routes, then use a fresh
  `verifier` with `verify-live` for the dry run.

### drills

Detection and recovery are measured, never assumed.

- **Target:** A drill record exists within the retention window. Its
  `detection_seconds` and `recovery_seconds` meet `baseline.json` thresholds.
- **Score:** None. Report `detection_seconds` and `recovery_seconds` as metrics.
- **Probe:** Inject one reversible fault into a non-production surface, then
  measure time until the monitoring signal fires and time until recovery
  completes. Record both measurements in run evidence and the finding stream.
- **Safety:** Run drills only against local, development, or staging surfaces.
  Explicit operator authorization is required for production blast radius.
  Take a restorable checkpoint before injection. Do not run without a restore
  path. If a drill damages a surface or fails recovery, stop all drills and
  restore the checkpoint before recording the incident.
- **Evidence:** Store the checkpoint, fault, signal timeline, recovery timeline,
  and both durations. Route detection or recovery gaps to a `builder`; prove a
  fix only by rerunning the same drill.

### evidence-retention

- **Target:** The latest run validates against the artifact schemas, retention
  windows are applied, and a secret scan over `.evidence/quality/operations/`
  finds zero matches.
- **Score:** 100 minus deductions for each schema violation, retention breach,
  or scan match.
- **Probe:** Validate `run.json` and trend rows with `jq` against required
  fields. List evidence directories older than the retention window. Run the
  secret scan and record redacted output.
- **Evidence:** Store validation output, age listing, and redacted scan output.
  Route repairs to a `builder` for scrubbing, pruning, or explicit `missing`
  backfill. Never delete trend rows to fix a violation.

Each selected target needs `pass`, `gap`, or `missing` evidence in the shared
assessment. A missing probe records its exact reason; it never guesses a status.

## Leaf routes

Load the narrow method instead of reproducing it:

| Need | Pointer |
|---|---|
| Gate design or gate evidence | [`skill://ci`](../../ci/SKILL.md) |
| Canary CLI/API and deployed-surface probes | [`skill://factory-apps`](../../factory-apps/SKILL.md) |
| Live runbook, incident, or drill verification | [`skill://verify-live`](../../verify-live/SKILL.md) |
| Harness-owned integration paths | [`skill://harness-engineering`](../../harness-engineering/SKILL.md) |

Keep focused methods, including `review-tests`, `qa-users`, and design leaves,
outside this operations branch.
