---
name: verification
description: Create or maintain a repo-local verification skill with a complete user-POV feature map and live proof loop. Use for /verification create, /verification maintain, create-verification-skill, or maintain-verification-skill.
disable-model-invocation: true
argument-hint: "[create|maintain] <repo-path> [--state <state-path>]"
---

# /verification

Create or maintain a repo-local verification skill for one repository.
The skill drives real user paths and records evidence that another agent can inspect.

Use one of these flow entries:

```text
/verification create <repo-path>
/verification maintain <repo-path> [--state <state-path>]
```

`create-verification-skill` and `maintain-verification-skill` are the two flow names in this skill.
Do not create a second global skill for either name.

## Boundaries

- Keep all generated changes in `<repo>/.agents/skills/<repo>-qa/`.
- Reuse an existing `<repo>-qa` skill instead of creating a parallel skill.
- Never change product code during maintenance.
- Report product regressions instead of changing verification text to hide them.
- Use local, development, or staging entrypoints.
- Do not target production unless the operator names it and approves the risk.
- Never place raw credentials in a skill, command, fixture, transcript, or evidence.
- Use Mint markers for credentialed vendor calls: `__mint.<alias>__`.
- Never kill a process by name; clean up only instances that the run started.
- Do not commit or open a pull request automatically.
- A generated skill must contain exact, observed commands.
- A generated skill must not contain guessed commands or unresolved placeholders.

## Composition with existing skills

| Need | Use | Boundary |
|---|---|---|
| Browser or live entrypoint mechanics | `skill://verify-live` | Use its browser escalation ladder, evidence rules, verdicts, and session hygiene. |
| Bounded persona sessions | `skill://qa-users` | Use its frozen non-production entrypoints, leaf authority, triage, and tracker rules. |
| Automated test-system quality | `skill://quality` with the `tests` domain | Route test inventory, falsifiers, suite rigor, and test remediation there. |
| Repository-specific verification | `<repo>/.agents/skills/<repo>-qa/SKILL.md` | Keep exact launch, doctor, drive, evidence, cleanup, gotchas, and report details here. |

This skill adds complete feature coverage and recurring upkeep.
It does not duplicate the browser ladder, persona dispatch, tracker policy, or automated-test program.

# Flow: create-verification-skill

Generate or refresh one repository's local `<repo>-qa` verification skill.

## 1. Interview the repository, not the operator

Read the repository and answer each question before asking for missing facts:

1. **Surface:** What does a user touch: web UI, CLI, TUI, desktop app, API, mobile app, MCP tool, or library?
2. **Run:** What exact documented command starts the app or builds the short-lived client?
3. **Ready:** What log line, port response, prompt, health route, or version output proves readiness?
4. **Drive:** What existing harness can interact with the real surface?
5. **Observe:** Which screenshots, transcripts, response bodies, logs, exit codes, files, rows, or messages prove the result?
6. **Isolate:** Which ports, data directories, profiles, accounts, or sessions isolate this run from user state?
7. **Coverage:** Which routes, commands, menus, tool schemas, workflows, and docs expose user-facing features?

Prefer evidence in package scripts, Makefiles, task files, READMEs, routes, CLI help, schemas, and existing QA skills.
Use existing Playwright, Cypress, browser, PTY, HTTP, MCP, or consumer harnesses before choosing a generic driver.
Use stable ARIA labels, data attributes, prompt strings, route paths, command names, and tool names.

If the repository cannot build or start, record the exact blocker and stop generation.
Do not encode a verification skill against a broken or guessed base.

## 2. Generate the local skill

Write or update this path:

```text
<repo>/.agents/skills/<repo>-qa/SKILL.md
```

Use YAML frontmatter with `name: <repo>-qa` and a description that names the app, its primary surface, and when to use the skill.
Preserve valid repository-specific content when the file already exists.

The body must contain these sections:

### Launch

- Give the exact command that starts the verification instance.
- Give every required non-secret environment setting.
- State the readiness signal.
- State the teardown command or owned process handle.
- For a short-lived CLI or TUI, state the build or install step and isolated PTY or tmux setup.

### Doctor

Give one read-only check for process health, version or build identity, port ownership, and auth validity when applicable.
An agent runs Doctor before the first drive and after every surprising failure.

### Drive

Give harness commands and real selectors from this repository.
Describe the user action and the state transition it should cause.
Use one instance serially for servers and UIs unless the repository requires isolated sessions.

### Evidence

Require evidence of both the action and the resulting state.
Require side-effect checks, such as file reads, row reads, response bodies, message delivery, or ledger state.
Use the `verify-live` verdict vocabulary when it applies: PASS, WARN, FAIL, or SKIP.
If a dry-run or test mode exists, observe what it actually skips instead of trusting its name.
Name the durable evidence path and create it before the drive.

### Cleanup

Stop only processes and sessions that this run started.
Remove scratch state and disposable data, but never remove evidence.
After cleanup, confirm that the named evidence still exists.

### Helpers

Every owned helper must be executable.
Show the exact helper invocation in the skill body.
Do not require a reader to reverse-engineer a helper.

### Report

Return the verdict, exact commands, surfaces covered, artifacts inspected, and uncovered surfaces.
Name every blocker and every external prerequisite.

Do not put product fixes, test-only shortcuts, fake endpoints, or fallback behavior in this skill.

## 3. Seed the complete feature map

Create this directory beside the local skill:

```text
<repo>/.agents/skills/<repo>-qa/features/
```

Create `features/README.md` and one Markdown file for every user-facing feature found during the repository interview.
Do not stop at a convenient top-three-to-five sample.

### Feature index contract

`features/README.md` must contain:

- The feature-map scope and the repository revision inspected.
- One table row for every feature file.
- A stable feature slug and human name.
- The primary surface and user entrypoint.
- A link to the feature file.
- Source paths or route, command, menu, or schema anchors.
- A status that distinguishes covered, blocked, and verified-unreachable features.

A missing, duplicate, extra, or dead index row is map drift.
Do not generate a separate inventory that can become a second source of truth.

### Feature file contract

Each feature file must identify its feature, surface, source anchors, prerequisites, and evidence location.
Use these four H2 headings exactly, replacing `<harness>` with the actual harness name:

```markdown
## Sub-features
## How to get to it (user POV)
## Driving it with <harness>
## Gotchas
```

Each file must answer these questions from the user's point of view:

- What does this feature do?
- How does a user reach it from a real entrypoint?
- Which exact actions use it, including important variants and error paths?
- Which visible result and side effect prove that it works?
- Which evidence artifact records the proof?
- Which auth, data, OS, network, or external-state prerequisite can block it?

Under `Sub-features`, list meaningful variants and child workflows.
Under `How to get to it (user POV)`, give the route, command, menu path, or tool selection.
Under `Driving it with <harness>`, use a table with action, expected state, and proof artifact columns.
Under `Gotchas`, record destructive actions, shared-state risks, auth limits, and cleanup rules.

Map every user-facing surface discovered in source and docs, including CLI commands, API routes, browser routes, menus, MCP tools, and workflows.
Treat the feature map as the maintained verification source, not as optional documentation.

## 4. Prove the generated skill

Run the generated skill once before handoff:

1. Launch the real app or isolated client.
2. Run Doctor.
3. Drive one mapped feature through its user path.
4. Capture action, result, side effect, and evidence.
5. Run Cleanup.
6. Confirm the evidence remains at its named path.

Use throwaway data and isolated resources.
If a step fails, clean up the failed iteration before changing the skill or retrying.
A generated skill that was not executed is a draft.

# Flow: maintain-verification-skill

Keep one repository's local skill and complete feature map aligned with source and live behavior.
The unit of coverage is the feature file, not one convenient sentence or route.

## Loop entry

The recurring entry is substrate-agnostic:

```text
systemd timer -> OMP recipe -> fresh `/verification maintain` run
```

The outer scheduler supplies the repository, state path, evidence root, run identifier, and budgets.
The recipe starts a fresh verifier and passes these logical inputs:

- `repo_path`
- `skill_path`
- `state_path`
- `evidence_root`
- `run_id`
- `max_duration`
- `max_retries`

Do not name or require a particular systemd unit, recipe binary, queue, or event service in this skill.
Do not invoke systemd from the skill.

Persist durable state at `state_path` after each feature and at the final outcome.
State must include the map digest, inspected repository revision, per-feature status, evidence paths, outcome, blocker, and next action.
Do not report `clean` when state or evidence cannot persist.

## Outcomes

Choose one final outcome and state it:

- **clean** — every feature received source and live coverage, and no correction is needed.
- **changed** — proven corrections changed only the local verification skill, map, or owned helper.
- **blocked** — coverage or a safe correction could not finish; name the exact blocker.

A feature is **verified-unreachable** only when the attempted route and concrete prerequisite are recorded.
Do not use that label for an undocumented route, broken harness, or missing map entry.

## Edit scope

Edit only `<repo>/.agents/skills/<repo>-qa/` and its owned helpers.
Never edit product code, product tests, deployment files, tracker state, or unrelated skills.
Do not weaken a gate, threshold, oracle, auth check, or cleanup rule.
Do not auto-commit or open a pull request.
Return a reviewable patch summary to the owning lane.

## Pass

### 0. Locate the target

Find the repository-local `<repo>-qa` skill with Launch, Drive, and a feature map.
If several candidates exist, stop and name them for selection.
If none exists, stop and route to `/verification create <repo-path>`.

### 1. Check index hygiene

Read `features/README.md` and glob sibling feature files.
Fix missing, extra, duplicate, dead, or stale links within the owned skill directory.
Do not create a generated inventory beside the README.

### 2. Run the source wave

Dispatch one read-only source reader per feature file, concurrently.
Each reader must return this shape:

```text
feature summary
source entry points
likely drift or none
one live verification recipe
```

Readers may inspect source and docs.
Readers must not drive the app, edit files, access tracker state, or change product code.

### 3. Reconcile source findings

Require a returned summary for every feature file.
Spot-check cited drift before editing.
Merge duplicate recipes into as few app states as practical.
Sweep recent repository changes for user-facing surfaces missing from the map.
Require a concrete source path before adding a missing feature.

### 4. Run the live pass

Follow the target skill's own Launch, Doctor, Drive, Evidence, and Cleanup sections.
Use `skill://verify-live` for browser or live-entrypoint mechanics.
Use `skill://qa-users` when the requested run is persona-driven.
Use a long-lived instance serially for servers and UIs.
Use a fresh isolated session for each short-lived CLI or TUI drive.

Hold these invariants for the whole pass:

1. Run Doctor before the first drive, after every surprising failure, and for every fresh session.
2. Reset or relaunch a wedged UI even when the process health check passes.
3. Preserve every evidence artifact through every cleanup and verify it at its named path.
4. Clean residue from every failed iteration, including sessions that exited or became stuck.
5. Teardown the final instance after the last drive, including any re-proof.

Exercise every feature at least once.
Capture the action, resulting state, side effect, and evidence for every feature.

Classify an unreachable feature as `verified-unreachable` only with its attempted route and concrete prerequisite.
If the map omitted that prerequisite, fix the map under edit scope.

If Doctor fails because the local skill drifted, correct the skill and retry once.
Restart only the instance invalidated by that correction.
Re-drive every harness fix before accepting it.

### 5. Triage

Fix wrong or missing user-POV descriptions as map drift.
Fix a working behavior that the harness cannot drive as a harness gap.
Keep product behavior failures as product findings; do not paper over them in the skill.

### 6. Ship or stop

For `clean`, make no patch and report complete coverage.
For `changed`, keep one reviewable patch of proven skill, map, or helper corrections.
For `blocked`, stop safely and report completed coverage, attempted route, blocker, evidence, and next action.
Re-read every changed file before returning the outcome.

## Loop budgets and halt rules

Run one bounded maintenance pass per recipe invocation.
Allow at most one retry for Doctor failure caused by verification-skill drift.
Stop on missing authorization, unsafe shared-state access, missing prerequisite, evidence loss, ownership conflict, no-progress, or budget exhaustion.
Never extend a run by silently reducing feature coverage.

## Maintenance report

Return:

- outcome: `clean`, `changed`, or `blocked`
- repository revision and map digest
- every feature status and source/live coverage
- exact commands or harness actions
- evidence paths that survived cleanup
- verified-unreachable prerequisites
- changed files, if any
- blockers, residual gaps, and next action
