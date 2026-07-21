---
disable-model-invocation: true
name: r90-ledger-guard
description: "Use when scoping MCP servers to a directory subtree in OMP (load X only here, never load Y here), auditing the R90 Habitat/Powder split, or debugging why a removed MCP server still appears in OMP sessions."
---

# Directory-scoped MCP loading in OMP (R90 Habitat/Powder case)

## Problem shape

An MCP server must load only under one filesystem subtree, and another must
never load there — at the tool-inventory level, not call-blocking.

## Verified OMP mechanics (omp v17, empirically tested — do not trust docs or
advisories on these points without a fixture test)

- Project `.omp/mcp.json` loads from the **exact cwd only**. There is NO
  ancestor-walk for MCP config (unlike skills/AGENTS.md). A file at a parent
  dir does nothing for sessions launched in child dirs.
- A project-level server with the **same name** as a user-level one and
  `"enabled": false` DOES suppress it (native provider scans project before
  user; first-wins dedup). This is the per-directory kill switch.
- `disabledServers` is honored only in the **user-level** file
  (`~/.omp/agent/mcp.json`) and hides the name **globally regardless of
  source** — it cannot express "disable only under path X", and it would also
  kill a project-level definition of that name.
- OMP **cross-discovers MCP servers from other harness configs**:
  `~/.claude.json` (top-level `mcpServers` only — entries scoped under
  `projects."<path>".mcpServers` do NOT leak into OMP), `~/.codex/config.toml`
  (`[mcp_servers.*]`), and `~/.gemini/settings.json`. Removing a server from
  OMP's own config is NOT enough; it reappears from these sources at
  priorities 80/70/60. Diagnose by neutralizing one source at a time and
  re-probing.
- No MCP path-scoping setting exists (`omp config list | grep mcp`); the
  path-scoped `disabledProviders` entries kill whole discovery sources, not
  individual servers. Profiles work but fork auth/sessions/settings — heavy.

## Solution pattern

1. One canonical `.omp/mcp.json` written to **every launch root** in the
   scoped subtree (each repo dir, the subtree root, and each live worktree
   root): define the scoped-in server; define the scoped-out server by its
   exact user-level name with `"enabled": false`.
2. Remove the scoped-in server from `~/.omp/agent/mcp.json` AND from every
   cross-tool global config (`~/.claude.json` top-level → move into its
   per-project `projects."<path>".mcpServers` slots; comment out of codex
   TOML; delete from gemini settings). Back each file up first.
3. Gitignore `.omp/` in each repo (machine-local config, not committed).
4. Keep a user-level `tool_call` hook blocking the scoped-out tool family
   under the subtree as defense-in-depth: new worktree roots lack the
   `.omp/mcp.json` until someone copies it, and the hook covers that gap.

## Verification protocol

Fixture-test mechanics FIRST if on a new OMP version: create
`/tmp/mcptest/.omp/mcp.json` with a uniquely-named real server clone plus an
`enabled:false` override of a real user-level server; probe from the dir and
a subdir with `omp -p --no-session --model <cheap>`. Then verify the real
rollout in all four quadrants with LIVE tool calls (a name listing can be
pattern-matched by the model): inside-subtree (scoped-in callable,
scoped-out ABSENT — distinguish "no such tool" from a hook block message),
outside (scoped-in ABSENT, scoped-out callable), and re-check the other
harnesses you edited (e.g. `claude -p` inside and outside the subtree).

## Residual gaps

- Brand-new worktree roots need the `.omp/mcp.json` copied in (hook covers
  the interim for call-blocking; inventory will still show the scoped-out
  server there).
- Raw `codex`/`gemini` sessions lose the de-globalized server everywhere
  (no per-project MCP mechanism in those harnesses); Roster dispatch
  projections and any CLI equivalent (e.g. scripts/habitat-ctl) are the
  sanctioned paths inside the subtree.
