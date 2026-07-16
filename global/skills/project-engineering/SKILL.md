---
name: project-engineering
description: |
  Adopt or audit a repository's project-engineering fitness function: map
  applicable obligations to repo-owned commands, policy and evidence paths,
  Factory integrations, and expiring waivers. Use when: "adopt project
  engineering" or "audit this repo's engineering profile".
argument-hint: "[repo-path] [adopt|audit]"
---

# /project-engineering

Make the project's engineering contract legible without imposing a fleet-wide
layout. The repo owns its commands and paths; this skill composes their
applicability and evidence into one fitness function.

## Branch

| Trigger | Action | Completion criterion |
|---|---|---|
| **Adopt** — no project profile, or the operator asks to adopt the contract | Read the live repo, classify its obligations, and fill `templates/project-profile.md` at the repo's existing governance location. Record missing surfaces as gaps, not invented paths; do not force a filename or root layout. | Identity fields are complete; every obligation row is applicable, not applicable with a reason, or waived with complete waiver metadata; every applicable obligation resolves to a command, policy path, evidence path, service, or durable gap; every proof-map row resolves to evidence or a project-specific non-applicability reason. |
| **Audit** — a profile exists, or the operator asks whether the repo conforms | Read `references/profile-contract.md`, execute safe declared commands and probes, resolve every pointer, and compare live evidence with the profile. Produce a proof-classed gap report; update the profile only when requested. | Every declared pointer is verified or named as stale/missing, every applicable obligation has current evidence or a gap, and no completion claim rests on declaration alone. |

## Five proof classes

Keep these distinct in the profile and report:

1. **Declaration** — applicability, policy, command, service, owner, waiver.
2. **Deterministic gate** — formatting, lint, types, tests, supply chain,
   changed-line coverage, and mutation thresholds.
3. **Live probe** — the real CLI, browser, API, consumer, runtime, restore, or
   production path exercised at its boundary.
4. **Capability eval** — a held-out task producing fresh output plus a grader.
5. **Fresh judgment** — artifact-only critique for irreducible architectural
   or product judgment.

A declaration routes proof; it never substitutes for the other classes. Load
[`references/profile-contract.md`](references/profile-contract.md) when
classifying a repo, filling the template, or auditing evidence.

## Routing

Use the existing owner for method; keep this skill at the composition layer.

| Concern | Owner |
|---|---|
| Fast/full gates, coverage, mutation, supply chain | `primitives/skills/ci/SKILL.md` and `primitives/shared/references/quality-gates.md` |
| Runtime and user-boundary proof | `primitives/skills/qa/SKILL.md` and `primitives/shared/references/verification-system-first.md` |
| Model or agent capability | `primitives/skills/eval-design/SKILL.md` |
| Canary, Powder, Landmark | `primitives/skills/factory-apps/SKILL.md` |
| Module depth, seams, dependency direction | `primitives/skills/.external/mattpocock-codebase-design/SKILL.md` |
| Application-only obligations and waivers | `primitives/shared/references/application-floor.md` |

Return the populated profile plus a gap report grouped by proof class. Route
leaf implementation to the owning skill; do not expand this audit into every
remediation.
