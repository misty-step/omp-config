# ADR 0006: Consolidate quality programs

- Status: Accepted
- Date: 2026-08-01

## Context

Seven hand-invoked skills repeat one audit, assessment, remediation, and verification loop:

- `audit-quality-controls`
- `quality-toolchain`
- `quality-tests`
- `quality-operations`
- `audit-architecture`
- `audit-product`
- `design-audit`

Their domain rules differ, but their control flow does not. The repeated skill surfaces duplicate routing, decisions, evidence rules, and completion gates. Their assessment paths and decision vocabularies also diverge.

`deliver-core` and `research-core` expose package seams inside one repository. OMP is their only proven consumer. ADR 0001 keeps first-party primitives local until two active harnesses repeatedly diverge.

Matt Pocock's `writing-great-skills` guidance makes predictability the root virtue. It requires one source for each meaning, branch-specific progressive disclosure, checkable completion criteria, and aggressive removal of duplication and no-op prose.

## Decision

Create one hand-invoked `quality` program. Its interface is:

```text
/quality <controls|toolchain|tests|operations|architecture|product|design>
         [--audit-only|--remediate|--verify|--trends] [target]
```

The main skill owns the shared program and completion criteria. It loads only the selected domain reference. Domain references own unique targets, probes, evidence, and safety rules.

Use one assessment contract at `.evidence/quality/<domain>/assessment.json` and `assessment.md`. Operations may add versioned run, baseline, and trend artifacts below `.evidence/quality/operations/`.

Keep `ci`, `review-tests`, `review-security`, `review-vision`, `verify-live`, and `qa-users` as focused leaf methods. They do not own the complete quality program.

Merge the neutral delivery and research contracts into `deliver` and `research`. Remove the two `-core` directories. Keep OMP routing in clearly named sections inside each parent skill.

Use a clean cutover. Delete all seven old quality program directories and both `-core` directories. Do not leave aliases, compatibility routes, or copied assessment contracts.

## Consequences

One skill name exposes the quality program. Seven domain references keep branch-only context out of the main skill. One assessment schema governs decisions and verification.

Existing evidence under old paths remains historical evidence. New runs use `.evidence/quality/<domain>/` only.

The main skill becomes a router. A domain may split again only when it gains a distinct invocation contract or hidden sequence that prevents premature completion.

## Reversal condition

Split a domain when a shaped eval proves that the unified program causes wrong routing, missed domain rules, or premature completion. Do not split only because a reference is long.
