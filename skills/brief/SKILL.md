---
name: brief
description: Give an evidence-only executive brief with explicit unknowns and decidable calls.
disable-model-invocation: true
argument-hint: "[session, project, or decision]"
---

# Brief

Give the operator the facts, gaps, calls, and next move. Do not supply missing
context from inference.

## 1. Set the boundary

Name the subject, decision, and time boundary. Use the invocation argument. If
the argument is absent, use the active session only.

Do not combine projects, repositories, environments, or releases without an
explicit request.

Completion criterion: One subject, decision, and as-of time or interval are
explicit.

## 2. Collect evidence

Read only sources that can answer the brief:

- session records own work performed, proof captured, and blockers observed in
  this session;
- repository records own branch, source changes, and accepted code decisions;
- the trusted ledger owns work priority, readiness, claims, and blocked status;
- the real runtime owns deployed identity, state, and health.

A branch does not prove a deployment. A ticket does not prove product
behavior. A log does not prove stored state. When authorities conflict, record
the conflict as `Unknown` until the owning source resolves it.

For each decision-relevant fact, record the source read now. If a source is
absent, unreachable, stale, or silent, write `Unknown`. State the missing
source and why the gap matters. Do not convert absence into a fact.

Completion criterion: Every applicable authority was queried. Every
decision-relevant fact is included with current evidence, an authority
conflict, or an explicit `Unknown`.

## 3. Find the calls

A call needs operator judgment about outcome, scope, compatibility, cost,
burden, risk, or an irreversible action. Reversible actions are next moves, not
calls.

For each call, state:

- the question;
- live options;
- your recommendation;
- evidence for the recommendation;
- cost of waiting;
- what becomes unblocked.

Do not ask the operator to decide an implementation detail that tools, code, or
an accepted spec can settle.

Completion criterion: Every open call is decidable from the listed evidence.

## 4. Write in ASD-STE100 style

Apply these rules to every sentence:

- Use active voice.
- Use one term for one concept.
- Use one meaning for each word.
- Put one instruction or main idea in each sentence.
- Keep procedural sentences at 20 words or fewer.
- Keep descriptive sentences at 25 words or fewer.
- Use simple present tense when possible.
- Name the actor. Avoid unclear pronouns.
- Define an abbreviation at first use.
- Avoid idioms, contractions, rhetorical questions, and decorative language.
- Break long conditions and lists into vertical steps.

Use exact quotations and domain terms when replacement reduces accuracy. Apply
the remaining sentence rules to all surrounding text. Do not claim formal
ASD-STE100 conformance.

Completion criterion: Every unaffected word and sentence follows every
applicable rule. Only the exact required quotation or domain term is exempt.

## 5. Deliver

Use this shape:

```markdown
# Bottom line
<State the as-of time. Then give two to four short conclusion-first sentences.>

## Known
- Fact: <fact>
  Source: <record read now>

## Unknown
- Gap: <missing fact>
  Missing source: <source>
  Decision effect: <effect>

## Calls
### <call>
- Options:
- Recommendation:
- Evidence:
- Cost of waiting:
- Unblocks:

## Next
- <highest-value authorized action>
```

Omit `Unknown` or `Calls` only when empty. Keep `Known` to the facts that
support the conclusion or a call. Do not narrate the research process. Do not
implement or groom work.

Completion criterion: Every applicable authority is accounted for. Every
`Known` item has a current source. Every unavailable fact is in `Unknown`.
Every call field is complete. Every next action has authorization in evidence.
