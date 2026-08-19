# CWE & Severity Matrix

Reference classification and severity thresholds for the Security Review Council.

---

## 1. Severity Definitions

| Severity | Impact Description | Action Requirement | Examples |
|---|---|---|---|
| **Critical** | Remote code execution, unauthenticated auth bypass, full system compromise, massive tenant data exfiltration | Immediate operator blocker. Requires proof & immediate fix. | OS Command Injection (CWE-78), Remote Code Execution (CWE-94), Unauthenticated SQLi (CWE-89), Admin Auth Bypass (CWE-287). |
| **High** | Authenticated privilege escalation, broken access control (IDOR), sensitive data leakage, severe Denial of Service | Gate item. Must be addressed before production release. | Insecure Direct Object Reference (CWE-639), CSRF on critical actions (CWE-352), Persistent XSS (CWE-79), SSRF (CWE-918). |
| **Medium** | Defense-in-depth failure, subtle logic bypass under constrained conditions, improper session handling, info disclosure | Review item. Address in planned refactoring. | Reflected XSS with CSP (CWE-79), Missing rate limiting (CWE-770), Verbose stack traces (CWE-209), Weak hashing (CWE-328). |
| **Low** | Hardening opportunity, minor informational leak, outdated protocol defaults without exploit path | Log item. Address during routine maintenance. | Missing security headers (HSTS/CSP), Verbose server banners (CWE-200), Minor cookie flags missing. |

---

## 2. Multi-Model Consensus Confidence

The council evaluates findings across GLM 5.3, Kimi K3, and DeepSeek V4 Pro 0813:

- **Tri-Model Consensus (3/3 models)**:
  - Unanimous confirmation across all three independent lenses.
  - High confidence; verified attack path and boundary failure.
- **Dual-Model Consensus (2/3 models)**:
  - Confirmed across two lenses (e.g. Code Sink + Logic Boundary).
  - High confidence; actionable remediation recommended.
- **Solo Lens Finding (1/3 models)**:
  - Discovered by a single specialized lens (e.g. subtle memory overflow or complex trust boundary violation).
  - Requires strict validation of the end-to-end call chain before presenting as a Take item.

---

## 3. False-Positive & Speculative Finding Filters

A candidate finding is **REJECTED** if it matches any of the following criteria:

1. **Unreachable Sink**: The tainted parameter cannot actually be reached by an external attacker, or is strictly constrained to immutable internal constants.
2. **Missing Exploit Mechanism**: Vague "this might be unsafe if someone changes caller in the future" speculation without a current reachable execution path.
3. **Cosmetic / Non-Security Refactor**: Code style, general clean-code preferences, or performance optimizations masquerading as security flaws.
4. **Assumed Invariants**: Flagging standard framework idioms that are inherently safe by framework design (e.g., parameterised queries flagged as raw concatenation).
