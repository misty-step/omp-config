# Security Review Lenses

The Security Review Council pairs three frontier models across orthogonal security domains to maximize vulnerability detection while eliminating single-model blind spots.

---

## 1. DeepSeek V4 Pro 0813 (`deepseek/deepseek-v4-pro-0813`)

### Assigned Lens
**Code Security & Dangerous Sinks**

### Audit Domain
- **Injection Sinks**: OS command injection (CWE-78), SQL/NoSQL injection (CWE-89), template injection (CWE-1336), regex injection / ReDoS (CWE-1333).
- **Memory & Arithmetic Safety**: Buffer overflows (CWE-120), out-of-bounds reads/writes (CWE-125/CWE-787), integer overflow/underflow (CWE-190), use-after-free (CWE-416).
- **Deserialization & Parsing**: Unsafe object deserialization (CWE-502), XML External Entity (XXE, CWE-611), prototype pollution (CWE-1321), parser state machine desync.
- **Unhandled Error States**: Panic on untrusted input, unhandled exception paths leading to denial of service or state corruption.

### Attacker Mindset
"How can I construct a crafted payload that breaks assumptions at the sink or parser level to hijack execution?"

---

## 2. Kimi K3 (`moonshotai/kimi-k3`)

### Assigned Lens
**Taint-Flow & Logic Boundaries**

### Audit Domain
- **Taint-Flow Analysis**: Tracing untrusted source input across module interfaces, service boundaries, and state stores to unchecked operations.
- **Broken Access Control & Auth**: Insecure Direct Object References (IDOR, CWE-639), privilege bypass (CWE-285), missing authentication gates (CWE-306), token validation flaws.
- **State Machine & Logic Flaws**: Invalid state transitions, step-skipping in multi-step workflows, price/quantity manipulation, balance depletion bypasses.
- **Concurrency & Races**: Time-of-Check to Time-of-Use (TOCTOU, CWE-367), un-synchronized shared state, double-spend / double-submission races.
- **Side-Channel & Data Leaks**: Timing discrepancies in authentication/crypto checks, error messages leaking internal state.

### Attacker Mindset
"How can I permute the order of operations or manipulate identity/state to bypass business logic and authorization?"

---

## 3. GLM 5.3 (`z-ai/glm-5.3`)

### Assigned Lens
**Threat Modeling & System Architecture**

### Audit Domain
- **Trust Domain Boundaries**: Boundary crossing between client/server, public/private networks, tenant-isolation failures.
- **Privilege Escalation**: Vertical and horizontal privilege escalation paths across system roles and processes.
- **Secret & Key Management**: Hardcoded credentials, insecure key storage, predictable entropy, token leakage in logs or headers.
- **Cryptographic Misuse**: Weak algorithms, ECB mode, broken signature verification, static IV/nonces (CWE-327, CWE-328).
- **Denial of Service & Blast Radius**: Unbounded resource allocation (memory, disk, connections, worker exhaustion), amplification vectors, single point of systemic failure.
- **Supply Chain & Dependencies**: Dangerous module imports, untrusted script execution, build-time code execution risks.

### Attacker Mindset
"How can I exploit the systemic architecture and trust boundaries to compromise tenant isolation or cause systemic failure?"
