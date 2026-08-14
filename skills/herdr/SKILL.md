---
name: herdr
description: Inspect or control the current Herdr workspace and recognized agent sessions.
---

# Herdr

Before a control action, require:

```bash
test "${HERDR_ENV:-}" = 1
```

If the check passes, run `herdr --skill` and follow its version-matched
instructions. They own command syntax, IDs, focus, lifecycle, and safety.

Report exact workspace, pane, or agent IDs; command status; lifecycle state;
retained process state; and user-focus changes.
