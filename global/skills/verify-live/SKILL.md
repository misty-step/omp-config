---
disable-model-invocation: true
name: verify-live
description: |
  Verify live behavior: drive a real browser and real entrypoints, prove that a
  change works or fails, and return PASS/WARN/FAIL/SKIP evidence. Use the ladder
  of the builtin browser tool, the agent-browser CLI, and the chrome-devtools
  CLI. Use when asked to verify, QA, smoke-test, or reproduce a rendered
  surface, golden path, performance, or console/network behavior against a
  running app.
  Trigger: /verify-live.
---

# /verify-live

Reproduce the claimed behavior through the real user-facing surface before you
trust it. "Tests pass" is not verification. Exercise the exact contract named
in the claim. Capture the command, screenshot, snapshot, or log that shows it.
Never repair the artifact under verification: make no edits, writes, commits,
or tracker mutations. State what you exercised and what you did not as clearly
as the verdict itself.

## Escalation ladder

Three tiers exist, from cheapest to most expensive. Never use a higher tier when
a lower tier settles the job. Each higher tier costs more tokens or setup.

**Tier 1 — builtin `browser` tool.** This tier has zero standing cost and is
already loaded. It uses Puppeteer: `tab.observe()`, `tab.ariaSnapshot()`,
`tab.screenshot`, `tab.evaluate`, CSS and
`aria/`/`text/`/`xpath/`/`pierce/` selectors. Playwright-only pseudo-selectors
(`:has-text()`, `:visible`) are rejected. Use `aria/<role>` or
`text/<substring>` instead. This tier is the default for "does the golden path
still work" and "did this render."

**Tier 2 — `agent-browser` CLI via `bash`**
(`/Users/phaedrus/.npm-global/bin/agent-browser`, v0.31.1). Use it only when
tier 1 cannot do the job: isolated console capture, uncaught-error isolation,
network request lists and HAR export, snapshot or screenshot diffing against a
saved baseline, Core Web Vitals, video recording of an interactive repro, and
auth/session persistence across commands. Run
`agent-browser skills get core` before your first command in a session. The
installed binary serves and updates this usage guide on upgrade, so this skill
does not hardcode its full grammar. Add `--full` for the complete command
reference when core is not enough.

**Tier 3 — `chrome-devtools` CLI via `bash`**
(`/Users/phaedrus/.bun/bin/chrome-devtools`, v1.6.0). Use it only for
Lighthouse-scored audits, performance trace-insight analysis, and heap
snapshots. Tier 1 and tier 2 do not cover these jobs. These jobs cost many
tokens. Always pass an output or file path (`--outputDirPath`, `--filePath`) so
the heavy payload lands on disk. Then read only the summary you need. The
`chrome-devtools` MCP server is defined in `global/mcp.json` but remains in
`disabledServers` and stays disabled. Running ~36 always-on tool schemas adds
context load that the CLI avoids. Google and Microsoft now recommend
CLI-plus-skills over always-on MCP for coding agents for this exact reason. Do
not re-enable it.

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

- Reproduce before reporting. Verify that the issue repeats at least once before
  recording it as a finding. A single unreplicated glitch is not evidence.
- Document each issue immediately during exploration. Do not tour the whole
  surface first. A session interruption must not cost you a finding.
- For interactive or state-dependent issues, record video and step-by-step
  screenshots. Run `agent-browser record start <path>` before the repro, take
  one screenshot per step, and run `record stop` after the broken state appears.
- For static issues visible on load, take exactly one annotated screenshot:
  `tab.screenshot()` or `agent-browser screenshot --annotate <path>`. Do not
  record video.
- Never delete evidence during the session. Do not `rm` a screenshot, video, or
  log because it seems benign. Note that you checked it and continue.

## Verdicts

Report `PASS`, `WARN`, `FAIL`, or `SKIP` per checked surface:

- **PASS** — the exact command or interaction ran and the observed result matches the claim.
- **WARN** — the surface works but shows a real, named problem that does not invalidate the claim.
- **FAIL** — the observed result contradicts the claim. Name the exact mismatch.
- **SKIP** — the surface could not be exercised (missing credentials, unreachable environment, no driver). Name the blocker; never silently omit a claimed surface.

Name the exact command and observed result for every verdict. Use a snapshot
excerpt, screenshot path, status code, or console line. A green aggregate across
verdicts is necessary but not sufficient. One FAIL on the actual claim outweighs
ten unrelated PASSes.

## Hard prohibitions

- Never repair the artifact under verification. Report the break; do not patch it.
- Never weaken a gate, threshold, or oracle to create a pass.
- Never claim verification without naming the exact tool call and observed output.
- Never assert rendered behavior without an actual render. Do not infer visual
  correctness from source code.

## Session hygiene

Create the evidence output directory before you start:
(`mkdir -p <out>/screenshots <out>/videos`). This prevents a missing path from
causing a race during the session. Close every session that you opened before
you finish. Run `agent-browser close --all` for CLI sessions, and close browser
tabs opened through the builtin tool. If you used tier 3, run
`chrome-devtools stop` when the audit ends.

## Reference material (read on demand, not autoloaded)

These files live under `global/external/`, which is not projected into the live
skills directory. Read them directly by absolute path when the job needs more
depth than this file carries:

- `/Users/phaedrus/Development/omp-config/global/external/vercel-agent-browser/SKILL.md` — agent-browser discovery stub; the authoritative grammar is `agent-browser skills get core`, not this file.
- `/Users/phaedrus/Development/omp-config/global/external/vercel-dogfood/SKILL.md` — full exploratory-QA workflow this ladder condenses.
- `/Users/phaedrus/Development/omp-config/global/external/vercel-dogfood/references/issue-taxonomy.md` — severity/category taxonomy and exploration checklist for open-ended bug hunts.
- `/Users/phaedrus/Development/omp-config/global/external/vercel-dogfood/templates/dogfood-report-template.md` — report shape for multi-issue findings; adapt its per-issue block, not its severity words, to the PASS/WARN/FAIL/SKIP vocabulary above.
