---
name: security-review
description: Run the approved tri-model adversarial audit and validate exploitable security findings.
disable-model-invocation: true
---

# Security review

Security review needs offensive reasoning from the approved independent models,
not the session primary. The bundled script owns council model selection. The
`security-reviewer` agent owns validation and adjudication. This skill is
read-only.

## Bound

Record the exact revision, dirty state, target files, trust boundaries, assets,
untrusted inputs, privileges, secrets, persistence, and exclusions. Read
`references/audit-domains.md` and `references/cwe-matrix.md`.

Done when every changed trust boundary is in scope.

## Run the council

From the target repository, run the installed script:

```sh
node <skill-directory>/scripts/audit.mjs
node <skill-directory>/scripts/audit.mjs --staged
node <skill-directory>/scripts/audit.mjs --commit HEAD
node <skill-directory>/scripts/audit.mjs --file <path>
```

Require every configured model to return or report the lane unavailable. Do not
silently replace a model or accept a partial council as complete.

Done when the report binds every response to the target revision and model.

## Validate

Send each candidate to `security-reviewer`. Require an attacker-controlled
source, complete path through current controls, dangerous sink or broken
invariant, reproducible preconditions, impact, and smallest remediation.
Reject unreachable, controlled, duplicated, speculative, or pre-existing
findings unrelated to the target.

Consensus supports confidence; it does not replace mechanism evidence.

Done when each finding is confirmed, rejected, or unavailable with a reason.

## Deliver

Return scope, model receipts, confirmed findings by severity, rejected
candidates, residual risk, and evidence gaps. Record accepted remediation with
an owner. Do not design or apply a security repair in this audit. Re-audit any
external repair on its exact revision.

Done when every confirmed finding has operator triage and one durable owner.
