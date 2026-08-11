---
disable-model-invocation: true
name: groom
description: |
  Product direction and backlog in one loop: keep VISION.md true, tidy Issues,
  then sweep and shape work. Use when: "groom", "vision", "backlog", "roadmap",
  "north star", "what should we build", "prioritize", "rethink this",
  "moonshot", "audit skills". Trigger: /groom, /vision, /backlog, /north-star,
  /rethink, /moonshot.
argument-hint: "[vision|tidy|audit|moonshot] [context]"
---

# /groom

Own product direction and the board together.
Keep root `VISION.md` true. Keep the repository's Issue backlog true. Shape ambitious work from both.
Do not maintain a separate roadmap skill or `ROADMAP.html` app.
Sequence and proof live on GitHub Issues under the vision.

Use `global/references/interrogate-first.md` for operator judgment.
Read the codebase for facts. Use `skill://dispatch` for native lanes.
Use julius-caveman only for interim synthesis; keep artifacts in normal English.

## Modes

| Mode | When | Work |
|---|---|---|
| default | strategic groom | vision check → tidy → mega sweep → shape board |
| `vision` | only north-star work | create or refresh root `VISION.md` and wire consumers |
| `tidy` | board hygiene only | Issue tidy; no mega sweep |
| `audit` | harness-health report | read-only skill/prompt usage and staleness; no board edits |
| `moonshot` | ambition emphasis | default loop with harder ambition floor and deletion pressure |

## Vision (always before strategic rank)

1. Read root `VISION.md`. Create or refresh it when missing or stale.
2. Interrogate the operator when intent is unclear. Batch decisions.
3. Read live repo facts: README, AGENTS, product docs, demos, tests, backlog.
4. Write a short north star: intent, audience, category, standards, non-goals,
   bets, and excellent outcomes. No required house template.
5. Wire consumers with pointers to `VISION.md`. Never copy vision prose into
   AGENTS or skills.
6. Load `references/vision-quality.md` when drafting or reviewing the artifact.
7. Backchain every theme and card to what the vision advances, de-risks,
   simplifies, or rejects.

Verification when vision changes:

```sh
test -f VISION.md
rg -n "VISION\.md" AGENTS.md .agents skills 2>/dev/null || true
```

## Tidy (mandatory on default and tidy modes)

GitHub Issues is the board of record for Misty Step. Follow durable-state and closeout rules.

- Close merged work as done or shipped with shipping evidence.
- Surface stale open issues (merged branch gone or 30+ days idle).
- Propose duplicate consolidation. Never merge silently.
- Report backlog telemetry: count, age, orphans, unfocused small items.
- Use GitHub Issues in Misty Step repos and Habitat in R90 repos.
  Remove legacy ticket directories only after live ledger readback.

## Mega Sweep (default mode)

Load `references/mega-groom.md` for the swarm, coverage map, and emission
contract. Use `references/investigation-bench.md` only for lane prompts.
If delegation is unavailable, label the run degraded and run locally.
Use `/research` when outside knowledge can change a verdict.

## Ambition Floor

Calibrate to frontier-agent execution, not human staffing.
Describe the best whole project, then backchain into epics, deletions,
sequence, and first pickups.
Run fresh independent lanes in parallel.
If findings stay obvious, run a second lane with inverted premises.

Emit epics with ordered children. Keep small items under an epic or as
isolated fixes. "All fine" without evidence is a claim, not proof.

## Shape the Board

Before promotion require outcome over mechanism, live anchors, rejected
alternatives, scope, non-goals, invariants, oracle, and falsifier.
Use `references/prd-ticket-quality.md`, `references/executable-oracles.md`,
`references/cli-design.md`, `references/voice-transcript-metadata.md`, and
`references/ticket-format.md` when those surfaces apply.

Every card carries Goal and Oracle.
Add a Verification System to M+ or ready work.
Sequence lives on the board under vision — not in a parallel roadmap app.

## Audit Mode

`/groom audit` is read-only harness health.
Explain high value when usage is low.
Treat low usage without value as a deletion candidate.
Do not auto-fix.

## Refuse

- Never auto-delete or silently merge cards.
- Never archive a card whose trailer points to an unmerged branch.
- Never let backlog size alone veto evidenced work.
- Never invent a second durable direction store beside `VISION.md` and GitHub Issues.

## Completion Gate

Use `global/references/verification-system-first.md`. Report:

1. Vision path and whether it changed.
2. Tidy diff by card id.
3. Source matrix for the sweep (or `tidy-only` / `vision-only`).
4. Board emissions with evidence links.
5. Residual risks and open operator questions.
