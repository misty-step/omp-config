# Control surfaces

Classify every row as `present`, `recommended`, or `not-applicable`. Cite the
authoritative command/path, trigger, tier, enforcement owner, failure behavior,
bypass route, and evidence. An unchecked absence is an audit failure.

| Domain | Required inventory |
|---|---|
| Authority | root instructions, manifests, lockfiles, generated authority, policy ownership |
| Static quality | formatting, syntax, warnings-as-errors lint, strict types, build/compile, architecture boundaries, dead code, duplication |
| Tests | unit, integration, contract, end-to-end/browser, property/fuzz, mutation, coverage/diff coverage, flakes, seeds, failure artifacts |
| Hooks | checked-in implementation, installer, effective `core.hooksPath`, foreign-hook chaining, commit/push latency, `--no-verify` backstop |
| CI | workflows, repo-owned commands, required-check and branch-rule evidence, path-filter sentinels, timeouts, cancellation, artifact retention |
| Secrets | staged diff, outbound commits and messages, history, PR/release metadata, redaction, missing-tool/error behavior, pinned TruffleHog version |
| Security | SAST, dependency vulnerabilities, licenses, lock integrity, registry existence, provenance, signatures, mutable action/image pins |
| Compatibility | API/schema/migration compatibility, generated drift, supported OS/runtime/toolchain matrix |
| Delivery | packaging, clean install, upgrade, rollback, release and deploy smoke checks, live verification ownership |
| Budgets | performance, resources, binary/artifact size, gate duration, observability and trend evidence |
| Agent resistance | ignored warnings, type escapes, swallowed errors, stubs, dead scaffolding, gate/config tampering, self-attestation |
| Reproducibility | fresh clone/bootstrap, offline behavior, declared tools, cache independence, deterministic or replayable randomness |

Search specifically for checked-in but unwired hooks, folklore scripts, mutable
pins, fail-open scanners, local/CI drift, swallowed exit codes, exclusion growth,
threshold reductions, and controls that pass without exercising their oracle.
