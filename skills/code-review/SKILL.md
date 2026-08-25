---
name: code-review
description: Dispatch an exhaustive multi-model Council of Subagents to review a pull request, branch, or commit, repair supported defects, and verify until green.
disable-model-invocation: true
argument-hint: "[pull request, branch, or commit]"
---

# Code Review

Exhaustive multi-angle review phase. The top-level agent acts as Master
Reviewer, dispatching a Council of Subagents across diverse model families
(Structure, Behavior, Practicality), adjudicating findings, and driving the
repair loop until tight.

```text
resolve target -> establish intent -> load council -> dispatch multi-model scouts
-> adjudicate findings -> repair loop -> emit report
```

## 1. Resolve the target

Use the named pull request, branch, or commit. For a pull request, create a
dedicated checkout or worktree. For a commit, create an isolated repair branch
and worktree from that commit. Default to the current change only when no
target is supplied.

Record the base, head, diff, and writable checkout before review. Leave the
operator's active branch unchanged.

Completion criterion: One exact target and isolated repair destination exist.

## 2. Establish intent

Reconstruct the accepted intent from the request, accepted decisions,
repository authority, and runtime evidence:

- outcome and user value;
- data, owners, lifetimes, states, transitions, and invariants;
- interfaces, callers, operators, and compatibility;
- intentional changes, removals, non-goals, and unchanged behavior;
- tests, QA scenarios, production signals, and rollback;
- proof that separates success from a plausible regression.
- for a pull request with observable claims, reviewer-open evidence attachments
  and an attached packet record, not local paths or hashes alone;

A concern that conflicts with accepted intent is a design question, not a
repair.

Completion criterion: Intent, invariants, scope, and proof are explicit.

## 3. Load council and repair protocol

Run `omp config path`. Read `references/review/COUNCIL.md` and
`references/review/REPAIR-LOOP.md` below that agent directory, along with the
selected lens files.

Completion criterion: Council contracts and selected lens references are
loaded from the deployed reference source.

## 4. Dispatch the Council of Subagents

Act as Master Reviewer. Fan out parallel read-only scouts across distinct
model roles per `references/review/COUNCIL.md`:

1. **Structure Scout (`@slow` / GPT-5.6 Sol Max):** Evaluates data ownership,
   invalid states, module depth, and decomplection (`torvalds.md`,
   `ousterhout.md`, `hickey.md`, `taelin.md`).
2. **Behavior Scout (Claude Fable 5 / Opus):** Evaluates correctness,
   behavioral contracts, error states, and test defense (`uncle-bob.md`,
   `kcd.md`).
3. **Practicality Scout (Grok 4.6 / Gemini Flash):** Evaluates hot path
   inspectability, mechanical sympathy, YAGNI, and dead seams (`carmack.md`,
   `thermo.md`, `ponytail.md`).
4. **Adversarial Security Pass:** When auth, secrets, untrusted inputs, or trust
   boundaries are modified, stop and ask the operator to invoke
   `/security-review`, then resume from its triaged findings.
Adjudicate and deduplicate all scout findings into **Blocker**, **Take**, or
**Drop**.

Completion criterion: Every dispatched scout returns, and all findings are
classified with explicit rationale.

## 5. Repair loop

Execute the repair and convergence protocol defined in
`references/review/REPAIR-LOOP.md`:

- repair in-scope Blockers and Takes autonomously;
- delete first, fix source directly, and migrate all callers;
- re-verify affected tests and product-surface QA after each repair;
- repeat until zero in-scope Blockers or Takes remain.

Completion criterion: The repair loop terminates green with all checks passing,
evidence matching the final state, and required PR evidence attachments opening
from the rendered pull request.

## 6. Report

Write the final review report to an OS temporary path:

```markdown
# Code review
## Target, intent, and scope
## Council roster and multi-model dispatch
## Findings (Blockers, Takes, Drops)
## Cycles and repairs applied
## Final verdict
## Proof and residual risk
```

Return the report path and lead with its final verdict.

Completion criterion: The final verdict is green or blocked with an explicit
reason, and no supported finding remains unaddressed.
