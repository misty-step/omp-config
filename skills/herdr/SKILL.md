---
name: herdr
description: Inspect or control Herdr while preserving operator focus and managing recognized agent sessions.
---

# Herdr

Preserve operator focus. The operator owns the active workspace, tab, and pane.

Before a control action, require:

```bash
test "${HERDR_ENV:-}" = 1
```

If the check passes, run `herdr --skill` and follow its version-matched
instructions for command syntax, IDs, lifecycle, and safety.

For every layout-changing action:

- Record the focused workspace, tab, and pane before the action.
- Create, move, and split with `--no-focus`.
- Target the caller with `--current`, or use an ID read from context or a
  command response.
- Keep background tabs and panes unfocused.
- Compare focus after the action with the recorded focus.

A focus flag or focus command requires an explicit operator request to change
focus. If an action can change focus and has no no-focus form, stop and report
the constraint.

Report exact workspace, tab, pane, or agent IDs; command status; lifecycle
state; retained process state; and whether focus remained unchanged.

Completion criterion: The requested action is complete and operator focus is
unchanged, or the operator's explicit focus request is complete.
