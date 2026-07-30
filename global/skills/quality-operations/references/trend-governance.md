# Trend storage, reports, and governance

## Trend store

`.evidence/quality-operations/trends.ndjson` is the durable trend store.

- Append-only: one `quality-operations.trend.v1` row per run, written at
  assess time. Never edit or reorder existing rows.
- Git-tracked: history travels with the repository and survives machine loss.
- Flat file, no broker: NDJSON serves grep, jq, and pandas directly. Adding a
  broker, database, or hosted service requires measured need — a named query
  or fan-out load, with observed numbers, that a flat file demonstrably cannot
  serve. File size alone below ~50 MB is not need.
- Rows from different repositories never share one file; each audited
  repository owns its store. Cross-repository comparison reads multiple files
  and joins on the key contract.

## Trend report

`--trends` (and section 4 of every `assessment.md`) computes four signals from
the store, per domain and overall:

| signal | definition |
|---|---|
| **Regression** | status worsened, score dropped below the prior row or below `baseline.json`, or a stored metric crossed its `baseline.json` threshold (for example `detection_seconds` above `max_detection_seconds`), at comparable keys (same branch; note PR vs non-PR context) |
| **Improvement** | status improved, score rose, or a stored metric moved back inside its threshold, against the prior comparable row |
| **Variance** | score spread (min, max, and range) over the last 10 comparable rows; flag a domain whose range exceeds 20 points as unstable — audit the probe before trusting the number |
| **Missing data** | any `missing` status, any absent expected run (for example a scheduled cadence gap), and any streak of 2+ consecutive `missing` rows for one domain — a streak is itself a `reporting` finding at `medium` severity |

Rules:

- Compare paired rows on identical keys where possible; never compare a `pr`
  row against a `master` row without naming the context difference.
- A delta computed across a `tool_version.skill` boundary is reported as
  "not comparable" with both schema versions named.
- One or two rows of history is a note, not a trend. Say so instead of
  extrapolating.

## Baseline and threshold governance

`baseline.json` is the only source of thresholds. Governance:

- Every change appends to the `changes` list: date, actor, field, old value,
  new value, reason. A threshold change without a `changes` entry is invalid.
- Thresholds move by ratchet only, per `global/references/quality-gates.md`:
  tighten freely; loosen only with operator approval recorded in the `reason`.
  Never loosen a threshold to convert a failing run into a passing one.
- A new metric starts report-only (`score` recorded, no threshold). Add its
  threshold to `baseline.json` after 3+ stable rows exist. Promote report →
  ratchet → hard requirement; never skip straight to hard on a noisy metric.
- The run records `baseline_ref` (sha256 of `baseline.json` at run time), so a
  later reader can tell a genuine regression from a moved goalpost.

## Retention

| artifact | retention |
|---|---|
| `trends.ndjson` | forever; never pruned |
| `baseline.json` | forever; history in git and in `changes` |
| `runs/<id>/run.json`, `findings.ndjson`, `assessment.md` | forever; they are small and are the audit trail |
| `runs/<id>/evidence/` | keep the last 10 runs or 90 days, whichever covers more; prune older payloads |

Pruning deletes only `evidence/` payload directories. Before pruning, confirm
the run's `assessment.md` summarizes what the payload showed. Never prune the
evidence of an `open` high-severity finding.

## Privacy

- Store no secret bytes: no credentials, tokens, cookies, or key material in
  any artifact. Scrub HAR files, console logs, and request dumps before
  writing them under `evidence/`.
- Store no end-user personal data. Replace real user identifiers in captured
  payloads with stable placeholders.
- Trend rows carry only keys, statuses, scores, and counts — safe to share
  across the team by construction.
- The `evidence-retention` domain audit runs a secret scan over
  `.evidence/quality-operations/` itself (same floor as the `/ci` security
  stance) and fails the domain on any match.

## Failure behavior

- **Audit lane fails or a surface is unreachable:** record the domain as
  `missing` with the exact error as `missing_reason`. Continue the run. Never
  substitute a guessed status; the verdict cap (no `pass` with `missing`)
  keeps the gap visible.
- **Trend-store write fails:** the run is incomplete. Fix storage and append
  the row before claiming any result. A run that cannot be recorded cannot be
  compared, so it did not happen.
- **Remediation lane exhausts its round cap:** the finding stays `open` with
  the attempt recorded in `remediation` evidence. Report it; never mark it
  `remediated` on effort.
- **A drill damages a surface or fails to recover:** stop all drills, restore
  from the pre-drill checkpoint, and record a `high` `incident-preparedness`
  finding with the full timeline. Do not re-drill until that finding is
  remediated and verified.
- **Baseline file is missing or unparseable:** run in report-only mode (all
  scores recorded, no threshold verdicts), record a `reporting` finding, and
  propose an initial baseline from the observed values.
