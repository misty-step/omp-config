---
name: foundation
description: Inspect a project's current reality, agree on its next foundation, then execute the locked scope.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Foundation

```text
inspect -> profile -> recommend -> lock -> execute -> prove
```

Before the lock, use only repository reads, safe probes, and reversible runtime
observation. Do not mutate the project.

## Inspect

Keep one project boundary. Establish:

- purpose, users, stage, distribution, and success criteria;
- domain ownership, state, interfaces, dependencies, and constraints;
- verification gates and undefended risks;
- onboarding, delivery, release, rollback, and operational needs.

Absence is not a gap without a product need. Treat old documents and installed
tools as evidence, not authority. Verify consequential runtime claims.

Settle facts with tools. Use `grill-me` only for material operator judgments
about ambition, users, compatibility, burden, or tradeoffs.

## Profile

Present:

```markdown
## Project profile
- Purpose and users:
- Stage and distribution:
- Strengths:
- Next pressure:
- Constraints:
- Risks:
- Operator decisions:
```

Label hypotheses. Cite the paths, commands, URLs, or observations behind
consequential claims.

## Recommend

Recommend one coherent package:

```markdown
## Foundation recommendation
- Outcome:
- Build:
- Preserve:
- Omit, with reconsideration trigger:
- Implementation slices:
- Proof:
- Non-goals:
```

Connect each item to evidence and a project outcome. State maintenance and
operating cost. Exclude interfaces, infrastructure, process, and documentation
that have no current job.

## Lock

Execution requires explicit operator agreement on:

```markdown
## Foundation lock
- Outcome:
- Scope:
- Non-goals:
- Slices:
- Acceptance and proof:
```

Audit, exploration, recommendation, silence, and partial approval are not a
lock. If the outcome changes, revise and lock again.

## Execute

1. Track the accepted slices.
2. Implement the simplest coherent design.
3. Preserve current conventions and migrate every affected caller.
4. Verify each changed contract on its real boundary.
5. Keep work inside the lock.

New product, architecture, compatibility, operating-cost, or destructive scope
requires a revised lock. Mechanical work implied by the accepted outcome does
not.

## Prove

Run the gates and real interfaces named by the lock. Close with:

```markdown
## Foundation result
- Outcome:
- Implemented:
- Proof:
- Preserved:
- Residual risk:
- Reconsider when:
```
