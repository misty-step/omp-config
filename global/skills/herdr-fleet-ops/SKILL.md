---
disable-model-invocation: true
name: herdr-fleet-ops
description: "Drive and unstick herdr-managed agent fleets (R90 spaces): read panes, nudge lanes via the 0.7.5 agent facade, recover from provider usage-limit stalls via in-pane model switch."
---

# Herdr Fleet Ops

Operating procedure for managing the R90 herdr session's agent spaces from another agent session. herdr is a terminal workspace manager with a socket API; each project space runs an omp/pi agent in a pane. Written against herdr 0.7.5.

## 0.7.5 command surface (renames that broke old recipes)

- `agent send` is GONE — use `agent send-keys` for keys (`esc`, `up`, `enter`, `ctrl+c`).
- Top-level `wait` is GONE — use `agent wait <name|pane> --until <state>` for lifecycle, `pane wait-output <pane> --regex <re>` for raw text.
- Agent commands accept a unique live agent NAME or the hosting pane ID. Names are cleared when the occupant exits, is released, or is replaced.
- Plugins are now GLOBAL per user (0.7.5 breaking change), not per-session; a plugin installed only inside a named session on 0.7.3 must be reinstalled once.
- `herdr config check` now reports unknown config keys with full paths — run it after every config edit.

## Discover

- `herdr workspace list` / `herdr pane list` — JSON; pipe to `jq` for a compact roster (`.result.panes[] | {pane_id, workspace_id, agent_status, terminal_title_stripped, cwd}`).
- `herdr agent list` — per-workspace `agent_status`: idle / working / blocked / done / unknown. 0.7.5 hardened lifecycle for omp, pi, opencode, grok, kimi, and codex panes, so these states are trustworthy for gating.
- `herdr pane read <pane> --source visible|recent --lines N` / `herdr agent read <name>` — see exactly what the lane sees before touching it. Full-screen agents may use the alternate screen; if more `--lines` returns nothing new, scroll inside the agent and read `--source visible`.

## Nudge

- PREFER `herdr agent prompt <name|pane> '<text>'` — atomic: submits text plus encoded Enter, honors live bracketed-paste mode (preserves text like `A != B`), and can prompt an agent that is already working. This replaces the old send-text + sleep + send-keys Enter dance.
- `--wait` variants: `herdr agent prompt <n> '<text>' --wait --timeout 120000` returns when the agent settles (`idle`/`done`/`blocked` by default; repeat `--until` for exact states). If the agent starts from a non-working state and no lifecycle change is observed within 5 s, it returns `agent_prompt_stalled` — treat that as "the submission did not take", read the pane, and retry deliberately.
- Raw pane path still exists for non-agent processes: `pane run`, `pane send-text`, `pane send-keys`, `pane wait-output`.
- Use `herdr --session R90 ...` explicitly when driving the R90 session.
- Oversized pastes are rejected with a client-local notification (no more client disconnect) — chunk giant prompts or pass a file path instead.
- Never send text into a modal state (ask dialog, picker). Cancel first with `agent send-keys <n> esc`, and VERIFY the pane is back at a prompt with a read before prompting — Escape may only back out one nesting level, and text sent into an open model picker lands in its search box (harmless but lost).
- A lane at an `ask()` dialog is blocked on a human: relay the question to the operator instead of Esc-ing past it, unless redirecting the lane to independent work while it waits.

## Start a helper lane (0.7.5 facade)

```
split=$(herdr pane split --current --direction right --no-focus)
pane=$(printf '%s\n' "$split" | jq -r '.result.pane.pane_id')
herdr agent start reviewer --kind omp --pane "$pane" -- <native-args>
herdr agent prompt reviewer '<task>' --wait --timeout 300000
herdr agent read reviewer --source recent-unwrapped --lines 120
```

`agent start` needs an existing shell pane at its prompt; it never creates layout. It returns only after the agent is detected and interactive (default 30 s; `--timeout` 3000–300000 ms). Capture pane IDs from the JSON responses; never predict them.

## Provider usage-limit stall (fleet-wide stop signature)

Symptom: every lane shows `Codex error event: The usage limit has been reached (code=usage_limit_reached)` with `Provider requested 1800000ms wait, exceeds retry.maxDelayMs`. Queued nudges error out; lanes sit idle. Fix by switching each lane's model in-pane:

1. `herdr agent prompt <lane> '/model'` opens the picker. `/model <args>` with arguments is NOT a command — it gets submitted as a prompt and errors.
2. Type filter text (e.g. `claude-fable-5`) — goes into the picker search.
3. `agent send-keys <lane> right` moves into the models column; `enter` on the row opens the role bar (`[ default ]  smol  slow  vision  plan ...`).
4. `enter` on `default` opens the effort bar (`off auto low medium high xhigh max`); arrows move, `enter` assigns. Left/Right may be consumed by column focus — verify the resulting chip glyph in the model detail line (`󰪟 low · 󰪣 high · 󰪥 xhigh ·  auto`).
5. The detail line under the highlighted model shows its role chips (e.g. `default 󰪥`); the `Roles N/10` counter must read 10/10 — 9/10 means a role lost its model (you toggled one off by accident; reassign).
6. `agent send-keys <lane> esc` to close; READ THE FOOTER (`Fable 5++ · xhi · <cwd>`) to confirm the switch actually happened before sending any kick text.
7. Send a short kick ("<why>; proceed with the earlier instructions") — the original nudge text is already in the transcript as a failed user turn.

Per-lane verification: `herdr agent wait <lane> --until working --timeout 30000` after the kick, or `herdr agent list` flipping to `working` within ~30 s.

Also know the mint-side cause: a lifetime `max_calls` policy cap (no `window_seconds`) denies ALL OpenRouter-routed calls until the rule gains a window (incident 2026-07-21, fixed in mint `ed65ec3`). If the stall is OpenRouter-specific with `call limit exhausted` in the error, check the mint broker rule before churning lane models.

## Model palette notes (R90 convention)

Chief-executive/orchestrator lanes: Fable high (or Sol high when Codex has quota). OpenAI Codex subscription is the fleet's historical default and a single point of failure — mixed-provider defaults per lane are preferable.

## Custom sidebar telemetry (0.7.5)

Lanes can publish fleet-readable status into the sidebar: add a `$token` to `[ui.sidebar.agents]` rows, then have the lane (or a hook) run `herdr pane report-metadata <pane> --source <hook> --token model=<slug> --token summary="<one-liner>"`. Unreported tokens disappear; styling lives in the local config, not the reporter.
