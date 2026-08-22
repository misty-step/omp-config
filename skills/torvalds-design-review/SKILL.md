---
name: torvalds-design-review
description: Ask a Torvalds-style first-principles critic whether a system should be designed this way.
disable-model-invocation: true
argument-hint: "[system, design, or solution]"
---

# Torvalds Design Review

Evaluate one system or solution through a blunt first-principles design review.
This is a read-only judgment pass. It does not redesign or edit the target in
the primary session.

## 1. Bound the target

Use the invocation argument. If it names no target, use the system or proposal
immediately preceding the invocation. Record:

- the concrete problem and representative workload;
- the current or proposed design;
- binding invariants and constraints;
- primary evidence: source paths, decisions, protocols, measurements, or
  production observations;
- the decision the operator needs from this review.

Inspect available evidence before dispatch. Distinguish facts from assumptions.
Ask only when several materially different targets remain after reading the
available context.

Completion criterion: one target brief accounts for the problem, design,
constraints, evidence, and decision.

## 2. Dispatch the critic

Dispatch exactly one `torvalds-reviewer` subagent. It is the read-only
high-effort route; do not substitute `task`, `scout`, or the primary model.
Subagents start blank, so send the complete target brief and evidence
locations.

Use this as the subagent's complete task. Replace placeholders only; keep the
three headings and acceptance criteria unchanged.

```text
# Target
Evaluate <system or solution>. Read <evidence locations>.

# Change
Perform a read-only design judgment. If Linus Torvalds were designing this
today from scratch, from first principles, would he design it this way? If
not, what would be fundamentally different?

# Acceptance
Use the Torvalds lens in your agent instructions. Treat this brief as ground
truth: <problem, workload, design, invariants, constraints, facts, assumptions,
and operator decision>. Account for every supplied constraint and material
design concept. Return a decisive, operator-facing report. Skip validation
commands.
```

When the target brief is large, place it in `local://torvalds-review-brief.md`
and send that URI instead of truncating it.

Wait for completion, then ask that same agent to render its complete
operator-facing report. Use that reply as the judgment source. If the subagent
fails, report the failure; the primary does not replace the independent
judgment with its own review.

Completion criterion: the `torvalds-reviewer` returns its complete report.

## 3. Ground the verdict

Check every evidence-backed claim against the supplied primary records. Label
unsupported claims. Preserve the critic's core verdict while making these
distinctions explicit:

- greenfield design quality;
- constraints that justify divergence today;
- unknowns that could reverse the verdict.

A later implementation request must settle material human-owned tradeoffs
before edits.

Completion criterion: every factual claim is grounded or labeled, and the
verdict still answers the operator's question.

## 4. Deliver

Return one evidence-grounded report. Lead with the direct answer to whether the
system would be designed this way from scratch. End with the first reversible
change, or state that no change survived review.

Completion criterion: the operator receives one decisive, evidence-grounded
comparison of the current design, greenfield design, and migration reality.