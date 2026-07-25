# Hatchet terminal evidence stage — evidence packet

Produce the terminal evidence record for this card. Do not change the
repository, and never form a new opinion about it — package what the prior
stages already established.

Card: **{{card.title}}** (priority: {{card.priority}}).
Stage `{{stage}}`, round {{round}}. Required current HEAD: `{{head_sha}}`.

{{card.body}}

Acceptance criteria this run attempted:
{{card.criteria}}

Runtime context, including the proposed terminal state and every prior
stage's durable evidence: {{task}}

1. Read the proposed terminal state and every prior stage's evidence from
   the runtime context above. Do not re-derive, second-guess, or add a
   finding of your own — this stage packages, it never judges.

2. Confirm the required HEAD, current branch, the recipe-authored commits
   that produced it, and a clean worktree. Never merge, push, edit, or
   commit.

3. Assemble the artifact refs so they compactly preserve, in one place:

   - the proposed terminal state;
   - the implement commit and the remediation commit(s), if any;
   - every adversarial-review round's outcome (`accepted` or `blocked`)
     and its ranked findings packet;
   - the live-verification PASS/WARN/FAIL/SKIP evidence;
   - `merge:false;operatorApprovalRequired:true`.

   A field you cannot find in the runtime context is a hard stop, not a
   gap to paper over — this stage has no authority to invent evidence.

4. Call `hatchet_terminal` exactly once with outcome `completed`, the
   unchanged full HEAD, and the artifact refs assembled above. This tool
   is the only completion channel. Do not print terminal JSON or call
   `yield`; after the tool accepts the terminal, end the turn.

5. If the proposed state is `awaiting_operator_approval`, name it exactly.
   Never claim operator approval, card completion, merge, or deployment —
   Hatchet stops here; a human decides next.
