---
name: roster
description: |
  Discover and dispatch the agent fleet. Any Roster agent may commission any
  other agent; there is no declared delegates list. Use when: "delegate this",
  "dispatch an agent", "who can do this", "hand this to a builder/reviewer/
  verifier", "launch a focused agent", or any time work should run in a fresh,
  independently composed context instead of this one.
  Trigger: /roster, /dispatch.
argument-hint: "[agent]"
---

# /roster

Every agent in the fleet can commission every other agent. Who exists, what
they carry, and how to launch them is discovered live from the CLI — never
from memory or a hardcoded list.

## See the fleet

```sh
roster list            # launchable agent definitions in the effective config
roster show <agent>    # one agent's exact resolved composition (role, model,
                       # harness, guidance, skills, MCPs)
```

Pick by role fit, not by name familiarity. An agent's role description is the
contract for what it will and won't do.

## Dispatch

```sh
roster dispatch <agent>
roster dispatch --default <codex|claude|omp>
```

This resolves the agent's full graph into a temporary, isolated bundle,
launches its harness in the current workspace, and removes the projection
after exit. The dispatched agent gets its own role's skills and MCPs — not
yours.

`--default` is for stable operator shortcuts. It resolves only the explicit
Harness mapping in the effective config, so the same command can launch Kaylee
under the home config and Penelope under an R90-local config. It never infers
from a role, declaration order, or filesystem path. Use a named agent for
delegation; use the Harness default only when the operator has intentionally
asked for that workspace's default interactive agent. Unless `--config` is
explicit, `--default` discovers from the current workspace instead of inheriting
the running agent's `ROSTER_CONFIG` pin.

Commission outcome-shaped lanes: give the agent a role-appropriate objective,
exact scope, an oracle it can run, the output shape you need back, and hard
boundaries. Give fresh critics (reviewer, verifier) only the artifact and the
oracle — never the author's reasoning trail.

For a one-off composition that does not deserve a durable role yet, resolve or
dispatch an ephemeral role:

```sh
roster dispatch \
  --using <binding-agent> \
  --as <runtime-name> \
  --purpose "<one concise why>" \
  --include <source/pack:name-or-primitive> \
  --include <source/skill:name>
```

`--using` supplies only the configured Harness, model, reasoning, and native
arguments. Its role contributes nothing. The repeatable `--include` values are
the complete role and use the same additive resolver as declared roles. Use
`roster resolve` with the same selector and `--output` to inspect the exact
bundle. Promote a composition to a named role when it recurs or becomes part of
an operating contract.

## Ground rules

- One card, one lane: a dispatched agent works one commissioned outcome.
- Don't chain dispatches to simulate a pipeline the operator didn't ask for;
  each hop loses context and costs attention.
- If no named agent fits, use an explicit ad-hoc role for one-off work. Record
  an agent-creation gap only when the composition should recur.
