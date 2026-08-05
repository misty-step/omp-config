---
disable-model-invocation: true
name: project-engineering
description: |
  Adopt or audit a repository's project-engineering fitness function. Map
  obligations to repo-owned commands, policy and evidence paths, Factory
  integrations, and expiring waivers. Use when: "adopt project engineering"
  or "audit this repo's engineering profile".
argument-hint: "[repo-path] [adopt|audit]"
---

# /project-engineering

Make the project's engineering contract clear without imposing a fleet-wide
layout. The repo owns its commands and paths. This skill combines their
applicability and evidence into one fitness function.

## Branch

The chief assigns **Adopt** to `builder` and **Audit** to read-only `architect`.
An architect reports proposed profile changes. A builder applies requested updates.

| Trigger | Action | Completion criterion |
|---|---|---|
| **Adopt** — no project profile, or the operator asks to adopt the contract | Read the live repo, classify its obligations, and fill `templates/project-profile.md` at the repo's existing governance location. Record missing surfaces as gaps, not invented paths; do not force a filename or root layout. | Identity fields are complete; every obligation row is applicable, not applicable with a reason, or waived with complete waiver metadata; every applicable obligation resolves to a command, policy path, evidence path, service, or durable gap; every proof-map row resolves to evidence or a project-specific non-applicability reason. |
| **Audit** — a profile exists, or the operator asks whether the repo conforms | Read `references/profile-contract.md`, execute safe declared probes, resolve every pointer, and compare live evidence with the profile. Produce a proof-classed gap report and proposed profile changes without mutation. | Every declared pointer is verified or named as stale/missing, every applicable obligation has current evidence or a gap, and no completion claim rests on declaration alone. |

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

Use a declaration to route proof. Never substitute it for another class. Load
[`references/profile-contract.md`](references/profile-contract.md) when you
classify a repo, fill the template, or audit evidence.


## Routing

Use the existing owner for each method.
The chief dispatches additional lanes. Keep this skill at the contract layer.

| Concern | Owner |
|---|---|
| Fast/full gates, coverage, mutation, supply chain | `global/skills/ci/SKILL.md` and `global/references/quality-gates.md` |
| Runtime and user-boundary proof | `global/references/verification-system-first.md`; the chief dispatches `verifier` with `verify-live` |
| Model or agent capability | `global/skills/eval-design/SKILL.md` |
| Canary, Powder, Landmark | `global/skills/factory-apps/SKILL.md` |
| Module depth, seams, dependency direction | `global/external/mattpocock-skills/codebase-design/SKILL.md` (`mattpocock-codebase-design`) |
| Application-only obligations and waivers | `global/references/application-floor.md` |

Return the populated profile and a gap report grouped by proof class.
The chief routes implementation to the owning native agent and skill.
Do not expand this audit into every remediation.
