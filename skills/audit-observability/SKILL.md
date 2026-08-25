---
name: audit-observability
description: Audit observability coverage and produce an evidence-backed, build-ready remediation plan.
disable-model-invocation: true
argument-hint: "[repo-or-system]"
---

# Audit Observability

Read-only whole-system observability audit and remediation design. Inspect,
probe safely, assess, and plan. Do not install SDKs, create monitors or alerts,
change dashboards or routing, send test notifications, modify production data,
implement remediation, commit, or push.

Use for observability audits, monitoring assessments, production-readiness
signal reviews, alerting design, and remediation planning.

Not `foundation`: that program installs an engineering baseline. Not `pulse`:
that program renders broad current engineering health. Not `watch-deploy`: that
program owns a post-deployment soak. This program maps every material failure
path to evidence, detection, diagnosis, ownership, and a build-ready plan.

Default to the current repository and its operated system unless the invocation
names another target. Keep one explicit system boundary. Write the canonical
packet outside the target repository, such as
`local://audit-observability.md`.

```text
orient -> map boundary -> classify semantics -> prove coverage -> assess -> design -> plan -> deliver
```

## 1. Orient and set authority

Read repository policy, architecture, run instructions, deployment records, and
operator-owned infrastructure records before inferring a topology. Read
`skill://research`. Search fleet memory with `exocortex`, then read the primary
record behind every relevant hit. Memory and old reports are leads, not proof of
current coverage.

Record:

- target repository, branch, source revision, dirty-state note, and capture time;
- deployed services and revision identities, when a runtime exists;
- included environments, regions, tenants, data stores, dependencies, and
  notification destinations;
- explicit exclusions and the authority for each exclusion;
- operator and service owners, SLOs, runbooks, incident paths, retention and
  spend limits already in force;
- access gaps that prevent read-only inspection.

A repository proves declared configuration. A provider API, CLI, dashboard, or
runtime probe proves provider or runtime state. Official vendor documentation
proves capability only. It never proves that the target enabled, routed, or
retained that capability.

Use primary records read now. Cite repository records as `path:line`, runtime or
provider observations as the exact read-only command/API/dashboard plus capture
time, and external capabilities as an official URL plus access date. Titles,
recollection, screenshots without identity, and secondary summaries are leads.
Keep unavailable facts `Unknown`; never turn missing access into `Absent` or
zero.

Completion criterion: the boundary, identities, authorities, exclusions, and
access gaps are explicit; every consequential current-state claim names a
primary record read during this run.

## 2. Map the system and its failures

Inventory every applicable surface and the data path between them:

1. browser or native UI;
2. server processes and runtime frameworks;
3. public and internal APIs, gateways, webhooks, and streaming connections;
4. workers, queues, schedulers, cron jobs, retries, dead letters, and durable
   execution;
5. databases, caches, object stores, migrations, replication, backups, and
   restore paths;
6. DNS, TLS, CDN, load balancers, networks, hosts, containers, functions,
   regions, and capacity limits;
7. builds, releases, artifacts, source maps or debug files, deploys, rollback,
   and runtime revision reporting;
8. external APIs, identity providers, payment or messaging providers, and their
   rate, quota, and status boundaries;
9. ownership, triage, escalation, on-call or business-hours response, runbooks,
   and Microsoft Teams or other notification routing.

For each component, follow user-visible and operator-visible outcomes through
inputs, work, durable state, output, acknowledgment, failure, retry, recovery,
and rollback. Include silent failures: stale data, skipped jobs, partial writes,
poison messages, exhausted retries, stuck progress, successful HTTP responses
with wrong content, expired certificates, full disks, pool exhaustion, provider
rate limits, notification failure, and telemetry pipeline failure.

Give each datum one producer, one semantic owner, and one explicit path to its
backend and consumer. Record duplicate emission and conflicting ownership as
findings.

Completion criterion: every applicable surface has an exact boundary, owner,
data path, material failure paths, recovery path, and current evidence source or
an explicit unknown.

## 3. Separate detection layers and signal semantics

Never let one green check stand in for another layer:

| Layer | It proves | It does not prove |
| --- | --- | --- |
| External reachability | An off-system client can resolve, connect, negotiate TLS, and receive the expected bounded response | The process can make progress, dependencies are usable, or the product result is correct |
| Runtime liveness | The intended process and event loop can make progress through a non-cached, process-generated check | The instance should receive traffic or dependencies are correct |
| Dependency readiness | The instance can accept traffic using only bounded dependencies required for that traffic | Deep business correctness, data freshness, or every optional dependency |
| Product/dependency correctness | A real receipt, freshness invariant, read-only functional check, or deep synthetic satisfies a named user outcome | General availability outside the exercised path |

Keep liveness cheap and independent of remote dependencies; a dependency outage
must not create restart cascades. Keep readiness bounded by timeout and by the
minimum dependencies necessary to serve. Use a process-generated nonce,
monotonic heartbeat, or equivalent dynamic value to defeat cached static
success without exposing diagnostics. Test deep correctness separately.
Return the dynamic value only to the probe consumer; do not index it, attach it
to metrics, or emit it as a log, span, or error attribute.

Inventory these signal classes independently:

- **Errors and issues:** handled and unhandled failures, grouping semantics,
  fatality, stack context, ownership, regression state, and direct issue link.
- **Traces:** entry spans, service boundaries, propagation, async continuation,
  error status, latency, sampling, and direct trace link.
- **Structured logs:** stable event name, severity, allowlisted attributes,
  trace correlation, queryability, and retention. Logs are telemetry, not
  alerts.
- **Metrics:** traffic, errors, latency distributions, saturation, queue age or
  depth, pool use, resource capacity, business freshness, units, aggregation,
  and bounded dimensions.
- **Uptime:** off-system DNS/TLS/connectivity/status checks, locations,
  interval, timeout, failure tolerance, recovery tolerance, and probe identity.
- **Liveness and readiness:** distinct runtime semantics, orchestrator action,
  cache behavior, dependency bounds, and cascade risk.
- **Deep functional or synthetic checks:** exact outcome, read/write behavior,
  fixture, cleanup, false-positive controls, and product boundary.
- **Cron and check-ins:** expected schedule, in-progress/success/failure/missed
  semantics, timeout, environment, execution identity, owner, and stale monitor
  behavior.
- **Releases:** source revision, artifact, release, deployment, environment,
  rollback identity, and event association.
- **Source maps or debug artifacts:** generated from the deployed artifact,
  uploaded with explicit project identity, retained as required, and verified
  against a controlled staging error.
- **Profiling and replay:** enable only for a named diagnostic question with an
  explicit privacy, overhead, sampling, retention, and access decision.
- **Alerts and escalation:** evaluated condition, window, threshold, severity,
  failure and recovery tolerance, owner, runbook, destination, acknowledgment,
  escalation, and direct diagnostic links.

Completion criterion: each applicable signal class has one defined semantic
job; reachability, liveness, readiness, and correctness remain separate.

## 4. Prove the coverage matrix

Build one row per `component × material failure path × signal`. Broad component
rows and a list of installed tools do not prove coverage.

```markdown
| ID | Surface/component | Outcome and failure path | Detection layer | Signal and semantic owner | Producer -> transport -> backend | Context/correlation | Sampling, freshness, retention | Query and direct links | Alert, tolerances, route | Owner and runbook | Primary evidence | Status | Maturity | Gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Use only these coverage statuses:

- `Observed`: current production or declared-target evidence proves the full row.
- `Partial`: evidence proves named parts and the row states the missing parts.
- `Absent`: a current authoritative record proves there is no applicable signal.
- `Unknown`: a valid source was unavailable or inconclusive.
- `Not applicable`: the boundary or invariant makes the signal irrelevant, with
  the reason cited.

Assign maturity per failure path, never by averaging unrelated rows:

- `M0 Blind`: authoritative evidence proves the failure has no detection.
- `M1 Collected`: the signal arrives and a fresh query can retrieve it.
- `M2 Correlated`: service, environment, release or deployment, and request or
  execution identity connect the necessary signals.
- `M3 Operational`: an owned, noise-bounded alert and runbook drive a response.
- `M4 Proven`: a safe failure-and-recovery scenario demonstrated detection,
  diagnosis, routing, and recovery on the intended surface.
- `Unknown`: evidence cannot support a maturity level.

Record both status and maturity. An SDK in a manifest is not `M1`; prove a fresh
sanitized event. An alert definition is not `M3`; prove ownership, routing,
query links, and applicable recent execution or an approved safe test. Do not
send alerts or inject failures during this audit.

Completion criterion: every material failure path has a row, exact evidence,
status, maturity, and a gap or explicit reason no gap exists.

## 5. Assess findings and operating quality

Write one finding per material coverage, semantic, privacy, cost, or ownership
problem. Each finding includes:

- stable ID, severity, confidence, affected outcomes and boundary;
- current behavior and concrete failure that remains invisible or unactionable;
- primary records read now, with no uncited current-state claim;
- current status and maturity;
- impact, detection delay, recovery consequence, and false-positive risk;
- one owning subsystem and accountable human or `Unknown`;
- smallest credible remediation outcome, dependencies, and acceptance scenario;
- privacy, performance, quota, retention, and migration constraints;
- priority and the evidence that makes it urgent.

Optimize for maximum useful coverage, not maximum event volume. Assess:

- SLI/SLO or explicit absence, failure and recovery tolerance, precision,
  recall, detection time, and reset time;
- signal freshness, sampling bias, tail visibility, retention, quota, spend,
  burst behavior, and telemetry loss;
- alert volume, duplicates, flap behavior, maintenance windows, ownership,
  acknowledgment, escalation, and runbook quality;
- instrumentation CPU, memory, latency, network, storage, and vendor-failure
  overhead;
- queries and direct links an agent can use without dashboard archaeology.

Delete or consolidate unsupported, duplicate, stale, unactionable, or noisy
signals before adding volume. An alert that caught a real defect gets tuned and
kept. An alert that repeatedly cannot drive action gets repaired or deleted.
Do not invent a universal SLO, retention period, sampling rate, threshold, or
soak duration.

Completion criterion: every finding is source-cited, owned, impact-ranked,
noise- and cost-aware, and tied to one observable remediation outcome.

## 6. Define the context contract

Recommend one versioned allowlist shared across errors, traces, logs, metrics,
monitors, and alerts. Start with the applicable fields below; omit fields with
no owner or diagnostic use:

- identity: `service`, `subsystem`, `operation`, `environment`, `release`,
  `deployment_id`;
- correlation: `trace_id`, `span_id`, `request_id`, `execution_id`, bounded
  `attempt`;
- result: `failure_class`, `status`, numeric `duration` with one documented
  unit, `retryability`, `impact`;
- operations: `owner`, `runbook`, and packet-level direct `issue_url` and
  `trace_url`.

For every field, the plan specifies semantic owner, source, type, allowed values
or format, sensitivity, tenant scope, expected cardinality, applicable signals,
indexing, retention, and fallback when unavailable.

Correlation rules:

1. Set `service`, `environment`, `release`, and `deployment_id` once from
   authoritative runtime or release configuration. Keep their meanings stable
   across signals.
2. Adopt an existing valid trace context at ingress or create one. Preserve it
   across supported service calls. Keep `request_id` distinct when the product
   already exposes a safe request handle.
3. Create one `execution_id` for a logical async execution and preserve it
   across queue boundaries and retries. Record attempts separately; do not
   create a new logical execution for each retry.
4. Use stable route, RPC, command, or job names for `operation`. Raw URLs,
   query strings, filenames, user input, and exception text are not operations.
5. Use a bounded failure taxonomy for `failure_class`, bounded enums for
   `status`, `retryability`, and `impact`, and one unit for `duration`.
6. Put unbounded IDs only in allowlisted logs, errors, or spans where policy and
   backend support them. Never use request, trace, execution, user, tenant,
   URL, error-message, or free-text values as metric dimensions.
7. Generate `issue_url` and `trace_url` in the audit or notification consumer
   from backend identifiers. Do not emit full vendor URLs as high-cardinality
   telemetry attributes.
8. Document sampling as one correlated policy. State how errors, slow paths,
   low-volume paths, and unsampled traces behave; never imply that a sample
   proves absence.

Privacy and security are schema constraints, not cleanup:

- emit bounded event names and allowlisted typed attributes;
- exclude secrets, credentials, auth codes, cookies, authorization values, raw
  request or response bodies, arbitrary diagnostic text, and prompt, response,
  tool, or message content;
- identify PII, quasi-identifiers, tenant IDs, cross-tenant joins, data region,
  access roles, retention, and deletion requirements before egress;
- filter at the producer before network transmission; backend scrubbing is a
  second control, not the first;
- treat monitor headers, query parameters, request bodies, baggage, span and log
  attributes, attachments, stack locals, replay, and profiles as external
  egress;
- prefer positive allowlists to redaction patterns; verify filters with
  synthetic canary strings, never real secrets or personal data;
- keep tenants isolated in attributes, queries, dashboards, alerts, exports,
  and direct links according to the system's authority.

Completion criterion: the packet contains one field dictionary and propagation
path that coding and operations agents can implement without inventing names,
cardinality, privacy, or ownership decisions.

## 7. Research and choose the provider boundary

After the system map exposes the required signals, research the installed SDKs,
provider features, pricing or quotas, retention, APIs, and integrations against
current official documentation. Verify exact platform and version support.
Use `skill://research`; record the chosen design, rejected designs, and open
questions. Re-read the exact authorities below before relying on them; this
index records the primary sources used to author the skill, not permanent
capability truth.

Primary-source index, accessed 2026-08-25:

- Sentry: [product signals](https://docs.sentry.io/product/sentry-basics/),
  [uptime](https://docs.sentry.io/product/monitors-and-alerts/monitors/uptime-monitoring/),
  [cron check-ins](https://docs.sentry.io/product/monitors-and-alerts/monitors/crons/job-monitoring/),
  [alerts](https://docs.sentry.io/product/monitors-and-alerts/alerts/),
  [Microsoft Teams](https://docs.sentry.io/integrations/notification-incidents/msteams/),
  [source-map CLI](https://docs.sentry.io/platforms/javascript/sourcemaps/uploading/cli/),
  [API](https://docs.sentry.io/api/),
  [quota controls](https://docs.sentry.io/pricing/quotas/), and
  [data scrubbing](https://docs.sentry.io/security-legal-pii/scrubbing/advanced-datascrubbing/).
- Vendor-neutral semantics:
  [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/),
  [resources](https://opentelemetry.io/docs/concepts/resources/), and
  [log correlation](https://opentelemetry.io/docs/specs/otel/logs/data-model/);
  [Google SRE monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
  and [SLO alerting](https://sre.google/workbook/alerting-on-slos/); and
  [Kubernetes probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/).

Compare three boundary-complete designs when the vendor boundary is material:

1. deepen and consolidate the adequate existing stack;
2. use Sentry as the integrated application-observability plane plus the
   existing hosting or infrastructure plane;
3. use an OpenTelemetry-first export path with specialized backends where
   portability or system shape justifies its additional ownership.

Compare data ownership and path, failure coverage, unsupported boundaries,
privacy and tenancy, operator work, SDK/runtime support, correlation, retention,
quota and spend, alert routing, migration and deletion, failure of the
observability provider, and reversibility. Converge on one design. Do not add a
second provider that duplicates adequate coverage without closing a named gap.

When no adequate application plane exists and current support, privacy, quota,
and access evidence allow it, favor Sentry as the integrated default for SDK
errors, tracing, structured logs, application metrics, releases, source maps or
debug artifacts, uptime, cron monitors, alert rules, and direct issue or trace
investigation. Consider profiling and replay only when a named diagnostic need
and explicit privacy/overhead decision justify them.

State Sentry's boundary. SDK telemetry cannot independently prove Sentry's own
availability, public reachability from every required network, host or kernel
health, DNS/TLS paths it cannot reach, storage capacity, backup restoration,
queue or database state not emitted by the application, third-party provider
correctness, or deep product correctness. Private endpoints may be unreachable
to hosted uptime probes. Close each such gap with a provider-native signal,
independent black-box probe, infrastructure backend, or product-owned receipt or
freshness check. Avoid circular proof where the monitored system owns its only
monitor.

For a Sentry recommendation, the plan names SDK/project/environment ownership,
DSN and token secret boundaries, release and deployment identity, sampling,
quotas, retention, data filters, source-map or debug-artifact path, monitor
configuration, alert rule, and read-only CLI/API verification. Pass explicit
organization and project identity to automation; never rely on ambient defaults.
Do not print tokens or DSNs in packet evidence.

Completion criterion: one provider architecture wins on actual boundary
evidence; unsupported failures and independent probes are explicit; every
vendor claim cites current official documentation.

## 8. Design alerting and Microsoft Teams routing

Separate collection from interruption. Logs are stored telemetry. Alerts are
purpose-built evaluated rules that route action. Never forward every log, every
exception, or an unfiltered issue stream to Microsoft Teams.

Route only actionable classes such as:

- confirmed external outage or sustained reachability regression;
- a new production regression with bounded impact;
- an actionable fatal failure;
- a sustained SLO, error, latency, saturation, freshness, queue-age, or job
  threshold breach.

Each route specifies source, environment, rule, threshold and window, failure
and recovery tolerance, severity, owner, Teams team/channel, runbook, direct
issue/trace/query links, acknowledgment and escalation, maintenance behavior,
and rollback. Tune for false positives, low traffic, flapping, duplicate paths,
reset time, and observability-provider outages.

Sentry's Microsoft Teams integration installation is human OAuth/admin work.
The packet identifies the required Sentry owner/manager/admin and Teams admin or
channel owner, target tenant/team/channel, approver, and verification scenario.
It does not install the integration. Identity linking for interactive message
actions is separate human work. Coding agents may implement repository-owned
alert definitions or verification scripts only after the human integration and
scope decisions are complete.

Completion criterion: every proposed interruption is actionable, owned,
noise-bounded, linked to diagnosis, and separated from raw logs; human OAuth and
admin steps remain explicit operator work.

## 9. Produce the deletion-first remediation plan

The audit never implements remediation. Return ordered slices in this sequence:

0. **Delete and consolidate:** remove unsupported, duplicate, stale, noisy, or
   unowned signals and routes; preserve a signal proven to catch real defects.
1. **External reachability:** add an independent non-writing black-box probe for
   DNS, TLS, connect, status, timeout, and bounded response semantics.
2. **Dynamic liveness:** add a cheap non-cached process-progress check with no
   remote dependency fan-out.
3. **Bounded readiness:** check only dependencies required to accept traffic,
   with timeouts and cascade-safe orchestrator semantics.
4. **Application and backend instrumentation:** establish release identity,
   context schema, errors, traces, structured logs, metrics, workers, jobs,
   database calls, and external dependency spans.
5. **Functional checks:** add read-only correctness, real receipt, and freshness
   evidence. Never create fake ledger facts or other production business data.
   Keep any write-path synthetic or fault injection in isolated staging with
   dedicated fixtures and cleanup.
6. **Alert routing:** implement SLO- or impact-shaped rules, direct diagnostic
   links, runbooks, ownership, escalation, and approved Teams routing.
7. **Staging fault injection:** exercise process stalls, dependency failure,
   job failure or miss, bad release artifacts, and notification failure without
   production writes.
8. **Evidence:** verify fresh signal retrieval, correlation, redaction,
   source-map or debug symbol resolution, failure and recovery tolerances,
   routing, runbooks, and independent-monitor behavior.
9. **Rollout:** canary by service, environment, signal, and quota; compare
   overhead, volume, spend, gaps, and alert precision against the accepted
   baseline.
10. **Soak:** observe for the evidence-backed window, verify recovery and reset,
    tune or roll back noisy signals, and close only with named owner approval.

Every slice includes:

- outcome, rationale, accepted decisions, non-goals, and unchanged invariants;
- exact affected repository files, runtime/provider objects, owner, and data
  path, or an explicit discovery task when evidence cannot name them;
- prerequisites and migration/deletion order with no compatibility shim;
- field contract, privacy review, sampling, retention, quota, spend, and
  expected overhead;
- executable acceptance scenarios at reachability, liveness, readiness,
  correctness, instrumentation, routing, failure, and recovery boundaries;
- required evidence artifact, source and deployed identity, query or direct
  link, and evidence owner;
- reversible rollout unit, rollback action, rollback proof, and stop condition.

At minimum, stop a rollout on secret or cross-tenant egress, identity mismatch,
unbounded cardinality, unexplained quota growth, material runtime overhead,
telemetry-caused failure, alert flooding or flapping, unsafe production writes,
unsupported provider behavior, missing owner, or a failed acceptance scenario.
Do not invent numeric limits: derive them from current baselines, SLOs, budgets,
provider constraints, or an explicit operator decision.

Completion criterion: the plan is executable by coding and operations agents in
order, every slice has acceptance, evidence, rollback, and stop conditions, and
no slice performs remediation during the audit.

## 10. Deliver the audit packet

Return one packet with this structure:

```markdown
# Observability audit: <system>
## Controlling verdict
## Scope, identities, exclusions, and primary-source index
## System and failure-path map
## Signal semantics and probe-layer definitions
## Coverage matrix
## Maturity assessment by failure path
## Findings, ordered by impact and dependency
## Context field dictionary and propagation path
## Privacy, tenancy, egress, sampling, retention, quota, and cost policy
## Provider designs considered
## Chosen architecture, Sentry fit, and unsupported boundaries
## Alert and Microsoft Teams routing design
## Phased remediation plan
## Acceptance scenarios and evidence requirements
## Rollout, rollback, stop, and soak policy
## Settled decisions
## Explicit unknowns and blocked slices
## Rejected options and reasons
```

The controlling verdict answers: what failures are invisible, what is noisy or
unsafe, what design wins, what gets built first, and which decision or access
gap blocks work. Keep `Absent`, `Unknown`, and `Not applicable` distinct.
Include direct current issue, trace, query, monitor, release, and alert links
only when read-only evidence proves they exist and tenant access is safe.

Before delivery, audit the audit: account for every inventory surface and signal
class; reject uncited findings; remove duplicate recommendations and arbitrary
numbers; verify Sentry claims against current primary docs; check that no
production write probe, secret, PII, tenant leakage, prompt content, or raw body
entered the packet; and confirm every plan slice has an owner, evidence,
rollback, and stop condition.

Completion criterion: every finding cites a primary record read now; every
material failure path is observed, partial, absent, unknown, or not applicable;
the chosen design and rejected alternatives are evidence-backed; the context
contract is implementation-ready; and the target repository and system remain
unchanged.
