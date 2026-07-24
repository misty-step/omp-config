---
disable-model-invocation: true
name: verify-live
description: |
  Live-behavior verification playbook: drive a real browser and real
  entrypoints, prove a change works or fails, and return PASS/WARN/FAIL/SKIP
  evidence. Escalation ladder across the builtin browser tool, the
  agent-browser CLI, and the chrome-devtools CLI. Use when asked to verify,
  QA, smoke-test, or reproduce a rendered surface, golden path, performance,
  or console/network behavior against a running app.
  Trigger: /verify-live.
---

# /verify-live

Reproduce the claimed behavior through the real user-facing surface before
trusting it. "Tests pass" is not verification — exercise the exact contract
named in the claim and capture the command, screenshot, snapshot, or log
that shows it. Never repair the artifact you are verifying: no edits, no
writes, no commits, no mutating a tracker. State what was exercised and what
was not as clearly as the verdict itself.

## Escalation ladder

Three tiers, cheapest first. Never skip to a higher tier for a job a lower
tier settles — each step up costs more tokens or more setup.

**Tier 1 — builtin `browser` tool.** Zero standing cost, already loaded.
Puppeteer-based: `tab.observe()`, `tab.ariaSnapshot()`, `tab.screenshot`,
`tab.evaluate`, CSS and `aria/`/`text/`/`xpath/`/`pierce/` selectors.
Playwright-only pseudo-selectors (`:has-text()`, `:visible`) are rejected —
use `aria/<role>` or `text/<substring>` instead. Default for "does the
golden path still work" and "did this render."

**Tier 2 — `agent-browser` CLI via `bash`**
(`/Users/phaedrus/.npm-global/bin/agent-browser`, v0.31.1). Reach for it only
for what tier 1 cannot do: isolated console capture, uncaught-error
isolation, network request lists and HAR export, snapshot/screenshot diffing
against a saved baseline, Core Web Vitals, video recording of an interactive
repro, and auth/session persistence across commands. Run
`agent-browser skills get core` before your first command in a session —
its usage guide is served by the installed binary and self-updates on
upgrade, so this skill deliberately does not hardcode its full grammar. Add
`--full` for the complete command reference when core is not enough.

**Tier 3 — `chrome-devtools` CLI via `bash`**
(`/Users/phaedrus/.bun/bin/chrome-devtools`, v1.6.0). Only for
Lighthouse-scored audits, performance trace-insight analysis, and heap
snapshots — jobs neither tier 1 nor tier 2 covers. These are token-expensive;
always pass an output/file path (`--outputDirPath`, `--filePath`) so the
heavy payload lands on disk instead of spilling into context, then read only
the summary you need. The `chrome-devtools` MCP server is defined in
`global/mcp.json` but sits in `disabledServers` and stays disabled — running
~36 always-on tool schemas through every turn is a token tax the CLI avoids
entirely; both Google and Microsoft now recommend CLI-plus-skills over
always-on MCP for coding agents for this exact reason. Do not re-enable it.

## Job routing table

| Job | Tier | Command / call |
|---|---|---|
| Golden path still works | 1 | `tab.observe()` / `tab.ariaSnapshot()` to find refs, then `tab.click`/`tab.fill` through the flow, re-observing after each navigation |
| Visual change rendered correctly | 1 (single check) / 2 (regression) | 1: `tab.screenshot()`. 2: `agent-browser diff screenshot --baseline <path>` or `agent-browser diff snapshot` against a saved baseline |
| Page is slow | 2 (Web Vitals) / 3 (root cause) | 2: `agent-browser vitals <url> --json`. 3: `chrome-devtools performance_start_trace --reload --filePath <path>` then `performance_stop_trace` and `performance_analyze_insight <insightSetId> <insightName>` |
| Accessibility | 1 (quick tree) / 3 (scored audit) | 1: `tab.ariaSnapshot()`. 3: `chrome-devtools lighthouse_audit --outputDirPath <path>` (covers accessibility, SEO, best practices, agentic browsing — not performance) |
| What network calls fired | 2 | `agent-browser network requests [--filter <pattern>]`, or `agent-browser network har start <path>` / `har stop` for a full HAR |
| Console error appeared | 2 | `agent-browser console` for all messages, `agent-browser errors` to isolate uncaught JS exceptions |

## Repro-first evidence discipline

- Reproduce before reporting. Verify the issue repeats at least once before recording it as a finding — a single unreplicated glitch is not evidence.
- Document each issue immediately, in the same pass as exploration. Do not tour the whole surface first and write up findings afterward — a session interruption should never cost you a finding already found.
- Interactive or state-dependent issues need a video plus step-by-step screenshots: `agent-browser record start <path>` before the repro, one screenshot per step, `record stop` after the broken state is visible.
- Static issues visible on load (layout, typos, clipped text) need exactly one annotated screenshot: `tab.screenshot()` or `agent-browser screenshot --annotate <path>`. No video.
- Never delete evidence mid-session. Do not `rm` a screenshot, video, or log because it turned out benign — note it was checked and move on.

## Verdicts

Report `PASS`, `WARN`, `FAIL`, or `SKIP` per checked surface:

- **PASS** — the exact command or interaction ran and the observed result matches the claim.
- **WARN** — the surface works but shows a real, named problem that does not invalidate the claim.
- **FAIL** — the observed result contradicts the claim. Name the exact mismatch.
- **SKIP** — the surface could not be exercised (missing credentials, unreachable environment, no driver). Name the blocker; never silently omit a claimed surface.

Every verdict names the exact command run and the exact observed result — a
snapshot excerpt, a screenshot path, a status code, a console line. A green
aggregate across verdicts is necessary, not sufficient: one FAIL on the
actual claim outweighs ten unrelated PASSes.

## Hard prohibitions

- Never repair the artifact under verification. Report the break; do not patch it.
- Never weaken a gate, threshold, or oracle to manufacture a pass.
- Never claim a surface was verified without naming the exact tool call and observed output that exercised it.
- Never assert rendered behavior without an actual render — no inferring visual correctness from source code.

## Session hygiene

Create the evidence output directory before starting
(`mkdir -p <out>/screenshots <out>/videos`) so nothing races a missing path
mid-session. Close every session you opened before finishing:
`agent-browser close --all` for CLI sessions, and close browser tabs opened
through the builtin tool. If tier 3 was used, `chrome-devtools stop` when
the audit is done.

## Reference material (read on demand, not autoloaded)

These live under `global/external/`, which is not projected into the live
skills directory — read them directly by absolute path when the job needs
more depth than this file carries:

- `/Users/phaedrus/Development/omp-config/global/external/vercel-agent-browser/SKILL.md` — agent-browser discovery stub; the authoritative grammar is `agent-browser skills get core`, not this file.
- `/Users/phaedrus/Development/omp-config/global/external/vercel-dogfood/SKILL.md` — full exploratory-QA workflow this ladder condenses.
- `/Users/phaedrus/Development/omp-config/global/external/vercel-dogfood/references/issue-taxonomy.md` — severity/category taxonomy and exploration checklist for open-ended bug hunts.
- `/Users/phaedrus/Development/omp-config/global/external/vercel-dogfood/templates/dogfood-report-template.md` — report shape for multi-issue findings; adapt its per-issue block, not its severity words, to the PASS/WARN/FAIL/SKIP vocabulary above.
