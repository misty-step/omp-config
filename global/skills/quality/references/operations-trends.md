# Operations trend governance

## Trend store

`.evidence/quality/operations/trends.ndjson` is the durable trend store.

- Append one `omp.quality.operations.trend.v2` row per run at assessment time.
  Never edit or reorder existing rows.
- Keep the file git-tracked. Its history travels with the repository and
  survives machine loss.
- Use no broker, database, or hosted service. NDJSON serves `grep`, `jq`, and
  pandas directly. Adding a broker requires measured need: a named query or
  fan-out load, with observed numbers, that a flat file cannot serve. File size
  alone below about 50 MB is not need.
- Keep rows from different repositories in separate files. Each audited
  repository owns its store. Cross-repository comparison reads multiple files
  and joins on the key contract in
  [operations-artifacts.md](operations-artifacts.md#key-contract).

## Trend report

`--trends`, and the Trend section of every shared `assessment.md`, computes four
signals per domain and overall:

| signal | definition |
|---|---|
| **Regression** | Status worsened, score dropped below the prior row or below `baseline.json`, or a stored metric crossed its `baseline.json` threshold (for example, `detection_seconds` exceeded `max_detection_seconds`) at comparable keys: same branch, with PR versus non-PR context noted. |
| **Improvement** | Status improved, score rose, or a stored metric moved back inside its threshold against the prior comparable row. |
| **Variance** | Score spread (minimum, maximum, and range) over the last 10 comparable rows. Flag a domain whose range exceeds 20 points as unstable; audit the probe before trusting the number. |
| **Missing data** | Any `missing` status, any absent expected run such as a scheduled cadence gap, and any streak of two or more consecutive `missing` rows for one domain. A streak is a `reporting` finding at `medium` severity. |

Rules:

- Compare paired rows on identical keys where possible. Never compare a PR row
  against a `master` row without naming the context difference.
- A delta across a `tool_version.skill` boundary is `not comparable`; name both
  schema versions.
- One or two history rows are a note, not a trend. Say so instead of
  extrapolating.

## Baseline and threshold governance

`baseline.json` in the operations evidence root is the only source of
thresholds. Its schema is defined in
[operations-artifacts.md](operations-artifacts.md#baselinejson--ompqualityoperationsbaselinev2).

- Append every change to the `changes` list with date, actor, field, old value,
  new value, and reason. A threshold change without a `changes` entry is
  invalid.
- Move thresholds by ratchet only, per `global/references/quality-gates.md`:
  tighten freely; loosen only with operator approval recorded in `reason`.
  Never loosen a threshold to convert a failing run into a passing one.
- A new metric starts report-only: record its score without a threshold. Add a
  threshold after three or more stable rows exist. Promote report to ratchet to
  hard requirement; never skip straight to hard on a noisy metric.
- Store `baseline_ref` as the SHA-256 of `baseline.json` at run time. This lets
  later readers distinguish a genuine regression from a moved goalpost.

## Retention

| artifact | retention |
|---|---|
| `trends.ndjson` | Forever; never pruned. |
| `baseline.json` | Forever; history in git and in `changes`. |
| `runs/<id>/run.json`, `findings.ndjson` | Forever; they are the audit trail. |
| `runs/<id>/evidence/` | Keep the last 10 runs or 90 days, whichever covers more; prune older payloads. |

Prune only `evidence/` payload directories. Before pruning, confirm that the
run's shared `assessment.md` summarizes what the payload showed. Never prune the
evidence of an `open` high-severity finding.

## Privacy

- Store no secret bytes: no credentials, tokens, cookies, or key material in
  any artifact. Scrub HAR files, console logs, and request dumps before writing
  them under `evidence/`.
- Store no end-user personal data. Replace real user identifiers in captured
  payloads with stable placeholders.
- Trend rows carry only keys, statuses, scores, and counts. They are safe to
  share across the team by construction.
- The `evidence-retention` audit runs a secret scan over
  `.evidence/quality/operations/` itself, using the `/ci` security floor, and
  fails the domain on any match.

## Failure behavior

- **Audit lane fails or a surface is unreachable:** Record the domain as
  `missing` with the exact error as `missing_reason`. Continue the run. Never
  substitute a guessed status; the verdict cap means no run passes with a
  missing domain.
- **Trend-store write fails:** The run is incomplete. Fix storage and append the
  row before claiming any result. A run that cannot be recorded cannot be
  compared, so it did not happen.
- **Remediation lane exhausts its round cap:** Keep the finding `open` and
  record the attempt in `remediation` evidence. Never mark it `remediated` on
  effort.
- **A drill damages a surface or fails to recover:** Stop all drills. Restore
  from the pre-drill checkpoint. Record a `high` `incident-preparedness` finding
  with the full timeline. Do not re-drill until that finding is remediated and
  verified.
- **Baseline file is missing or unparseable:** Run in report-only mode. Record
  all scores without threshold verdicts, record a `reporting` finding, and
  propose an initial baseline from observed values.
