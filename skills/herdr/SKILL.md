---
name: herdr
description: Inspect or control Herdr without stealing the operator's active workspace.
---

# Herdr

The operator owns the active workspace, tab, and pane. Preserve focus.

Inspect sessions before control. Address only recognized agent sessions. Prefer
background or existing inactive surfaces. Never switch, close, type into, or
reuse the operator's active surface unless the operator names it.

Before a control action, state the target session and expected visible effect.
Afterward, verify the target changed and the operator's focus did not.

Done when the requested agent state is reached without altering unrelated
workspace state.
