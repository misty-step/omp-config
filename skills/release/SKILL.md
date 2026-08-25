---
name: release
description: Address review, confirm CI is not failing, merge, deploy, verify production, and watch. Revert and investigate if ship or verify fails.
disable-model-invocation: true
argument-hint: "[pull request]"
---

# Release

Ship one pull request. Watch it in production. If it fails, revert and find out why.

```text
review clean -> CI not failing -> merge -> deploy -> verify -> watch
on red: revert -> investigate -> operator -> fix -> postmortem
```

Explicit `/release` is the go-ahead to merge and deploy that PR. It authorizes
the repository's ordinary rollback (revert the merge, reinstall the previous
binary) if verify fails. It does not authorize a different production change.

## 1. Review clean

Open the PR. Record the exact head SHA.

- Every in-scope review finding is addressed or explicitly declined with a
  reason on the PR.
- No open Blocker from `/code-review` remains.
- Human approval is not a gate. Bot comments are not a gate.

If a supported defect is still open, fix it on the branch and start again at
this step. Do not merge around it.

Completion criterion: Head SHA recorded. In-scope review is closed.

## 2. CI not failing

Look at checks on that exact head.

- Failing required or existing CI blocks the ship.
- Missing CI is not a failure. Do not invent a suite to satisfy this step.
- Re-run a failed check once if it looks flaky. A second failure blocks.

Completion criterion: No failing check on the recorded head.

## 3. Merge

Confirm the PR head still equals the recorded SHA. Merge that head through the
repository's normal path (`gh pr merge`, protected rules if they exist).

Record the merge commit. Wait for post-merge checks if the repo has them. A
new failure after merge blocks deploy: revert, do not push a second fix onto
the live merge.

Completion criterion: The merge commit contains the recorded head.

## 4. Deploy

Deploy through the path this repo already owns (documented install, unit,
`go install`, workflow). Observe what actually started.

If the runtime can name its revision, record it. If it cannot, say so and
continue — do not block the ship for a missing version command.

A deploy that never starts, or starts the wrong artifact, is red. Go to
Recover.

Completion criterion: The owned deploy path ran and the new code is what
production will execute.

## 5. Verify

Exercise the changed surface the way an operator would. Health, smoke, and
the specific path this PR changed. Capture what you ran and what you saw.

Green: hand `skill://watch-deploy` the repo, environment, merge SHA, deploy
identity if known, rollback command, and soak window (repo default, else one
deploy cycle or 30 minutes).

Red: go to Recover. Do not keep poking production.

Completion criterion: Production behaves, or recovery has started.

## 6. Recover

Stop new work. Keep the failing evidence.

1. Say what failed, which release, and what the operator or user sees.
2. Revert the merge or reinstall the previous binary — one action.
3. Confirm the revert actually restored the surface.
4. Tell the operator what broke and what you reverted.
5. Reproduce, fix on a new branch, and start again at Review clean.
6. Write a short postmortem when the failure shipped, risked data, or needed
   a revert.

Do not retry the same broken revision. Three failed recoveries: stop mutating
and escalate.

Completion criterion: Production is healthy again, or mutation has stopped
and the operator has the incident.
