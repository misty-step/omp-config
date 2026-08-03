---
disable-model-invocation: true
name: review-security
description: |
  Security lens for `verifier`: read a diff and find security defects proven
  by the change itself. Check secret leakage, missing or reordered authorization,
  injection, unsafe deserialization, blast-radius growth, weakened gates, and
  error handling that leaks data. Work statically and read-only. Do not exploit
  live systems. Use when `verifier` reviews a diff for security.
  Trigger: /review-security.
---

# /review-security

Judge the diff, not the codebase. Cite a file, line, diff hunk, or literal text
from the change in every finding. Treat a vulnerability as out of scope for
`blocking`/`important` when it predates the diff. Apply this rule only when the
diff does not touch, worsen, or newly expose it. Call it `advisory` at most.
State that it is pre-existing debt. Do not add findings to justify the run.

Work statically. Reason from the diff, its file, and named callers found by grep
or LSP references. Do not run code, send requests, or attempt exploitation. Do
not speculate about a theoretical attacker without a shown path.

Read-only. Never edit, write, commit, or mutate tracker state. Return
findings; do not fix them.

## Severity

Closed enum, matching the fleet's standing vocabulary. No free-text severity.

- **blocking** — ships a security regression. Secret leakage and any
  weakened gate are automatically `blocking`.
- **important** — a real defect with a plausible reachable path, not yet
  proven exploitable end-to-end.
- **advisory** — hardening, defense-in-depth, or pre-existing debt the diff
  touches but does not introduce or worsen.

`No blocking findings` is a valid, expected, complete result.

## Checks

Each check is enforceable with a failure example built from an obviously
fake value. Real credentials never appear in a finding or this file.

### 1. Secret leakage — always `blocking`

This workstation holds zero vendor credential bytes. The tailnet-only Mint
broker at `http://mint.tail5f5eb4.ts.net:4949` replaces valid markers in
request headers and relays upstream responses unchanged.
Mint does not authenticate or authorize callers.
Tailnet reachability and dedicated-host custody are the entire boundary.
Config carries only value-free `__mint.<alias>__` markers.
OpenRouter uses `__mint.openrouter.default__`.
These markers are not credentials.
Flag a literal credential in code, config, fixtures, tests, or logs.
Flag a local credential path that bypasses Mint for a credentialed vendor call.
Flag a resolved value echoed to stdout or an error.
A Mint marker can remain only when the provider contract names it.
Never replace the marker with a real key.

### 2. Authorization

Flag: a new route/handler/job/tool that reads or mutates with no authority
check reachable in the diff — e.g. `DELETE /projects/:id` calling
`db.delete(id)` with no `requireRole`/`can(user, ...)` anywhere nearby; a
check that runs after the mutation — e.g.
`await db.update(id, body); if (!isOwner(user, id)) throw ...`; a decision
keyed off client-supplied identity instead of a verified claim — e.g.
trusting `req.body.userId` or an `X-User-Id` header over the session.

### 3. Injection

Flag: untrusted input interpolated into a shell command — e.g.
``exec(`convert ${filename} out.png`)``; string-built SQL — e.g.
``query(`SELECT * FROM users WHERE email='${email}'`)`` instead of
parameterized; unescaped user content into HTML/a template — e.g.
`innerHTML = comment.body`; path construction from user input with no
traversal containment — e.g. `fs.readFile(path.join(baseDir, req.params.file))`
and no check the resolved path stays under `baseDir`; command construction by
string concatenation where an argv array was available — e.g.
`spawn("sh", ["-c", `git clone ${url}`])` instead of `spawn("git", ["clone", url])`.

### 4. Deserialization and parsing

Flag: untrusted bytes into a deserializer that can construct arbitrary
types — e.g. `pickle.loads(request.body)`, a network-fed
`ObjectInputStream`, a YAML loader in unsafe mode on request data; a parser
given unbounded input with no size cap — e.g. buffering a full request body
before checking `Content-Length`; no depth/recursion limit on nested
input — e.g. a JSON/XML parse call left at library-default expansion limits
on attacker-reachable input.

### 5. Blast radius

Flag any change widening what a credential, token, role, or process can reach.
Name the widening explicitly, from X to Y, instead of calling it "risky."
Flag a new Mint alias that has no operational need.
Flag a process or device that gains Mint reachability.
That access permits every loaded alias with any caller-selected HTTP(S) destination.
Flag a service account or database role with a broader verb or resource than
the diff needs.
Flag a provider credential with broader authority than the consumer needs.

### 6. Weakened gate — always `blocking`

Matches this repo's standing rule: a gate is never weakened to make a change
pass. Flag a check, assertion, validation, or approval boundary the diff
removes, loosens, or bypasses — e.g. deleting a signature-verification call,
downgrading `strict: true` to `strict: false` on auth middleware, widening
an allowlist to a wildcard, or commenting out a failing test/assertion
instead of fixing what it guarded.

### 7. Error handling as a leak

Flag error paths reachable by an untrusted caller when they surface internals.
Flag a stack trace or raw exception body in an HTTP response instead of a
generic error. Flag internal paths/hosts/env details in a user-facing error —
e.g.
`throw new Error(\`failed to read /etc/app/secrets.yaml\`)` propagated to the
client; raw query text echoed in a 500 body; identity leaked through error
asymmetry — e.g. a login endpoint returning a different error for "wrong
password" vs. "no such user."

## Non-goals

Out of scope for this lens: dependency/CVE scanning (a scanner's job, not a
reading agent's); compliance-framework checklists; threat-modeling the whole
system or its deployment topology; cryptographic algorithm review beyond
obvious misuse (e.g. MD5 for new password hashing, a hardcoded IV — not
choosing between AEAD schemes); speculative attack narratives with no
reachable path shown in this diff; formatting, import order, lint
violations — the linter's job.

## Output

Report findings against the seven checks with severity, file:line or hunk
citation, and the concrete failure. State "No blocking findings" when none
survive scrutiny — a complete, successful result, not a reason to keep
looking.
