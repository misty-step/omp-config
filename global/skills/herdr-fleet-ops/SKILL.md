---
disable-model-invocation: true
name: herdr-fleet-ops
description: "Drive herdr-managed R90 agent fleets: read panes, nudge lanes through the 0.7.5 facade, and recover provider usage-limit stalls with in-pane model switches."
---

# Herdr Fleet Ops

Use this procedure to manage agent spaces in an R90 herdr session from another
agent session. Herdr manages terminal workspaces through a socket API. Each
project space runs an omp/pi agent in a pane. This procedure targets herdr 0.7.5.

## 0.7.5 command surface (renames that broke old recipes)

- `agent send` is GONE — use `agent send-keys` for keys (`esc`, `up`, `enter`, `ctrl+c`).
- Top-level `wait` is GONE — use `agent wait <name|pane> --until <state>` for
  lifecycle, and `pane wait-output <pane> --regex <re>` for raw text.
- Give agent commands a unique live agent NAME or the hosting pane ID. Names are
  cleared when the occupant exits, is released, or is replaced.
- Plugins are now GLOBAL per user in 0.7.5, not per-session. Reinstall a plugin
  once if you installed it only inside a named session on herdr 0.7.3.
- `herdr config check` now reports unknown config keys with full paths. Run it
  after every config edit.
## Discover

- `herdr workspace list` / `herdr pane list` — JSON; pipe to `jq` for a compact
  roster (`.result.panes[] | {pane_id, workspace_id, agent_status, terminal_title_stripped, cwd}`).
- `herdr agent list` — report each workspace's `agent_status`: idle / working /
  blocked / done / unknown. Herdr 0.7.5 hardened lifecycle for omp, pi,
  opencode, grok, kimi, and codex panes. Trust these states for gating.
- `herdr pane read <pane> --source visible|recent --lines N` /
  `herdr agent read <name>` — read exactly what the lane sees before you touch
  it. Full-screen agents may use the alternate screen. If more `--lines`
  returns no new text, scroll inside the agent and read
  `--source visible`.

## Nudge

- Prefer `herdr agent prompt <name|pane> '<text>'` — this atomic command submits
  text with encoded Enter, honors live bracketed-paste mode, preserves text like
  `A != B`, and can prompt a working agent. It replaces the old send-text,
  sleep, and send-keys Enter sequence.
- `--wait` variants: `herdr agent prompt <n> '<text>' --wait --timeout 120000`
  returns when the agent settles (`idle`/`done`/`blocked` by default). Repeat
  `--until` for exact states. If the agent starts outside a working state and
  no lifecycle change appears within 5 s, it returns `agent_prompt_stalled`.
  Treat that result as a failed submission. Read the pane and retry deliberately.
- Use the raw pane path for non-agent processes: `pane run`, `pane send-text`,
  `pane send-keys`, `pane wait-output`.
- Use `herdr --session R90 ...` explicitly when driving the R90 session.
- Oversized pastes are rejected with a client-local notification. Chunk giant
  prompts or pass a file path instead.
- Never send text into a modal state (ask dialog or picker). Cancel first with
  `agent send-keys <n> esc`. Verify the pane has returned to a prompt before
  prompting. Escape may back out only one nesting level. Text sent into an open
  model picker enters its search box and is lost.
- A lane at an `ask()` dialog waits for a human. Relay the question to the
  operator instead of pressing Esc, unless you redirect the lane to independent
  work while it waits.

## Start a helper lane (0.7.5 facade)

```
split=$(herdr pane split --current --direction right --no-focus)
pane=$(printf '%s\n' "$split" | jq -r '.result.pane.pane_id')
herdr agent start reviewer --kind omp --pane "$pane" -- <native-args>
herdr agent prompt reviewer '<task>' --wait --timeout 300000
herdr agent read reviewer --source recent-unwrapped --lines 120
```

`agent start` needs an existing shell pane at its prompt; it never creates the
layout. It returns only after the agent is detected and interactive (default
30 s; `--timeout` 3000–300000 ms). Capture pane IDs from JSON responses; never
predict them.

## Provider usage-limit stall (fleet-wide stop signature)

Symptom: Every lane shows `Codex error event: The usage limit has been reached (code=usage_limit_reached)` with `Provider requested 1800000ms wait, exceeds retry.maxDelayMs`.
Queued nudges fail. Lanes remain idle. Fix this stall by switching each lane's
model in-pane:

1. Run `herdr agent prompt <lane> '/model'` to open the picker. `/model <args>`
   with arguments is not a command; it is submitted as a prompt and fails.
2. Type filter text (for example, `claude-fable-5`) into the picker search.
3. Run `agent send-keys <lane> right` to move into the models column. Press
   `enter` on the row to open the role bar
   (`[ default ]`  `smol`  `slow`  `vision`  `plan` ...).
4. Press `enter` on `default` to open the effort bar
   (`off auto low medium high xhigh max`). Move with the arrows and press
   `enter` to assign. Left or Right may move column focus. Verify the resulting
   chip glyph in the model detail line
   (`󰪟 low · 󰪣 high · 󰪥 xhigh ·  auto`).
5. The detail line under the highlighted model shows its role chips
   (for example, `default 󰪥`). The `Roles N/10` counter must read 10/10.
   A 9/10 result means that a role lost its model. Reassign that role.
6. Run `agent send-keys <lane> esc` to close. READ THE FOOTER
   (`Fable 5++ · xhi · <cwd>`) to confirm the switch before you send kick text.
7. Send a short kick ("<why>; proceed with the earlier instructions"). The
   original nudge text already appears in the transcript as a failed user turn.

Verify each lane with `herdr agent wait <lane> --until working --timeout 30000`
after the kick, or use `herdr agent list` to confirm `working` within ~30 s.

Also know the local Agent Vault cause: a missing or denied OpenRouter service
rule, an unapproved credential slot, or a bypassed proxy/CA environment can
stall only OpenRouter-routed calls. Inspect the operator-visible service
status and request log without printing credential values before churning
lane models.

## Model palette notes (R90 convention)

For chief-executive/orchestrator lanes, use Fable high, or Sol high when Codex
has quota. The OpenAI Codex subscription is the fleet's historical default and
a single point of failure. Prefer mixed-provider defaults per lane.

## Custom sidebar telemetry (0.7.5)

Lanes can publish fleet-readable status into the sidebar. Add a `$token` to
`[ui.sidebar.agents]` rows. Then have the lane or a hook run
`herdr pane report-metadata <pane> --source <hook> --token model=<slug> --token summary="<one-liner>"`.
Unreported tokens disappear. Styling lives in the local config, not the reporter.
