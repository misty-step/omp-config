# Operations artifacts and schemas

All operations artifacts live in the audited repository. The layout is:

```text
.evidence/quality/operations/
  baseline.json                    # governed targets; ratchet-only
  trends.ndjson                    # append-only trend store; one row per run
  runs/<run_id>/
    run.json                       # machine-readable run record
    findings.ndjson                # one finding per line
    evidence/                      # raw probe payloads; prunable per retention
```

`run_id` is `<UTC compact timestamp>-<first 12 hex of sha>`, for example
`20260730T172104Z-3a97f603c1de`.

Paths beginning `evidence/` in a run record resolve under
`.evidence/quality/operations/runs/<run_id>/`.

Keep every count, key, and verdict in one run derivable from the other
artifacts. This is the parseability and coherence falsifier for the contract.
The shared quality assessment is rendered from its machine data and cites these
artifacts; do not create a second assessment contract here.

## Key contract

Every `run.json` and every trend row carries all six keys. A run without all six
keys is not comparable and is not a run.

| key | type | rule |
|---|---|---|
| `repository` | string | `owner/repo` from the git remote, or the absolute path when no remote exists |
| `branch` | string | The audited branch name. |
| `sha` | string | Full 40-hex commit hash of the audited working copy; a dirty tree appends `-dirty`. |
| `pr` | integer or `null` | The PR under audit; `null` outside PR context, never omitted. |
| `tool_version` | object | Identical shape in `run.json` and trend rows; see below. |
| `timestamp` | string | UTC ISO-8601 with `Z`, run start time. |

`tool_version` has this shape:

```json
{
  "skill": "omp.quality.operations.run.v2",
  "auditors": { "canary": "1.4.2", "agent-browser": "0.31.1" }
}
```

`skill` identifies this schema version. `auditors` maps every external probe
tool actually used to its reported version. A tool whose version is unreadable
maps to `"unknown"`; it never disappears.

## Operational modes

`mode` is one of `full | audit-only | remediate | verify`:

- `full` is the default program mode.
- `audit-only` is the `--audit-only` invocation.
- `remediate` is the `--remediate` invocation.
- `verify` is the independent `--verify` re-audit at the repaired revision and writes its own run record.
- `--trends` recomputes reports from stored rows, audits nothing, and writes no
  run record. It has no `trends` mode value.

## `run.json` — `omp.quality.operations.run.v2`

```json
{
  "schema": "omp.quality.operations.run.v2",
  "run_id": "20260730T172104Z-3a97f603c1de",
  "repository": "misty-step/example",
  "branch": "master",
  "sha": "3a97f603c1de8a4b92f0d5e6c7b8a9d0e1f2a3b4",
  "pr": null,
  "tool_version": {
    "skill": "omp.quality.operations.run.v2",
    "auditors": { "canary": "1.4.2", "agent-browser": "0.31.1" }
  },
  "timestamp": "2026-07-30T17:21:04Z",
  "mode": "full",
  "baseline_ref": "<sha256 of baseline.json at run time>",
  "domains": {
    "reporting": { "status": "pass", "score": 92, "findings": 0, "missing_reason": null, "metrics": null, "evidence": ["evidence/reporting/"] },
    "visibility": { "status": "warn", "score": 70, "findings": 1, "missing_reason": null, "metrics": null, "evidence": ["evidence/visibility/"] },
    "observability": { "status": "fail", "score": 40, "findings": 2, "missing_reason": null, "metrics": null, "evidence": ["evidence/observability/"] },
    "incident-preparedness": { "status": "missing", "score": null, "findings": 0, "missing_reason": "staging unreachable: <error>", "metrics": null, "evidence": [] },
    "runbooks": { "status": "pass", "score": 88, "findings": 0, "missing_reason": null, "metrics": null, "evidence": ["evidence/runbooks/"] },
    "drills": { "status": "warn", "score": null, "findings": 1, "missing_reason": null, "metrics": { "detection_seconds": 214, "recovery_seconds": 655 }, "evidence": ["evidence/drills/"] },
    "evidence-retention": { "status": "pass", "score": 100, "findings": 0, "missing_reason": null, "metrics": null, "evidence": ["evidence/retention/"] }
  },
  "verdict": "fail"
}
```

Rules:

- The seven domain keys are fixed and always present.
- `status` is one of `pass | warn | fail | missing`. `missing` replaces `SKIP`
  for stored data.
- `score` is 0–100 when the domain defines a numeric score in
  `operations.md`; otherwise it is `null`. Never invent a number.
- `metrics` is an object of the named measurements the domain defines. For
  `drills`, it contains `detection_seconds` and `recovery_seconds`. It is
  `null` for domains that define no metrics. Store metrics so trend reports
  evaluate them from the store alone, without rereading evidence.
- `missing_reason` is non-null exactly when `status` is `missing`.
- `verdict` is the worst domain status. Any `missing` caps the verdict at
  `warn` or worse; a run cannot pass with unaudited domains.

## `findings.ndjson` — `omp.quality.operations.finding.v2`

Write one JSON object per line. The field reference is:

```json
{
  "schema": "omp.quality.operations.finding.v2",
  "id": "obs-001",
  "run_id": "20260730T172104Z-3a97f603c1de",
  "domain": "observability",
  "severity": "high",
  "title": "Primary service has no health probe",
  "target": "every deployed surface answers a health or readiness probe",
  "evidence": "evidence/observability/health-probe-404.txt",
  "status": "open",
  "waiver_reason": null,
  "waiver_expires": null,
  "remediation": null
}
```

The complete stream for the example run has one line per finding. Its lines
match the per-domain `findings` counts in `run.json` (visibility 1,
observability 2, drills 1):

```ndjson
{"schema":"omp.quality.operations.finding.v2","id":"vis-001","run_id":"20260730T172104Z-3a97f603c1de","domain":"visibility","severity":"medium","title":"Latest shipped change has no ledger card","target":"the last shipped change is traceable without chat context","evidence":"evidence/visibility/ledger-query.txt","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
{"schema":"omp.quality.operations.finding.v2","id":"obs-001","run_id":"20260730T172104Z-3a97f603c1de","domain":"observability","severity":"high","title":"Primary service has no health probe","target":"every deployed surface answers a health or readiness probe","evidence":"evidence/observability/health-probe-404.txt","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
{"schema":"omp.quality.operations.finding.v2","id":"obs-002","run_id":"20260730T172104Z-3a97f603c1de","domain":"observability","severity":"low","title":"Alert thresholds undocumented for worker queue","target":"each alert names the failure it catches","evidence":"evidence/observability/alert-inventory.txt","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
{"schema":"omp.quality.operations.finding.v2","id":"drl-001","run_id":"20260730T172104Z-3a97f603c1de","domain":"drills","severity":"medium","title":"Drill detection relied on manual observation","target":"detection fires from a monitoring signal","evidence":"evidence/drills/drill-timeline.md","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
```

- `severity` is one of `high | medium | low`.
- `status` is one of `open | accepted | remediated | waived`.
- `waiver_reason` and `waiver_expires` (ISO date) are non-null exactly when
  `status` is `waived`.
- When non-null, `remediation` is
  `{ "sha": "<fix commit>", "verified_by": "<independent lane>", "evidence": "<path>" }`.
  A finding is `remediated` only after independent live re-verification.

## `trends.ndjson` — `omp.quality.operations.trend.v2`

Write one flattened JSON object per run, appended once per run and never edited.
The example row has `open_high` 1 (`obs-001`) and `open_total` 4 because it
counts the `open` findings in the stream above:

```json
{
  "schema": "omp.quality.operations.trend.v2",
  "run_id": "20260730T172104Z-3a97f603c1de",
  "repository": "misty-step/example",
  "branch": "master",
  "sha": "3a97f603c1de8a4b92f0d5e6c7b8a9d0e1f2a3b4",
  "pr": null,
  "tool_version": {
    "skill": "omp.quality.operations.run.v2",
    "auditors": { "canary": "1.4.2", "agent-browser": "0.31.1" }
  },
  "timestamp": "2026-07-30T17:21:04Z",
  "mode": "full",
  "verdict": "fail",
  "open_high": 1,
  "open_total": 4,
  "domains": {
    "reporting": { "status": "pass", "score": 92, "metrics": null },
    "visibility": { "status": "warn", "score": 70, "metrics": null },
    "observability": { "status": "fail", "score": 40, "metrics": null },
    "incident-preparedness": { "status": "missing", "score": null, "metrics": null },
    "runbooks": { "status": "pass", "score": 88, "metrics": null },
    "drills": { "status": "warn", "score": null, "metrics": { "detection_seconds": 214, "recovery_seconds": 655 } },
    "evidence-retention": { "status": "pass", "score": 100, "metrics": null }
  }
}
```

Trend rows carry keys, statuses, scores, metrics, and counts only. They never
carry evidence payloads, prose, or paths. This keeps the store small, diffable,
and safe to retain forever. `tool_version` has the identical object shape as
`run.json`; it has no string projection.

## `baseline.json` — `omp.quality.operations.baseline.v2`

```json
{
  "schema": "omp.quality.operations.baseline.v2",
  "domains": {
    "observability": { "min_score": 60, "max_open_high": 0 },
    "drills": { "max_detection_seconds": 300, "max_recovery_seconds": 900 }
  },
  "changes": [
    { "date": "2026-07-30", "by": "<operator>", "field": "observability.min_score", "from": 50, "to": 60, "reason": "probe coverage complete" }
  ]
}
```

Governance rules live in [operations-trends.md](operations-trends.md#baseline-and-threshold-governance). Metric thresholds evaluate against the stored
`metrics` objects in trend rows.

## Operations assessment output

The shared assessment renderer must cite the machine artifacts and include:

1. The six run-key fields verbatim.
2. A verdict and per-domain table with status, score, metrics, finding count,
   and evidence path.
3. Every finding with severity, evidence citation, and proposed route.
4. Regression, improvement, variance, and missing-data signals against prior
   rows, or an explicit empty-history statement.
5. Every waiver with reason and expiry, and every `missing` domain with its
   reason.

The assessment must not contradict machine artifacts. Fix the machine artifact
first when the two diverge.

## Schema evolution

Bump the version suffix on any field change. Never mutate an existing-version
row in place. A trend report that spans versions groups rows by
`tool_version.skill` and names the boundary instead of silently mixing scales.
