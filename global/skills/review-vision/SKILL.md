---
disable-model-invocation: true
name: review-vision
description: |
  Static critique lens for `verifier`: judge whether a change serves the
  product's written intent, never an unwritten one. Check a diff against
  `VISION.md`, a card's acceptance criteria, a stated goal, or an ADR for scope
  drift, silent scope reduction, non-goal violations, premise decay,
  obsolescence debt, and placeholder-as-completion.
  Use when a diff needs an intent/vision pass, not a correctness, security, or
  test-strength pass. Trigger: /review-vision.
---

# /review-vision

Judge a change against the product's *stated* intent. This lens can turn into
unsupported taste: a critic grades a diff against personal product opinions.
The rules below prevent that.

## Rule 1: authority first, always

Test every finding against one **written** artifact: root `VISION.md`, the
Powder card's Goal/acceptance criteria, a stated goal in the brief, or an ADR.
Look for these sources in that order. Form no opinion about the diff before that
search.

If none exist, or the available artifact says nothing relevant to this diff,
return exactly one `advisory` finding. State that intent is unstated. Name the
document that would settle it (usually "no `VISION.md`; create one via `/groom` (vision mode)"
or "card has no acceptance criteria"). Stop there. Do not infer intent and grade
the diff against that inference. An invented standard is not authority. A
finding based on it is fabricated, not discovered.

## Finding shape

Every finding is a table row with all five columns filled. A row missing the
quote or the path is not a finding — delete it.

```markdown
| Severity | Check | Authority (file:line, quoted) | What the change does | Violation |
| --- | --- | --- | --- | --- |
```

- **Authority** is a direct quote plus its path, e.g. `VISION.md:14 "ships as
  a single binary, no daemon"`. Paraphrase is not a quote.
- **What the change does** is observed from the diff, never assumed.
- **Violation** states the one-sentence contradiction between the two.

## Severity (closed enum)

- `blocking` — the change contradicts an explicit non-goal, or removes
  committed scope silently. Do not ship without a decision.
- `important` — the change drifts from stated scope, or leaves obsolescence
  debt a maintainer will find. Ship can proceed; name the gap.
- `advisory` — intent is unstated, or the drift is minor and cheap to note.
  Never blocks.

No other severity label is valid. Do not invent `nit`, `suggestion`, or
`critical`.

## Checks

Run each check only when the diff and an authority exist. Skip a check with
nothing to test. Do not create a finding.

1. **Scope drift** — the change does more than the accepted item, and the
   extra is unrequested. *Example:* card says "add rate limiting to the
   webhook endpoint"; diff also refactors the retry queue. The refactor is
   unrequested scope.
2. **Silent scope reduction** — the change does less than accepted, and the
   gap is nowhere in the diff, PR body, or card. More dangerous than drift
   because the gap has no note. *Example:* card requires "validates
   both HMAC and IP allowlist"; diff ships HMAC only, with no note anywhere
   that IP allowlisting was dropped.
3. **Stated-non-goal violation** — the change does something the authority
   explicitly excludes. *Example:* `VISION.md` states "non-goal: multi-tenant
   support"; diff adds a `tenant_id` column and per-tenant routing.
4. **Premise decay** — the change faithfully implements a stated intent, but
   evidence gathered in this run contradicts that intent. Report the
   contradiction as a finding. Do not quietly re-plan around it or hide it.
   *Example:* `VISION.md` says "reads finish under 50ms"; the diff
   correctly implements the documented cache-then-fetch design, but this
   run's benchmark shows 400ms under the documented design itself.
5. **Obsolescence debt** — the change adds a replacement but does not remove
   what it replaces. This repo treats erasure as part of every change. A
   surviving shim, feature flag, alias, dead test, or stale doc that the change
   made obsolete is a finding, even if nothing else is wrong.
   *Example:* diff adds `sendV2()` and every caller migrates to it, but
   `send()` and its now-unused test remain.
6. **Placeholder-as-completion** — a stub, mock, no-op, or `TODO: implement`
   is presented as delivered work against a card or goal that asked for the
   real behavior. *Example:* card asks for "retry with exponential backoff";
   diff adds a `retry()` function that calls the operation once and returns.

## Non-goals

- Rewriting `VISION.md` or proposing roadmap. Route that to `/groom`.
- Arguing strategy the operator already settled. Reopening an accepted
  decision is not this lens's job.
- Aesthetic opinion, naming preference, or architectural taste with no
  written authority behind it.
- Grading against an unwritten standard, however reasonable it seems. See
  Rule 1.
- Style, formatting, import order, and lint — the linter's job, not this
  lens's.

**Taste is not a finding.** Without a quoted file and line, you have an opinion,
not a finding. Remove it.

## Read-only

Never edit, write, commit, or mutate tracker state. You receive the diff and
the candidate authority documents, not the author's reasoning trail.

## Output

Return one of these results: a table of surviving findings, the single
`advisory` row from Rule 1, or an explicit **no blocking findings** line.
Use the explicit line when the change matches its written intent. Each result is
valid and complete. Do not add taste to an empty result.
