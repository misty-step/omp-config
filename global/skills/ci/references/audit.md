# CI Audit Rubric

Use this rubric to judge whether a repo's CI is strong, fast, portable, and legible to agents.
Load `host-agnostic-ci.md` first for host-agnostic CI design.

For consumer repos, identify the repo-owned gate first.
Read root instructions, package manifests, CI workflows, hooks, and shipped scripts.
Apply this rubric to the repo's actual gate.


## Required Checks

- One repo-owned contract is named: command, script, Dagger function, Make/Just/Task target, or build-system target.
- Local, GitHub Actions, Azure, or other runners call the same repo-owned contract or a clearly documented fast/full tier.
- Keep fast and full gates distinct unless live evidence proves one gate is comprehensive and fast enough for repeated agent use.
- Check generated `index.yaml`, docs, API clients, schemas, fixtures, or lockfiles when relevant.
- Cover format, lint, typecheck, tests, and build/package checks in the tier where they belong.
- Scan working-tree content and Git/PR metadata for secrets.
  Include the commit message file, outbound commit subjects/bodies, PR title/body, release notes, changelog text, generated summaries, and logs.
  Name the field and rule in each finding.
  Never print the secret value.
- Run at least one protection before remote publication.
  Use server-side push protection or a pre-receive hook when available.
  Otherwise, use `commit-msg` plus `pre-push` hooks.
  Keep CI required because local hooks can be bypassed.
- Generate or explicitly waive reports.
  Include a run digest, test report, coverage/diff-coverage, security findings, artifact checksums, and performance or mutation output where relevant.
- Prevent path filters from skipping required hosted checks into false-green or stuck-pending states.
  Add sentinel checks when path filters could skip required hosted checks or leave them stuck pending.


## Speed Rules

- Keep the docs/backlog-only push path to seconds, not minutes.
- Keep the fast local gate free of Docker and network unless container or service orchestration is the point.
- Use Dagger when it provides portability, pinned services, caching, containerized dependency graphs, or traceability.
  Do not use it as a slow wrapper around ordinary host commands in the inner loop.
- If external API behavior is required and `emulate.dev` supports the provider, use local emulation with seeded fixtures as the offline behavioral gate.
- Put expensive checks behind explicit commands or path-scoped triggers.
- If the full local gate is too slow, split fast and full tiers.
  Do not delete the invariant.
- Track or report gate duration, critical path, and cache behavior when the substrate exposes them.


## Audit Findings

| Severity | Meaning | Action |
|---|---|---|
| high | Missing repo-owned gate, hosted provider owns the only contract, source changes bypass required checks, false-green path filters, or secrets can reach remote commit/PR metadata unscanned | Fix inline |
| med | Gate is too slow, noisy, host-specific, report-poor, or duplicates an invariant | Simplify inline or file backlog |
| low | Naming/docs drift | Fix when touching nearby files |

Treat historical Dagger references in archived backlog as no findings.
Do not let live skills, root docs, hooks, or generated reference pages imply one universal substrate.
Accept Dagger, direct host scripts, and build-system targets when repo evidence earns them.
