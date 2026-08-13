---
name: herdr
description: Inspect and control the current Herdr terminal workspace and recognized agent sessions.
disable-model-invocation: false
---

# Herdr

Herdr owns terminal layout, process continuity, and recognized coding-agent
lifecycle. It does not replace task decomposition, acceptance contracts, or
verification.

Before any control action, verify this session is inside Herdr:

```bash
test "${HERDR_ENV:-}" = 1
```

If that fails, stop. Do not control the focused Herdr session from outside a
managed pane.

Then run `herdr --skill` and follow the installed binary's version-matched
instructions. That output owns command syntax, IDs, focus behavior, lifecycle
semantics, and safety boundaries. Do not rely on remembered command recipes.

Herdr lifecycle state is not an acceptance verdict. Report exact workspace,
tab, pane, or agent IDs; command status; observed lifecycle state; retained
process state; and any user-focus change.
