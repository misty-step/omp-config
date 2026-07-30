# Interrogate-First Lens

Use before shaping a contestable idea or framing a strategic groom.
Treat this as an interview, not a questionnaire.
Guide the operator through the decision tree until hidden choices are visible and resolved.
`/shape`'s grill step loads this reference as its primary stance.
`global/skills/grilling/SKILL.md` is the invocable relative. Its `"grill me"` trigger phrases invoke it directly.
It shares this lens's batching doctrine instead of duplicating it.
(2026-07-15 batching update: Revoke one-question-at-a-time everywhere, not only in grilling.)
The operator dictates and wants all questions at once, not call-and-response.

1. **Batch every round.** Present all currently open questions at once.
   Group them by theme. Give a recommended answer and one-line reason for each.
   The operator may answer any subset in any order, including partial dictation.
   Absorb answers and resolve the decisions they settle.
   Return the next full batch with unanswered questions, new questions, and follow-ups for ambiguous answers.
   Repeat until no question remains.
   A single awaited question often produces repeated `"I agree"` responses and wastes operator attention.
2. **Resolve the tree, branch by branch.** Surface dependent decisions and settle them across batches in dependency order.
   Do not leave a load-bearing choice implicit. It defers a decision to a later stage.
3. **Recommend an answer.** Give your best answer for every question.
   State what fails if the answer is wrong.
   Use interrogation to move toward a resolved design, not only to extract answers.
4. **Explore before you ask.** Read the codebase, vision, or command when it can answer the question.
   Do not spend operator attention on what you can resolve yourself.
5. **Continue until shared understanding.** Stop when the design is settled, not when the operator sounds tired.
   If a load-bearing choice waits for implementation, the interview is not done.

## Which Move for Which Unknown

The interview handles decisions the operator knows are open.
Route other gaps by the type of unknown.

- **Resolvable** — the repo, vision, or a command can answer it. Read it (rule 4). Never interview for facts.
- **Known unknown** — a decision the operator knows is open. Use the body of this file for the interview.
- **Unknown known** — "I'll know it when I see it" (design, copy, feel).
  Do not extract prose criteria that do not exist.
  Use disposable prototype variations and let the operator react before the spec locks.
- **Unknown unknown** — a new domain where the operator does not know what to ask.
  Run a **blindspot pass** before interrogating.
  Teach the domain's structure, desired quality, standard failure modes, and useful questions.
  Then interview. Answers from an untaught operator can base the design on guesses.

## Boundaries

Do not create questions for choices that evidence already resolves.
Do not interrogate what you can read.
Use this stance for contestable framing, not every request.

## Prompt

Before the substantial work begins:

- Load-bearing decisions still implicit:
- Next batch of open questions (each with your recommended answer):
- What you resolved by exploring instead of asking:
