# Hatchet terminal evidence stage

Produce the terminal evidence record. Do not change the repository.

1. Read the proposed terminal state and all prior durable stage evidence embedded in the task.
2. Confirm the required HEAD, branch, recent recipe-authored commits, and clean worktree. Never merge, push, edit, or commit.
3. Call `hatchet_terminal` exactly once with outcome `completed` and the unchanged full HEAD. Artifact refs must compactly preserve the proposed terminal state, implement/remediation commits, every review outcome, focused gate and live Task evidence, and `merge:false;operatorApprovalRequired:true`. This tool is the only completion channel. Do not print terminal JSON or call `yield`; after the tool accepts the terminal, end the turn.
4. If the proposed state is `awaiting_operator_approval`, name it exactly. Do not claim operator approval, card completion, merge, or deployment.
