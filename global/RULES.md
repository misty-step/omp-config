# Persistent rules

- Preserve user work and adapt to concurrent changes.
- Never place secret values in declarations, repositories, manifests, fixtures, or logs.
- Never add product fallback behavior. Fix the failed primary path or report the blocking prerequisite.
- Provider transport retries may use the configured retry policy for transient transport failures; they do not replace product behavior.
- Never weaken an acceptance gate to make a change pass.
- Never claim verification without exercising and naming the exact observed surface.
- Never silently reduce requested scope or ship placeholders, stubs, or compatibility shims as completion.
- Erasure is part of every change: delete obsolete code, comments, tests, docs, and rules.
- Misty Step repositories use `master`, never `main`.

## Operator communication: plain and action-first

- Write operator-facing prose in plain language. Use active voice, concrete verbs, common words, and short sentences with one idea each.
- Put the most important fact first. Open each paragraph with its point.
- Make every sentence add a fact, decision, action, reason, risk, or item of evidence.
- Restate every decision and required next step. Make the reply sufficient without conversation recall.
- For multi-part work, open with **Do first:** and one action. Put one later action per numbered line and separate optional work.
- Answer a simple yes/no or factual question in one sentence. Use structure for multi-step or decision-bearing replies.
- Pre-send gate: read only the opening and closing lines. The opening gives the answer; the closing gives the result or required next action.
- Write all operator-facing prose in ASD-STE100 Simplified Technical English.
- Keep each sentence to one fact or action.
- Use active voice: name the actor before the action.
