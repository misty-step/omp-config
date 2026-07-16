# Project profile contract

Load this reference when adopting or auditing `/project-engineering`. The
profile is a repo-specific applicability map, not a universal scaffold.

## Classification

Start from live evidence: root instructions, manifests, shipped surfaces,
workflows, deploy configuration, public routes, data stores, model seams, and
existing evidence directories. Classify the project kind in its own vocabulary
(for example runtime application, library, CLI, model workload, website, or
support repository). Mixed projects may name multiple kinds.

Complete every identity field. For every obligation row choose exactly one
state:

- `applicable` — name the command, path, service, durable evidence location, or
  gap card that owns it.
- `not-applicable` — give a short project-specific reason. Absence is not a
  reason.
- `waived` — add owner, reason, current evidence, review date, and expiry.

Do not create guessed commands or placeholder paths to make the profile look
complete. A truthful `gap: <durable pointer>` is conformant declaration; an
unrecorded or chat-only gap is not.

Place the populated profile with the repo's existing governance or engineering
policy files. If no convention exists, return the filled artifact with a
recommended repo-local path and record that location decision as a declaration
gap. The fleet contract does not reserve a filename or root directory.

## Fitness function

### Gates

Declare the repo-owned fast and full commands. `/ci` owns their design. The
fast gate should fit normal edit cycles; the full gate must retain every
required invariant before merge, release, or deploy. Record the evidence
location emitted by each command.

Coverage declares all three parts of the target:

- changed-line threshold or ratchet;
- non-regression threshold or baseline policy;
- mutation command, threshold, and survivor report.

Project-specific values live in the profile or its named policy. Do not infer
quality from a global coverage percentage.

Supply-chain applicability names the owning policy and evidence for dependency
locking, vulnerability/license review, provenance/SBOM, artifact integrity,
and secret scanning. The profile points; the gate implements.

### Architecture

Declare the architecture-policy path and allowed dependency directions. Audit
the policy against the live module graph.

Deep-module quality needs fresh judgment at material seams: inspect interface
complexity, hidden invariants, locality, adapter reality, and whether deletion
would spread complexity back into callers. Fitness proxies may flag review
targets—dependency cycles, public-surface growth, fan-out, duplicated policy,
or changed interface size—but no proxy or composite score proves depth.

### Tests and live proof

Declare unit, integration, and end-to-end applicability separately. Each
applicable tier points to its driver and evidence. `/qa` and
`verification-system-first.md` own the proof design.

Internal collaborators run for real. Replace only external boundaries:

- emulator for a supported third-party API;
- container for an external service or datastore;
- contract fake for a boundary whose protocol can be checked independently.

A test made convenient by mocking an internal module is an architecture smell,
not integration evidence.

### Capability and judgment

Use `/eval-design` only when a named decision is informed by fresh model or
agent output scored by a grader. Linters, fixed-artifact checks, historical
KPIs, coverage, and mutation are gates or instrumentation.

Irreducible architecture or product judgment names a fresh artifact-only
critic and the reviewed artifact. Keep it distinct from a capability eval.
Add one row for each capability decision or judgment seam. If the repository
has neither, retain one `not-applicable` row with a project-specific reason;
do not leave the table ambiguous or invent a seam.

### Factory and operational obligations

Declare:

- Canary mode (`http`, `check-in`, `errors-only`, or `not-applicable`) and live
  service identity;
- work-ledger provider and project identity for durable work; the Misty Step
  profile binds Powder, while another machine profile may bind Linear or an
  equivalent provider without changing the project obligations;
- Landmark/release mode and its manifest, workflow, or explicit deferral;
- performance, accessibility, backup/restore, and data lifecycle obligations,
  each with applicability and proof pointer.

`/factory-apps` owns Canary, Powder, and Landmark method for the Misty Step
profile. A different provider binding must still prove queryable durable work
state; renaming chat or TODO prose as a ledger does not satisfy the contract. The application floor
applies only when the project is an application; classify other project kinds
rather than silently projecting application layout onto them.

## Audit output

Return:

1. Project kind and profile path.
2. Verified pointers and exact commands/probes exercised.
3. Gaps grouped by declaration, deterministic gate, live probe, capability
   eval, and fresh judgment.
4. Stale or incomplete waivers, including days to expiry.
5. The smallest owner-routed remediation for each gap.

Severity follows evidence loss: an applicable obligation with no declaration
is high; a declaration whose gate or live evidence is absent is high; stale
evidence or an expiring waiver is medium unless the underlying risk raises it.
Do not report the project conformant while an applicable high gap remains.
