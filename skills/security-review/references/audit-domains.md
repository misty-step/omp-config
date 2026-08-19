# Security Audit Domains & Methodology

The Security Review Council tasks three frontier reasoning models—**GLM 5.3**, **Kimi K3**, and **DeepSeek V4 Pro 0813**—to execute independent, deep, exhaustive security audits across the entire vulnerability spectrum.

---

## Audit Investigation Domains

Every model audits the target scope across all five core vulnerability classes:

### 1. Sinks, Injections & Memory Corruption
- **Command & Code Injection**: OS command injection (CWE-78), eval/code injection (CWE-94), argument injection (CWE-88).
- **Query & Template Injections**: SQL injection (CWE-89), NoSQL injection, Server-Side Template Injection (SSTI, CWE-1336), LDAP/XPath injection.
- **Regular Expressions**: ReDoS (CWE-1333), catastrophic backtracking on untrusted input.
- **Deserialization & Parsers**: Unsafe object deserialization (CWE-502), XML External Entity (XXE, CWE-611), Prototype Pollution (CWE-1321).
- **Memory & Arithmetic**: Buffer overflows (CWE-120), out-of-bounds access (CWE-125/787), integer overflow/underflow (CWE-190), use-after-free (CWE-416).

### 2. Taint Flow & Input Validation
- **Source-to-Sink Tracing**: Untrusted input originating from HTTP parameters, headers, cookies, webhooks, CLI flags, environment variables, or file uploads reaching sensitive functions without sanitization.
- **Encoding & Escaping Errors**: Missing or double encoding, improper context escaping in HTML, shell, database, or logging outputs.
- **Type Coercion & Schema Validation**: Loose type comparisons, missing validation on request boundaries, unconstrained parameter sizes.

### 3. Authentication, Authorization & Session Management
- **Broken Object Level Authorization (BOLA / IDOR)**: Accessing resources belonging to other tenants or users without ownership validation (CWE-639).
- **Broken Function Level Authorization**: Accessing privileged or administrative endpoints without proper role checks (CWE-285).
- **Authentication & Token Flaws**: Hardcoded credentials (CWE-798), static API keys, weak JWT signing/verification, missing expiry, predictable tokens.
- **Session Lifecycle**: Session fixation, insecure cookie attributes (missing HttpOnly, Secure, SameSite), improper logout invalidation.

### 4. Business Logic, Concurrency & State Machines
- **Logic Flaws**: Step-skipping in multi-step workflows, price/quantity manipulation, balance depletion bypasses.
- **Race Conditions & Concurrency**: Time-of-Check to Time-of-Use (TOCTOU, CWE-367), unsynchronized shared state access, double-spend / duplicate action races.
- **Error Handling & State Desync**: Partial failure states leaving transactions incomplete or corrupted, unhandled promise rejections crashing processes.

### 5. Threat Modeling, Architecture & Systemic Resilience
- **Trust Boundaries**: Crossings between public/private networks, client/server boundaries, tenant isolation mechanisms.
- **Secret & Key Security**: Leakage in logs, source code, error messages, debug endpoints, or client bundles.
- **Cryptographic Weaknesses**: Insecure algorithms (MD5, SHA1, DES), ECB mode, hardcoded IV/salt, broken signature checks (CWE-327, CWE-328).
- **Denial of Service (DoS) & Blast Radius**: Unbounded resource allocation (memory, disk, connections, worker threads), algorithmic complexity attacks, cascading failure modes.

---

## Attacker Mindset & Exploit Verification

When evaluating code, the council operates with an adversarial mindset:
1. **Identify Entrypoints**: Locate all untrusted attack surfaces.
2. **Trace Propagation**: Track data flow through functions, state mutations, and serialization boundaries.
3. **Trigger Sink**: Prove how an attacker constructs a malicious payload to reach a dangerous sink or break an invariant.
4. **Determine Blast Radius**: Quantify the maximum consequence (RCE, data breach, privilege escalation, service disruption).
5. **Formulate Robust Remediation**: Design minimal, source-level fixes that eliminate the root cause and provide defense-in-depth.
