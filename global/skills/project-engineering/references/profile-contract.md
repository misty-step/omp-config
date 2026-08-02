# Project profile contract

Load this reference when you adopt or audit `/project-engineering`. The profile
maps repo-specific applicability; it is not a universal scaffold.

## Classification

Start with live evidence: root instructions, manifests, shipped surfaces,
workflows, deploy configuration, public routes, data stores, model seams, and
existing evidence directories. Classify the project kind in its own vocabulary,
such as runtime application, library, CLI, model workload, website, or support
repository. Mixed projects may name multiple kinds.

Complete every identity field. Choose exactly one state for every obligation row:

- `applicable` — name the command, path, service, durable evidence location, or
  gap card that owns it.
- `not-applicable` — give a short project-specific reason. Absence is not a
  reason.
- `waived` — add owner, reason, current evidence, review date, and expiry.

Do not create guessed commands or placeholder paths to make the profile look
complete. A truthful `gap: <durable pointer>` is conformant declaration. An
unrecorded or chat-only gap is not.

Place the populated profile with the repo's existing governance or engineering
policy files. If no convention exists, return the filled artifact with a
recommended repo-local path. Record that location decision as a declaration
gap. The fleet contract does not reserve a filename or root directory.


## Fitness function

### Gates

Declare the repo-owned fast and full commands. `/ci` owns their design. Make
the fast gate fit normal edit cycles. Keep every required invariant in the full
gate before merge, release, or deploy. Record the evidence location that each
command emits.

Declare all three parts of the coverage target:

- changed-line threshold or ratchet;
- non-regression threshold or baseline policy;
- mutation command, threshold, and survivor report.

Keep project-specific values in the profile or its named policy. Do not infer
quality from a global coverage percentage.

For supply-chain applicability, name the owning policy and evidence for
dependency locking, vulnerability/license review, provenance/SBOM, artifact
integrity, and secret scanning. The profile points. The gate implements.

### Architecture

Declare the architecture-policy path and allowed dependency directions. Audit the
policy against the live module graph.

Use fresh judgment at material seams to assess deep-module quality. Inspect
interface complexity, hidden invariants, locality, adapter reality, and whether
deletion would spread complexity back into callers. Fitness proxies may flag
review targets: dependency cycles, public-surface growth, fan-out, duplicated
policy, or changed interface size. No proxy or composite score proves depth.

### Tests and live proof

Declare unit, integration, and end-to-end applicability separately. Point each
applicable tier to its driver and evidence. `verifier` with `verify-live` and
`verification-system-first.md` own proof design.

Run internal collaborators for real. Replace only external boundaries:

- emulator for a supported third-party API;
- container for an external service or datastore;
- contract fake for a boundary whose protocol can be checked independently.

Treat a test that mocks an internal module for convenience as an architecture
smell, not integration evidence.

### Capability and judgment

Use `/eval-design` only when a named decision uses fresh model or agent output
scored by a grader. Treat linters, fixed-artifact checks, historical KPIs,
coverage, and mutation as gates or instrumentation.

For irreducible architecture or product judgment, name a fresh artifact-only
critic and the reviewed artifact. Keep this distinct from a capability eval.
Add one row for each capability decision or judgment seam. If the repository
has neither, keep one `not-applicable` row with a project-specific reason.
Do not leave the table ambiguous or invent a seam.

### Factory and operational obligations

Declare:

- Canary mode (`http`, `check-in`, `errors-only`, or `not-applicable`) and live
  service identity;
- work-ledger provider and project identity for durable work. The Misty Step
  profile binds Powder. Another machine profile may bind Linear or an
  equivalent provider without changing project obligations;
- Landmark/release mode and its manifest, workflow, or explicit deferral;
- performance, accessibility, backup/restore, and data lifecycle obligations,
  each with applicability and proof pointer.

`/factory-apps` owns the Canary, Powder, and Landmark method for the Misty Step
profile. A different provider binding must still prove queryable durable work
state. Renaming chat or TODO prose as a ledger does not satisfy the contract.
Apply the application floor only when the project is an application. Classify
other project kinds instead of silently projecting application layout onto them.

## Audit output

Return:

1. Project kind and profile path.
2. Verified pointers and exact commands/probes exercised.
3. Gaps grouped by declaration, deterministic gate, live probe, capability
   eval, and fresh judgment.
4. Stale or incomplete waivers, including days to expiry.
5. The smallest owner-routed remediation for each gap.

Set severity by evidence loss. Mark an applicable obligation without a
declaration high. Mark a declaration without gate or live evidence high. Mark
stale evidence or an expiring waiver medium unless the underlying risk raises
it. Do not report the project as conformant while an applicable high gap remains.
