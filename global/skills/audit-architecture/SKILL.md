---
disable-model-invocation: true
name: audit-architecture
description: Chief-run static architecture audit: discover entrypoints, define target, audit lenses, assess, remediate, and verify.
argument-hint: "[target] [notes]"
---

# /audit-architecture

The chief runs this loop and dispatches every lane through `skill://dispatch`.
Name each lane's role, model:reasoning, skills, tools, verifier, and contract.
Include the exact child boundary sentence `You are a subagent. Don't run memo.`
Judge structure, interfaces, and test defense from source. Do not drive a browser.
Route live behavior to `qa` or `audit-product`.

## Audit spine

1. **Discover.** Dispatch read-only `magellan` for repo-wide sweeps or `scout` for bounded subsystems. Inventory public APIs, routes, CLIs, jobs, extension points, schemas; each module, interface, and caller; and tests, gates, ADRs, and project rules. Name every reachable entrypoint with a file path. List unknowns instead of guessing.
2. **Define target.** Write the target state before auditing. Dispatch `daedalus` first for XL scope or contested decomposition. Apply [`references/target-state.md`](references/target-state.md). Write `.evidence/quality/audit-architecture/target-state.md` in the audited repository. Get operator acceptance when direction is contested. Judge only against the accepted target.
3. **Audit.** Fan out one fresh-context, read-only `code-critic` per lens in parallel. Use `ousterhout` and `delete-first` from `global/references/lenses.md`. Inject `review-tests` to judge observable-contract defense, not line execution. Add `security` or `works` only when the target includes them. Require file:line evidence, a target clause, and severity. Require findings or an explicit clean pass from every lane. A lane that edits fails its contract.
4. **Assess.** Merge findings into `.evidence/quality/audit-architecture/assessment.md`. Rank gaps and map each to target-clause evidence. Preserve strengths. Record suppression reasons, remediation shape, blast radius, and closure verification for each gap. Have the operator, or the delegated chief, accept, suppress with reason, or reject every finding. Only accepted gaps proceed.
5. **Remediate.** Send a ranked findings packet to one `fixer` with a two-round cap. It fixes causes and never weakens a gate or test. Send each independent structural slice to one `builder`; use `daedalus` first when slices couple. Prefer deleting a module over wrapping it. Require a landed change or a named blocker with evidence for every accepted gap.
6. **Verify.** Keep verification independent of the remediating lane. Have a fresh `code-critic` recheck each remediated interface against its originating lens. Have `qa` exercise each runtime contract; structure claims never replace behavior evidence. Changed contracts need tests that fail on plausible mutations; `review-tests` applies.

## Completion Gate

Follow the Shared Operating Spine (`Prove`, `Durable State and Closeout`) and `global/references/verification-system-first.md`.

- Verify every accepted gap with named evidence, or return it with its blocker. A plausible subset fails.
- Keep both frozen artifacts in the audited repository: `.evidence/quality/audit-architecture/target-state.md` and `.evidence/quality/audit-architecture/assessment.md`.
- Confirm that every strength named in the assessment still holds after remediation.
