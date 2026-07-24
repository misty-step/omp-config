---
disable-model-invocation: true
name: review-security
description: |
  Security lens for code-critic: read a diff and find security defects
  provable from the change itself — secret leakage, missing or reordered
  authorization, injection, unsafe deserialization, blast-radius growth,
  weakened gates, and leaky error handling. Static, read-only, no live
  exploitation. Use when code-critic is dispatched with the security lens
  on a diff. Trigger: /review-security.
---

# /review-security

Judge the diff, not the codebase. Every finding cites a file, a line, a diff
hunk, or literal text from the change under review. A vulnerability that
predates the diff and the diff does not touch, worsen, or newly expose is out
of scope for `blocking`/`important` — call it `advisory` at most and say it
is pre-existing debt. Do not pad the packet to justify the run.

Static only: reason from the diff, its file, and named callers found by grep
or LSP references. No running code, no requests, no exploitation attempts,
no speculation about a theoretical attacker with no shown path.

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

This workstation holds zero vendor credential bytes (`global/MINT.md`).
Credentialed calls route through the mint broker; config carries a
placeholder shaped `__mint.<service>.<name>__` and the broker resolves it
host-side after the request leaves the agent. Anything else key-shaped in
the diff is a mint-bypass bug.

Flag: a literal credential in code/config/fixtures/tests/logs — e.g.
`apiKey: "sk-live-4f9a..."` where the diff should carry
`apiKey: "__mint.openrouter.default__"`; a placeholder replaced by a literal
mid-diff — e.g. `Authorization: __mint.stripe.default__` changed to
`Authorization: Bearer rk_live_abc123`; a secret or resolved value echoed to
stdout or an error — e.g. `console.log("using key", apiKey)`.

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

Flag any change widening what a credential, token, role, or process can
reach, and name the widening explicitly (from X to Y), not "this could be
risky": a mint policy route broadened from a narrow path to a wildcard —
e.g. `require_placeholder` scope narrowed from
`/proxy/https/api.stripe.com/v1/charges` to `/proxy/https/api.stripe.com/*`;
a service account or DB role granted a broader verb/resource than the diff's
purpose needs — e.g. a read-only reporting job now runs with `db.write`; a
process boundary removed — e.g. a sandboxed worker gains a raw shell or
outbound network access it didn't have.

### 6. Weakened gate — always `blocking`

Matches this repo's standing rule: a gate is never weakened to make a change
pass. Flag a check, assertion, validation, or approval boundary the diff
removes, loosens, or bypasses — e.g. deleting a signature-verification call,
downgrading `strict: true` to `strict: false` on auth middleware, widening
an allowlist to a wildcard, or commenting out a failing test/assertion
instead of fixing what it guarded.

### 7. Error handling as a leak

Flag error paths reachable by an untrusted caller that surface internals: a
stack trace or raw exception body in an HTTP response instead of a generic
error; internal paths/hosts/env details in a user-facing error — e.g.
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
