# Run artifacts and schemas

All artifacts live in the audited repository. Layout:

```text
.evidence/quality-operations/
  baseline.json                    # governed targets; ratchet-only
  trends.ndjson                    # append-only trend store; one row per run
  runs/<run_id>/
    run.json                       # machine-readable run record
    findings.ndjson                # one finding per line
    assessment.md                  # human-readable report; cites the two above
    evidence/                      # raw probe payloads; prunable per retention
```

`run_id` = `<UTC compact timestamp>-<first 12 hex of sha>`, for example
`20260730T172104Z-3a97f603c1de`.

The examples below compose one coherent run: every count, key, and verdict in
one artifact is derivable from the others. Keep them consistent — they are the
parseability and coherence falsifier named in `evals/WAIVER.md`.

## Key contract

Every `run.json` and every trend row carries all six keys. A run without all
six keys is not comparable and is not a run.

| key | type | rule |
|---|---|---|
| `repository` | string | `owner/repo` from the git remote, or the absolute path when no remote exists |
| `branch` | string | the audited branch name |
| `sha` | string | full 40-hex commit hash of the audited working copy; a dirty tree appends `-dirty` |
| `pr` | integer or `null` | the PR under audit; `null` outside PR context, never omitted |
| `tool_version` | object | identical shape in `run.json` and trend rows; see below |
| `timestamp` | string | UTC ISO-8601 with `Z`, run start time |

`tool_version`:

```json
{
  "skill": "quality-operations.run.v1",
  "auditors": { "canary": "1.4.2", "agent-browser": "0.31.1" }
}
```

`skill` is the schema version of this contract. `auditors` maps each external
probe tool actually used to its reported version. A tool whose version is
unreadable maps to `"unknown"`, never disappears.

## Modes

`mode` ∈ `full | audit-only | remediate | delta`:

- `full` — the default loop, recorded when steps 1–6 run.
- `audit-only` — the `--audit-only` invocation.
- `remediate` — the `--remediate` invocation.
- `delta` — the step-7 re-audit of remediated domains at the new SHA; it is a
  loop step, never a CLI flag, and writes its own run record.
- `--trends` recomputes reports from stored rows, audits nothing, and writes
  no run record, so no `trends` mode exists.

## `run.json` — `quality-operations.run.v1`

```json
{
  "schema": "quality-operations.run.v1",
  "run_id": "20260730T172104Z-3a97f603c1de",
  "repository": "misty-step/example",
  "branch": "master",
  "sha": "3a97f603c1de8a4b92f0d5e6c7b8a9d0e1f2a3b4",
  "pr": null,
  "tool_version": {
    "skill": "quality-operations.run.v1",
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
- `status` ∈ `pass | warn | fail | missing` — the same vocabulary as
  `verify-live` verdicts; `missing` replaces `SKIP` for stored data.
- `score` is 0–100 when the domain defines a numeric score in
  `domain-audits.md`; otherwise `null`. Never invent a number.
- `metrics` is an object of the named measurements the domain defines
  (`drills`: `detection_seconds`, `recovery_seconds`); `null` for domains
  that define none. Metrics are stored so trend reports evaluate them from
  the store alone, without re-reading evidence.
- `missing_reason` is non-null exactly when `status` is `missing`.
- `verdict` is the worst domain status, where any `missing` caps the verdict
  at `warn` or worse: a run cannot `pass` with unaudited domains.

## `findings.ndjson` — `quality-operations.finding.v1`

One JSON object per line. Field reference, pretty-printed:

```json
{
  "schema": "quality-operations.finding.v1",
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

The complete stream for the example run — one line per finding, matching the
per-domain `findings` counts in `run.json` (visibility 1, observability 2,
drills 1):

```ndjson
{"schema":"quality-operations.finding.v1","id":"vis-001","run_id":"20260730T172104Z-3a97f603c1de","domain":"visibility","severity":"medium","title":"Latest shipped change has no ledger card","target":"the last shipped change is traceable without chat context","evidence":"evidence/visibility/ledger-query.txt","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
{"schema":"quality-operations.finding.v1","id":"obs-001","run_id":"20260730T172104Z-3a97f603c1de","domain":"observability","severity":"high","title":"Primary service has no health probe","target":"every deployed surface answers a health or readiness probe","evidence":"evidence/observability/health-probe-404.txt","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
{"schema":"quality-operations.finding.v1","id":"obs-002","run_id":"20260730T172104Z-3a97f603c1de","domain":"observability","severity":"low","title":"Alert thresholds undocumented for worker queue","target":"each alert names the failure it catches","evidence":"evidence/observability/alert-inventory.txt","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
{"schema":"quality-operations.finding.v1","id":"drl-001","run_id":"20260730T172104Z-3a97f603c1de","domain":"drills","severity":"medium","title":"Drill detection relied on manual observation","target":"detection fires from a monitoring signal","evidence":"evidence/drills/drill-timeline.md","status":"open","waiver_reason":null,"waiver_expires":null,"remediation":null}
```

- `severity` ∈ `high | medium | low`.
- `status` ∈ `open | accepted | remediated | waived`.
- `waiver_reason` and `waiver_expires` (ISO date) are non-null exactly when
  `status` is `waived`.
- `remediation`, when non-null:
  `{ "sha": "<fix commit>", "verified_by": "<independent lane>", "evidence": "<path>" }`.
  A finding is `remediated` only after independent live re-verification.

## `trends.ndjson` — `quality-operations.trend.v1`

One flattened JSON object per line, appended once per run, never edited. The
row for the example run — `open_high` 1 (obs-001) and `open_total` 4 count the
`open` findings in the stream above:

```json
{
  "schema": "quality-operations.trend.v1",
  "run_id": "20260730T172104Z-3a97f603c1de",
  "repository": "misty-step/example",
  "branch": "master",
  "sha": "3a97f603c1de8a4b92f0d5e6c7b8a9d0e1f2a3b4",
  "pr": null,
  "tool_version": {
    "skill": "quality-operations.run.v1",
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

Trend rows carry keys, statuses, scores, metrics, and counts only — never
evidence payloads, prose, or paths. This keeps the store small, diffable, and
safe to retain forever. `tool_version` has the identical object shape as
`run.json`; there is no string projection.

## `baseline.json` — `quality-operations.baseline.v1`

```json
{
  "schema": "quality-operations.baseline.v1",
  "domains": {
    "observability": { "min_score": 60, "max_open_high": 0 },
    "drills": { "max_detection_seconds": 300, "max_recovery_seconds": 900 }
  },
  "changes": [
    { "date": "2026-07-30", "by": "<operator>", "field": "observability.min_score", "from": 50, "to": 60, "reason": "probe coverage complete" }
  ]
}
```

Governance rules live in `trend-governance.md`. Metric thresholds
(`max_detection_seconds`, `max_recovery_seconds`) evaluate against the stored
`metrics` objects in trend rows.

## `assessment.md` required sections

1. **Run key** — the six key fields, verbatim.
2. **Verdict and per-domain table** — status, score, metrics, finding count,
   evidence path per domain.
3. **Findings** — each with severity, evidence citation, and proposed route.
4. **Trend** — regression, improvement, variance, and missing data against
   prior rows (see `trend-governance.md`), or the statement that history is
   empty.
5. **Waivers and misses** — every waiver with reason and expiry; every
   `missing` domain with its reason.

The assessment cites machine artifacts; it never contradicts them. On any
divergence, fix the machine artifact first.

## Schema evolution

Bump the version suffix (`.v2`) on any field change; never mutate `.v1` rows in
place. A trend report that spans versions groups rows by `tool_version.skill`
and names the boundary instead of silently mixing scales.
