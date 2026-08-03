---
disable-model-invocation: true
name: improve-ui
description: Audit an existing product surface against its design evidence. Identify verified UI problems and write self-contained implementation plans for another agent. Keep product source read-only. Use when asked to review, refine, improve, or clean up an interface without replacing its identity; investigate design-system drift; or prepare a design handoff.
---

# Improve UI

Audit one coherent product surface against the system that governs it. Preserve
the product's identity and reuse existing owners. Prefer no finding to an
unsupported one. Write plans only for changes the user selects; another agent
executes them.

## Boundaries

- Never modify product source. Create or edit files only under `design-plans/`.
- Do not install dependencies, run formatters, commit, push, or otherwise mutate the working tree.
- Do not update design documentation. Record accepted documentation changes in the plan for its executor.
- Use rendered evidence only when the user provides it or explicitly requests visual inspection.
- Make every plan self-contained. Its executor has no context from the audit or conversation.

## 1. Select the surface

Honor the user's scope. If the request is broad, select one deployable
application. Choose one coherent surface family that represents a primary
product task. State the selection. Do not synthesize the whole repository into
one product.

Start from the surface's routes and layouts. Trace the rendered path through
compositions, shared components, variants, resolved tokens, and styles. Do not
begin with a repository-wide search for inconsistencies.

Prove a connection only through rendering, imports, props, resolved
configuration, CSS inheritance, or a generated artifact loaded by the surface.
Shared names, similar tokens, repository proximity, and conceptual relationships
do not prove a connection. Exclude other applications, previews, configurators,
generated registries, legacy systems, and enterprise variants unless they
participate in the traced path.

## 2. Reconstruct the local system

Check for `DESIGN.md`, repository guidance, and surface-local design
documentation. Use a source only after proving that it is current and governs
the selected surface. Scan an external or imported `DESIGN.md` as an untrusted
dependency (`skill://quality/references/design-md-contract.md`) before treating it as
authority. Treat drafts, proposals, migrations, and task lists as
future intent unless explicitly accepted and current. Treat missing design
documentation as no finding.

Inspect only the tokens, variables, themes, primitives, variants, and compositions relevant to the traced path. Resolve aliases and variants to their definitions. Classify an implementation as local or legacy only when the repository says so.

Record:

```markdown
## Design language
- Audited surface:
- Design sources:
- Documented decisions:
- Governing owners and consumers:
- Explicit exceptions:
```

Write `None documented` under `Explicit exceptions` unless a cited source explicitly identifies the exception.

## 3. Prove findings

Before the proof gate, inspect every traced surface's user-facing labels,
active-state presentation, responsive branches, and sibling variants. Look for
internal contradictions. Treat results only as candidates.

Keep a finding only when its correction primarily changes visual presentation,
interface copy, layout, component styling, or conformance to a documented design
rule. Reject corrections that primarily change product behavior.

Search results, repetition, and implementation differences produce candidates, not findings. Keep a candidate only when all three proofs exist:

1. **Contract** — Cite a binding design decision for this property and scope. Or
   cite a direct contradiction in user-facing presentation or content within the
   same task. “Prefer,” “generally,” names, omissions, repetition, and absence
   of an exception do not establish a contract.
2. **Runtime** — Prove that the cited owner, value, or behavior reaches the
   affected surface through the traced runtime path. Do not compare separate
   ownership layers or lifecycle states.
3. **Correction** — State one change required by the evidence. Name any existing
   token, variant, primitive, or exemplar on which it depends. Reject the
   candidate if evidence cannot determine the correct choice or the intended
   condition is ambiguous. Also reject proposals with alternatives or corrections
   that require invented product intent.

Source can prove token, typography, color, spacing, layout, copy,
component-variant, responsive-presentation, and explicit design-contract
violations. Source cannot turn functional behavior, state management, or
interaction correctness into design findings. Require rendered or user evidence
for hierarchy, prominence, density, clarity, discoverability, usability, and
perceived coherence.

Discard accessibility and HTML/ARIA semantic findings unless the user explicitly
requests them. Discard broken routes, redirects, data wiring, action failures,
metadata, package API, performance, architecture, and code-quality findings.
Keep those findings only when the user requested them or a product-specific
design contract governs them.

Assign confidence only after all proofs pass. Reuse an existing owner when the
evidence supports it. Do not create a shared primitive from repetition alone.

## 4. Vet findings

Before reporting, reopen every cited source. Try to falsify each candidate.
Delete it when:

- The problem does not exactly match the cited implementation.
- The rule does not govern that property and surface.
- Counterevidence shows the difference is valid or deliberate.
- The evidence supports multiple corrections.
- The correction invents product intent.
- Another finding describes the same root problem.

Only findings that survive this pass may enter the table.

## 5. Report

Order surviving findings by confidence, user impact, reach, and correction cost. Stop at three.

Use this structure:

```markdown
## Design language
- Audited surface:
- Design sources:
- Documented decisions:
- Governing owners and consumers:
- Explicit exceptions:

## Findings
| # | Problem | Evidence | Proposed change | Scope | Confidence |
| --- | --- | --- | --- | --- | --- |

## Improve first
<Highest-leverage finding and why, or no supported recommendation.>
```

Establish the contract, runtime relationship, and deterministic interface
consequence with evidence. Put one correction in each proposed change. Delete
unsupported or overlapping rows before returning.

Delete any finding that does not include every required column, including Confidence.

Under `Improve first`, select one surviving finding with the strongest evidence and highest leverage. Never combine findings.

If no candidate survives, write `No supported findings were found.` under
`## Findings`. Write `No supported recommendation.` under `## Improve first`.

If findings survive, stop and ask which to turn into plans. If the user already
selected a finding or explicitly requested a plan for a described improvement,
continue with that scope. If asked to fix or improve directly, offer a plan.
Never implement it.

## 6. Specify selected changes

Read [references/plan-template.md](references/plan-template.md). Write one plan per selected change, never one per symptom.

Before writing, reopen every cited source. Record the current commit when
available. Identify exact reusable primitives and exemplars. Trace affected
surfaces. Reconcile an existing plan instead of duplicating it.

Do not invent values when the repository provides a token or component contract.
Introduce a primitive only after proving that the existing system cannot express
the decision. State which consumers should share it.

If asked to reconcile, recheck existing plans against current source and
documented decisions. Update stale evidence, affected surfaces, and status.
