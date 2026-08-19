---
name: security-review
description: Tri-model adversarial security audit using GLM 5.3, Kimi K3, and DeepSeek V4 Pro 0813 via OpenRouter.
disable-model-invocation: true
---

# Security Review

Execute an adversarial security audit across three frontier models via OpenRouter:
- **DeepSeek V4 Pro 0813** (`deepseek/deepseek-v4-pro-0813`): Code & Sink Specialist (Injection, Memory, Deserialization, Parsers).
- **Kimi K3** (`moonshotai/kimi-k3`): Taint & Logic Specialist (Data Flow, State Machines, Auth/Authz, TOCTOU).
- **GLM 5.3** (`z-ai/glm-5.3`): Threat Model & Architecture Specialist (Trust Domains, Secrets, Blast Radius, Supply Chain).

---

## 1. Scope & Recon

Establish the security audit boundary from the repository state, request, or target files:

- **Target scope**: Unstaged working tree diff, staged changes (`--staged`), commit (`--commit <hash>`), or explicit files/directories (`--file <path>`).
- **Trust boundaries**: Identify untrusted inputs (HTTP requests, CLI args, environment variables, webhooks, IPC, file system) and external dependencies.
- **Critical assets**: Sensitive data stores, credentials, authorization gates, and privileged execution boundaries.

Completion criterion: Target scope, untrusted inputs, and trust boundaries identified.

---

## 2. Tri-Model Council Execution

Run the multi-model audit engine across the target scope.

### Execution via Bundled Script
Run `scripts/audit.mjs` directly from the skill directory:

```bash
# Audit working tree changes
node skills/security-review/scripts/audit.mjs

# Audit staged changes
node skills/security-review/scripts/audit.mjs --staged

# Audit specific commit
node skills/security-review/scripts/audit.mjs --commit HEAD

# Audit specific files or directories
node skills/security-review/scripts/audit.mjs --file src/auth.ts --file src/server.ts
```

The script queries all three models in parallel, extracts structured JSON findings, correlates matching issues, and generates:
- Markdown audit report: `/tmp/security-review-<id>.md`
- Hunk walkthrough annotations: `/tmp/security-walkthrough-<id>.json`
- Raw findings data: `/tmp/security-findings-<id>.json`

For model domain details and lens reference, see `references/lenses.md`.

Completion criterion: Tri-model council responses collected from all three models with zero unhandled timeouts.

---

## 3. Adversarial Taint & Exploit Validation

For each candidate finding reported by the council:

1. **Source-to-Sink Trace**: Trace the attacker-controlled input through every intermediate transformation down to the dangerous operation or broken control.
2. **Control Verification**: Inspect existing guards, parameterizations, type bounds, and validation checks along the call chain.
3. **Exploit Path Grounding**: Confirm a concrete trigger sequence exists under real runtime conditions.
4. **False-Positive Filtering**: Discard speculative findings, unreachable sinks, and cosmetic concerns without exploitable mechanisms (see `references/cwe-matrix.md`).

Completion criterion: Every candidate finding verified against the codebase or rejected with explicit rationale.

---

## 4. Adjudication & Consensus Synthesis

Group and classify surviving findings:

- **Consensus Rating**:
  - **Tri-Model Consensus (3/3)**: Unanimous agreement across all three models. High confidence.
  - **Dual-Model Consensus (2/3)**: Agreement between two models (e.g. Code Sink + Logic Boundary). High confidence.
  - **Solo Lens Finding (1/3)**: Specialized finding identified by one model. Requires verified call chain.
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

## 6. Minimal Verified Remediation

For each accepted finding:

1. **Root Cause Fix**: Eliminate the vulnerability at the source or sink boundary (e.g., parameterize query, enforce strict whitelist, sanitize input, eliminate TOCTOU).
2. **Defense-in-Depth**: Add secondary boundary validation where appropriate without adding unnecessary abstraction layers.
3. **Verification**: Execute a narrow regression scenario or test demonstrating the exploit payload is safely rejected.
4. **Re-Audit**: On non-trivial repairs, re-run the Tri-Model Council to ensure zero new vulnerabilities were introduced.

Completion criterion: Every accepted finding repaired and verified with zero regressions.
