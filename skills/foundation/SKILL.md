---
name: foundation
description: Inspect a project, install its agentic engineering baseline, and execute the locked next foundation.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Foundation

Build a tight engineering environment, then the next credible stage.

```text
inspect -> assess baseline -> profile -> recommend -> lock -> execute -> prove
```

## Stance

A control is a gate that fails fast on an invalid change and names the
repair. A tight control is fast, deterministic, and actionable. The baseline
is the set of applicable controls. Equivalent existing machinery satisfies a
control.

Product requirements decide what the system must do. The baseline decides how
narrowly, quickly, and reliably agents may change it. Absence of a product
feature is not a gap. A missing applicable control is, unless an equivalent
exists or a documented constraint prevents it.

Judge data structures and relationships first (Torvalds). Keep complexity
behind deep modules with errors defined out of existence (Ousterhout). Prefer
simple over easy; decomplect concerns and drop incidental complexity
(Hickey). Use one ubiquitous language across code, API, UI, and operations
(Evans). Keep important paths direct and inspectable (Carmack).

If a stable quality requirement can be encoded in architecture, types, tests,
tooling, CI, or release infrastructure, a prompt-only reminder is a missing
control.

## 1. Inspect

Default to the current repository unless the invocation names another target.
Keep one project boundary.

Before the lock, only repository reads, safe probes, and reversible runtime
observation.

Establish observed facts and unresolved questions:

- purpose, users, jobs, stage, distribution, success criteria, and current
  product truth;
- philosophy and domain model: concepts, data structures, relationships,
  authority, lifetimes, transitions, invariants, and names;
- architecture, interfaces, dependencies, and which faces serve real users;
- verification gates and undefended risks;
- onboarding, delivery, release, rollback, and operational needs;
- project-owned agent context.

Treat old documents and installed tools as evidence. Verify consequential
runtime claims. Settle facts with tools. Use `grilling` only for material
operator judgments about ambition, users, compatibility, burden, or tradeoffs.

Audit names as model claims. Separate current domain truth from historical
residue, synonyms, and overloaded terms. Recover the existing model with DDD
questions. Recommend only structures the model already requires.

Completion criterion: Every area above is evidenced, labeled as a hypothesis,
or recorded as an operator judgment. Consequential runtime claims are verified.

## 2. Assess baseline

Classify each applicable control as present, equivalent, missing, or a required
deviation:

- statically checked language and configuration;
- formatter and linter as errors;
- domain types and data constraints;
- deterministic tests through real contracts;
- one tight local check command;
- a deterministic local start path with sanitized fixtures or seed data for
  every runnable application;
- an executable smoke or acceptance path through the public interface;
- committed hooks: tight pre-commit, broader pre-push;
- CI as clean-room authority over the same owned commands;
- secret and dependency scanning;
- structured errors with release identity, for operated software;
- one documented clone-to-green path;
- project authority discoverable from `AGENTS.md`;
- protected default branch with merge protection on required checks;
- deployment from the merged immutable revision, with a health check and a
  rollback path.

Read [CONTROLS.md](CONTROLS.md) when a classification is uncertain, when
language, diagnosis, telemetry, or CI latency is in scope, or when a control
will be installed or proved.

Completion criterion: Every applicable control is classified. Each missing
control has a place in the recommendation. Each deviation has a reason.

## 3. Profile

Present:

```markdown
## Project profile
- Purpose and users:
- Stage, distribution, and next credible outcome:
- Philosophy and domain model:
- Current stack, architecture, and interfaces:
- Baseline posture:
- Verification, delivery, and operations:
- Strengths:
- Next pressure and measured bottlenecks:
- Constraints and invariants:
- Risks:
- Operator decisions:
```

Label hypotheses. Cite the paths, commands, URLs, or observations behind
consequential claims.

Completion criterion: Every profile field is filled. Claims that change the
recommendation are cited. Operator decisions are only the unresolved judgments.

## 4. Recommend

Recommend one coherent package:

```markdown
## Foundation recommendation

### Agentic engineering baseline
- Controls to install:
- Equivalents to keep:
- Required deviations:
- Proof:

### Product-shaped foundation
- Outcome:
- Build:
- Preserve:
- Omit, with reconsideration trigger:
- Maintenance, operating cost, and exit:
- Implementation slices:
- Proof:
- Non-goals:
```

Connect each baseline control to the failure it makes expensive or impossible.
Connect each product item to a project outcome. State maintenance and operating
cost. Product-shaped interfaces, infrastructure, process, and documentation
need a current job.

Completion criterion: Every missing baseline control is in the package or a
recorded deviation. Every product item has a job, cost, and proof. Every
omission has a reconsideration trigger.

## 5. Lock

Execution starts only after explicit operator agreement on:

```markdown
## Foundation lock
- Outcome:
- Baseline scope:
- Product scope:
- Non-goals:
- Slices:
- Acceptance and proof:
```

Audit, exploration, recommendation, silence, and partial approval are not a
lock. If the outcome changes, revise and lock again.

Completion criterion: The operator explicitly agreed to the lock template.

## 6. Execute

1. Track the accepted slices.
2. Implement the simplest coherent design.
3. Preserve current conventions and migrate every affected caller.
4. Verify each changed contract on its real boundary.
5. Keep work inside the lock.

Install accepted controls with [CONTROLS.md](CONTROLS.md). Mechanical baseline
work implied by the lock proceeds. A new vendor, language, paid service,
compatibility promise, or destructive change needs a revised lock.

Completion criterion: Accepted slices are implemented. Affected callers are
migrated. Each changed contract is verified on its real boundary.

## 7. Prove

Run the gates and real interfaces named by the lock. Each control in the lock
goes red on a synthetic defect, then the clean path passes. Use the
[CONTROLS.md](CONTROLS.md) probes. Distinguish declarations, deterministic
gates, live observations, and fresh judgment.

Close with:

```markdown
## Foundation result
- Outcome:
- Baseline installed:
- Implemented:
- Proof:
- Control-plane probes:
- Preserved:
- Residual risk:
- Reconsider when:
```

Completion criterion: Named gates and interfaces ran. Controls in the lock went
red on probes, then the clean path passed. The result template is complete.
