# Cross-session coordination

Top-level sessions do not share Hub state. Git worktrees can still share one repository and production resources.

## Procedure

1. Resolve `<git-common-dir>` with `git rev-parse --git-common-dir`. All worktrees share this path.
2. Read `<git-common-dir>/omp-coordination.md`. Create the file when absent.
3. Record UTC time, session name, resource, action, and `active` status.
4. Stop if another active entry names the same resource. Contact that session or ask the operator to select one owner.
5. Change your entry to `done` and add the result after verification.
6. Never put credentials, secret-derived data, command output, or private host details in this file.
