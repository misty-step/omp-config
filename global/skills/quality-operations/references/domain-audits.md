# Domain audits

Seven fixed domains. Each section names the inventory questions, the
measurable target state, the probes that produce evidence, and the remediation
route. A target the repository cannot meet yet is still the target; record the
gap and ratchet toward it. Reuse existing surfaces by pointer — this loop owns
no gate mechanics, no monitor product, and no infrastructure authority.

## reporting

- **Inventory:** which run digests, gate reports, coverage/mutation artifacts,
  and release notes exist? Where do they land? Can a cold agent find them?
- **Target:** every repo-owned gate run emits a reviewable artifact under
  `.evidence/` (`global/references/quality-gates.md`, Report tier); the latest
  artifact is younger than the latest merge to the default branch.
- **Score:** percentage of gates that emitted a durable artifact on their last
  run.
- **Probe:** run the repo-owned gate once; confirm the artifact appears with
  the run digest. `/ci` owns gate design — a missing or weak gate becomes a
  finding routed to a `builder` lane loading `ci`, not work done here.
- **Remediate:** `builder` + `ci`.

## visibility

- **Inventory:** where does durable work state live (ledger cards, feed
  milestones, status surfaces)? Is any state chat-only?
- **Target:** the last shipped change is traceable without chat context: a
  ledger card, a feed row, or a release record names it; state queries answer
  from durable surfaces only.
- **Score:** of the last 5 shipped changes, percentage traceable end to end.
- **Probe:** pick the latest merged change; query the ledger and feed for it;
  record the query and result verbatim.
- **Remediate:** `builder` wires the missing ledger/feed step into the repo's
  documented workflow.

## observability

- **Inventory:** which surfaces are deployed? Which have health checks,
  Canary registration, error timelines, metrics, alerts?
- **Target:** every deployed surface answers a health or readiness probe; its
  error timeline is queryable; each alert names the failure it catches
  (`global/references/verification-system-first.md`, ops row).
- **Score:** percentage of deployed surfaces meeting all three.
- **Probe:** query health, incidents, checks, and recent errors through the
  Canary CLI/API per `factory-apps` (the Canary MCP stays disabled); hit each
  health endpoint live and record status codes.
- **Remediate:** `builder` adds the Canary integration path
  (`harness-engineering` preferred stack); infrastructure mutation requires
  explicit operator authorization, never a direct provider change.

## incident-preparedness

- **Inventory:** incident route, ownership, rollback path, escalation
  authority, RCA records for past incidents.
- **Target:** a cold agent given only the repository can name the owner, the
  rollback command, and the incident route for the primary surface; the last
  incident has an RCA record.
- **Score:** binary per element (owner, rollback, route, RCA) × primary
  surfaces.
- **Probe:** tabletop — dispatch a fresh `researcher` with only the repository
  and the question "how do you roll back the primary surface?"; grade its answer
  against the real path. Do not execute the rollback.
- **Remediate:** `builder` writes or repairs the incident docs. A live incident
  is never audit work: route it to a fresh `verifier` with `verify-live`
  immediately.

## runbooks

- **Inventory:** deploy, DR, migration, and onboarding runbooks in `docs/*.md`
  and repo-local skills; last-verified dates.
- **Target:** each deployed surface has an executable runbook with real
  commands; a dry run of each runbook passes on staging or a local
  environment.
- **Score:** percentage of runbooks whose dry run passed this audit.
- **Probe:** `verifier` with `verify-live` executes each runbook in dry-run or
  staging mode and records every command and its exit status.
- **Remediate:** `builder` regenerates the runbook from the real routes
  (`harness-engineering` repo-local skill generation), then a fresh `verifier`
  with `verify-live` dry run verifies it.

## drills

Detection and recovery, measured, never assumed.

- **Inventory:** last drill record, injectable reversible faults, monitoring
  hooks that should fire, pre-drill checkpoint procedure.
- **Target:** a drill record exists within the retention window;
  `detection_seconds` and `recovery_seconds` are within `baseline.json`
  thresholds.
- **Score:** none — report the two durations as metrics.
- **Probe:** inject one reversible fault into a non-production surface (stop a
  staging service, break a synthetic check), then measure time until the
  monitoring signal fires and time until recovery completes. Record both in
  the run evidence and the finding stream.
- **Safety rule:** drills run only against local, dev, or staging surfaces;
  a drill with production blast radius requires explicit operator
  authorization. Take a restorable checkpoint before injection. A drill with
  no restore path does not run.
- **Remediate:** `builder` fixes the detection or recovery gap; the fix is
  proven only by re-running the same drill.

## evidence-retention

- **Inventory:** `.evidence/` layout, this loop's own artifacts, retention
  practice, secret exposure in stored evidence.
- **Target:** the latest run directory validates against
  `run-artifact.md` schemas; retention windows from `trend-governance.md` are
  applied; a secret scan over `.evidence/quality-operations/` finds zero
  matches.
- **Score:** 100 minus deductions per schema violation, retention breach, or
  scan match.
- **Probe:** validate `run.json` and `trends.ndjson` rows with `jq` against
  the required fields; list evidence directories older than the window; run
  the secret scan and record its (redacted) output.
- **Remediate:** `builder` repairs the store: scrub, prune, or backfill
  explicit `missing` rows. Never delete trend rows to fix a violation.
