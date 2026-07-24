# Hatchet remediation stage

Fix the blocking findings from the immediately preceding adversarial review for `omp-config-tools-wildcard-resolution`.

1. Read the prior durable stage evidence embedded in the task and verify each finding against current HEAD.
2. Fix every confirmed blocker at its source without adding wildcard compatibility, copied catalogs, shims, or unrelated changes.
3. Run only the focused checks that exercise the corrected behavior. Do not run formatters, linters, or broad suites.
4. Create one new commit with `git -c user.name='OMP Hatchet Remediate' -c user.email='omp-hatchet-remediate@local' commit ...`. Never merge, push, or rewrite history.
5. After the new commit and checks, call `hatchet_terminal` exactly once with outcome `completed`, the new full HEAD, and artifact refs naming the remediation commit, resolved review findings, and exact focused command results. This tool is the only completion channel. Do not print terminal JSON or call `yield`; after the tool accepts the terminal, end the turn. Do not report completion without a new commit.
