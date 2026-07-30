---
disable-model-invocation: true
name: grilling
description: |
  Grill the operator relentlessly about a plan, decision, or idea by batching
  every open question into one round instead of asking one at a time.
  Use when: the operator wants to stress-test their thinking, or uses any
  'grill' trigger phrases.
  Trigger: /grill, /grilling.
argument-hint: "[plan|decision|idea]"
---

# /grill

Interview the operator until you reach shared understanding. Batch every open
question into one round instead of asking questions one at a time. The operator
dictates by voice. Let the operator speak freely instead of requiring
call-and-response.

## Contract

- **Batch every round.** Present ALL currently-open questions at once. Group them
  by theme. Give a recommended answer and a one-line reason for each. Never ask
  one question and wait. That pattern creates repeated "I agree" turns and
  confusing readback.
- **The operator answers freely.** The operator may answer in any subset or order,
  including rambling voice dictation. Do not require a full or sequential answer.
- **Absorb, then re-batch.** Resolve decision dependencies that the answers
  settle. Drop decided questions. Return the next full batch with unanswered
  carry-overs, new questions, and follow-ups for ambiguous answers. Repeat until
  no question remains open.
- **Look up facts, not decisions.** If the filesystem, tools, repository, or prior
  decisions can answer a fact, resolve it yourself. Put only decisions in the
  batch.
- **Do not act before confirmation.** A fully answered batch is not approval to
  act. State the resulting shared understanding in full. Get explicit
  confirmation before acting on it.

## Batch format

```markdown
## Round <n>

### <Theme>
1. <question> — recommend: <answer> (<one-line why>)
2. <question> — recommend: <answer> (<one-line why>)

### <Theme>
3. ...
```

## Completion Gate

Apply the Shared Operating Spine (`Prove`; `Durable State and Closeout`). Add
shared understanding stated in full and confirmed by the operator before any
action starts.

## Gotchas

- **Reflexive one-at-a-time:** A single-question default defeats this skill. Always
  batch all questions that are open now.
- **Re-asking answered questions:** Asking a settled question again shows that you
  did not listen. Ask again only when the answer was ambiguous.
