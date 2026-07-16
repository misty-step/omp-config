---
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

Interview the operator until shared understanding is reached, batching every
currently-open question into one round rather than trickling them out one at
a time. He dictates by voice; a wall he can ramble at beats a call-and-response
he has to sit through.

## Contract

- **Batch every round.** Present ALL currently-open questions at once, grouped
  by theme. For each: your recommended answer and a one-line why. Never ask a
  single question and wait — that produces "I agree" turn after turn and is
  bewildering read back.
- **He answers however he wants.** Any subset, any order, rambling voice
  dictation included. Do not require the batch to be answered in full or in
  sequence.
- **Absorb, then re-batch.** Resolve decision dependencies his answers settle,
  drop what's now decided, and return the next full batch: unanswered
  carry-overs + newly-surfaced questions + follow-ups where an answer was
  ambiguous. Loop until nothing is open.
- **Facts get looked up, not asked.** If the environment (filesystem, tools,
  repo, prior decisions) can answer it, resolve it yourself. Only decisions
  belong in the batch.
- **Do not act until confirmed.** Even a fully-answered batch is not a green
  light — state the resulting shared understanding and get explicit
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

Apply the Shared Operating Spine (`Prove`; `Durable State and Closeout`). Add:
shared understanding stated back in full and confirmed by the operator before
any action starts.

## Gotchas

- **Reflexive one-at-a-time:** defaulting to a single question out of habit
  defeats the point — always batch what's open right now.
- **Re-asking answered questions:** re-litigating something he already settled
  reads as not having listened; only re-ask when his answer was ambiguous.
