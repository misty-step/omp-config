---
name: security-review
description: Tri-model adversarial security audit using GLM 5.3, Kimi K3, and DeepSeek V4 Pro 0813 via OpenRouter.
disable-model-invocation: true
---

# Security Review

Execute a deep, exhaustive, and rigorous adversarial security audit across three frontier reasoning models via OpenRouter:
- **GLM 5.3** (`z-ai/glm-5.3`)
- **Kimi K3** (`moonshotai/kimi-k3`)
- **DeepSeek V4 Pro 0813** (`deepseek/deepseek-v4-pro-0813`)

All three models are concurrently tasked with full-spectrum vulnerability research across injections, taint flow, broken access control, logic defects, concurrency races, cryptography, and systemic architecture.

---

## Model Policy

Security judgment never runs on the session's primary model. Frontier-lab models refuse or soften offensive reasoning. Every phase that weighs exploitability, severity, or repair design belongs to the approved trio:

- **Council queries** (section 2): the bundled script pins GLM 5.3, Kimi K3, and DeepSeek V4 Pro 0813 directly via OpenRouter.
- **Validation, adjudication, recon** (sections 1, 3–4): delegate to the `security-reviewer` agent — read-only, DeepSeek-routed via `task.agentModelOverrides`; the primary forwards evidence and records verdicts verbatim.
- **Remediation** (section 6): blocked. The council emits prose guidance, not diffs, and no approved writable agent exists yet. Record the triage decision and guidance verbatim; re-audit any externally landed repair. Never let the primary design the fix inside this audit.

## 1. Scope & Recon

Establish the security audit boundary from the repository state, request, or target files.

Delegate this section to the `security-reviewer` agent; it is read-only and routed to DeepSeek V4 Pro. The primary supplies the invocation target and receives the boundary summary.

- **Target scope**: Unstaged working tree diff, staged changes (`--staged`), commit (`--commit <hash>`), or explicit files/directories (`--file <path>`).
- **Trust boundaries**: Identify untrusted inputs (HTTP requests, CLI args, environment variables, webhooks, IPC, file system) and external dependencies.
- **Critical assets**: Sensitive data stores, credentials, authorization gates, and privileged execution boundaries.

Completion criterion: Target scope, untrusted inputs, and trust boundaries identified.

---

## 2. Tri-Model Council Execution

Run the multi-model audit engine across the target scope.

### Execution via Bundled Script
Run `scripts/audit.mjs` from the installed skill directory against the target repository:

```bash
# Audit working tree changes
node <skill-directory>/scripts/audit.mjs

# Audit staged changes
node <skill-directory>/scripts/audit.mjs --staged

# Audit specific commit
node <skill-directory>/scripts/audit.mjs --commit HEAD

# Audit specific files or directories
node <skill-directory>/scripts/audit.mjs --file src/auth.ts --file src/server.ts
```

The script queries GLM 5.3, Kimi K3, and DeepSeek V4 Pro in parallel, extracts structured JSON findings, correlates matching issues, and generates:
- Markdown audit report: `/tmp/security-review-<id>.md`
- Hunk walkthrough annotations: `/tmp/security-walkthrough-<id>.json`
- Raw findings data: `/tmp/security-findings-<id>.json`

For exhaustive vulnerability checklist and attack domain details, see `references/audit-domains.md`.

Completion criterion: Tri-model council responses collected from all three models with zero unhandled timeouts.

---

## 3. Adversarial Taint & Exploit Validation

Route each candidate through the `security-reviewer` agent (Model Policy). The primary supplies paths and evidence; it does not judge.

For each candidate finding reported by the council:

1. **Source-to-Sink Trace**: Trace the attacker-controlled input through every intermediate transformation down to the dangerous operation or broken control.
2. **Control Verification**: Inspect existing guards, parameterizations, type bounds, and validation checks along the call chain.
3. **Exploit Path Grounding**: Confirm a concrete trigger sequence exists under real runtime conditions.
4. **False-Positive Filtering**: Discard speculative findings, unreachable sinks, and cosmetic concerns without exploitable mechanisms (see `references/cwe-matrix.md`).

Completion criterion: Every candidate finding verified against the codebase or rejected with explicit rationale.

---

## 4. Adjudication & Consensus Synthesis

Group and classify surviving findings.

Consensus and severity labels come from council output and `security-reviewer` adjudication — never from the primary's own judgment.

- **Consensus Rating**:
  - **Tri-Model Consensus (3/3)**: Unanimous agreement across all three models. High confidence.
  - **Dual-Model Consensus (2/3)**: Agreement between two models. High confidence.
  - **Solo Model Finding (1/3)**: Finding identified by a single model. Requires strict call chain verification.
- **Severity Rating**:
  - `Critical`: Remote code execution, unauthenticated auth bypass, major data exfiltration.
  - `High`: Authenticated privilege escalation, IDOR, sensitive state leak, low-complexity DoS.
  - `Medium`: Defense-in-depth failure, subtle logic bypass, missing rate limits.
  - `Low`: Hardening opportunity, verbose errors, minor configuration improvements.

Completion criterion: Consolidated findings categorized by consensus, severity, CWE, and affected line ranges.

---

## 5. Walkthrough & Operator Triage

1. Review the generated Markdown report.
2. Load the walkthrough notes into the live Hunk session (`skill://hunk`) using the generated sidecar JSON:
   - Walk the operator through each critical and high finding anchored to source lines.
   - Present the concrete attack mechanism, blast radius, and minimal repair.
3. Wait for the operator to accept, defer, or reject each finding before modifying any production code.

Completion criterion: Report presented to the operator, Hunk walkthrough loaded, and triage decisions recorded.

---

## 6. Remediation Handoff (blocked)

No mechanism can author repairs yet: the council emits prose guidance, not diffs, and no approved writable agent exists. For each accepted finding:

1. Record the operator's triage decision with the council's attack path, severity, and remediation guidance verbatim.
2. Open remediation as tracked work for an approved-model agent or patch producer once one exists; until then the fix waits — do not design or apply it in this audit.
3. When an external repair lands, re-run the Tri-Model Council (section 2) over the repaired range.

Completion criterion: every accepted finding carries triage, verbatim council guidance, and a tracked remediation reference; no repair authored here.
