---
disable-model-invocation: true
name: groom
description: |
  Backlog grooming uses one always-on loop: tidy the board, then sweep.
  Investigate, research, critique, and shape ambitious work. Tidy every run.
  Use when: "groom", "backlog", "what should we build", "prioritize",
  "rethink this", "biggest opportunity", "moonshot", "audit skills",
  "skill quality audit".
  Trigger: /groom, /groom audit, /backlog, /rethink, /moonshot, /scaffold.
argument-hint: "[audit|--emphasis explore|rethink|moonshot|scaffold] [context]"
---

# /groom

Keep the board of record true and make the project more ambitious.
A strategic `/groom` is a mega-sweep, not triage. Cover the project and emit a
vision-led backlog diff. Use prose only to justify that diff.

Use `global/references/interrogate-first.md` for operator judgment. Read the
codebase for facts and keep the investigation autonomous. Use
`global/skills/dispatch/SKILL.md` for native lane routing. Use julius-caveman only
for interim synthesis; keep findings and artifacts in normal English.

## Project Vision

Create, refresh, or validate a durable vision before ranking strategic work.
Read root `VISION.md`. If it is missing or stale, route to `/vision`; when no
vision exists, emit the smallest durable artifact, preferring root `VISION.md`.
Use `docs/product.md`, a roadmap, or a named backlog epic only when evidence
rejects root vision. Do not defer that emission.

Name the audience, job-to-be-done, category, standards, non-goals, bets, and
excellent 6-12 month outcome. Revise the artifact when evidence contradicts it.
Record direction changes in the artifact, not only chat or issue comments.
Backchain each theme and ticket to what the vision advances, de-risks,
simplifies, or rejects. Use `global/references/image-generation.md` for a system
map when prose cannot show relationships or sequence.

## Tidy (mandatory)

Use Powder cards as the board of record, not stale files. Follow the Shared
Operating Spine durable-state and closeout rules. Read the card store. Close
cards only through `update_status` or `complete_card`; carry shipping evidence.
Powder audits actor, time, and change.

- Close merged work as done or shipped.
- Surface `in_progress` cards when branches merge or disappear, or when cards
  have no changes for 30+ days. Never flip them silently.
- Propose duplicate consolidation. Never merge duplicates silently.
- Treat backlog size as telemetry, not policy. Report count, age, duplicates,
  stale owners, orphaned themes, and unfocused small items.
- Consolidate only tickets with one outcome. Never veto evidenced work by count.

Do not use repository-local ticket directories. Use Powder in ordinary Misty
Step repositories and Habitat in R90 repositories. Preserve legacy ticket
contents in the routed work plane, verify live readback, and remove the tree
before grooming.

## Mega Sweep

Load `references/mega-groom.md` for the strategic swarm, coverage map, source
matrix, evidence, output, and emission contract. Use
`references/investigation-bench.md` only for lane prompts. If delegation is
unavailable, label the run degraded and execute the matrix locally. Use
`/research` when outside knowledge can change a verdict.

## Ambition Floor

Calibrate scope to frontier-agent execution, not human staffing. Describe the
best whole project, then backchain into epics, deletions, sequencing, and first
pickups. Compose repo-specific perspectives; invert premises, borrow from
adjacent domains, and ask what competitors, operators, and new users notice.
Run fresh independent lanes in parallel. If findings remain obvious, run a
second independent lane with inverted premises and adjacent-domain analogies.

Describe software that is elegant, changeable, personalizable, delightful,
operationally boring, and valuable. Treat the gap to that target as backlog.
Emit epics by default with ordered children. Keep small items under an epic or
as isolated fixes. Vet every epic premise with evidence; an "all fine" report is
a claim, not proof.

## Judgment

Investigate before opinions. Run tidy-only only when requested; otherwise run
the mega sweep. Read live code, hotspots, debt, and the oldest stuck card.
Challenge premises, reframe symptoms toward causes, and propose deletions with
rationale.

Audit harness readiness as backlog work. Check verification routes, cold-agent
build/test/lint discovery, deployed runbooks, enforced quality and security
gates, including secret leaks in files and Git/PR metadata before publication.
Check stale AGENTS/CLAUDE prose and missing product context. Use
`global/references/quality-gates.md` and
`global/references/verification-system-first.md` for shared contracts.

Group findings by root cause, rank impact after confidence, and recommend one
action per theme. Use the shared proof contract to vet findings against live
evidence. Use the interrogate-first reference for contestable plans, one branch
at a time.


## Shape the Board

Shaping belongs in grooming. A one-card request still requires its board,
dependencies, competing priorities, and vision.
Before promotion, require the outcome over the mechanism and live anchors.
Record rejected alternatives, scope, non-goals, and invariants.
Define an executable oracle and falsifier.
Record cold-start dependencies, acceptance, and stop conditions.
Preserve the premise with a source or waiver and residual risk.

Use `references/prd-ticket-quality.md` for M+ work,
`references/executable-oracles.md` for disputed proof,
`references/cli-design.md` for command-line surfaces,
`references/voice-transcript-metadata.md` for voice premises, and
`references/ticket-format.md` for card shape and promotion rules.

Emit a board-level packet with vision, themes, chosen and rejected directions,
ordered epics, dependencies, oracles, risks, and the first pickup. Do not hide
nearby work in an isolated context packet. Every card carries Goal and Oracle;
add a Verification System to M+ or ready work.

## Audit Mode

`/groom audit` is a read-only harness-health report, not grooming. Read skill and
prompt usage, hook and native invocation logs, session evidence, and edit age.
Explain high value when usage is low. Treat low usage without demonstrated value
as a deletion candidate. Order findings by severity. Do not auto-fix. This repo
has no semantic telemetry engine.

## Refuse

- Never auto-delete or silently merge cards.
- Never archive a card whose trailer points to an unmerged branch.
- Never let backlog size alone veto evidenced work.
- Run the strategic swarm when subagents, peer CLIs, or sprite lanes exist.
  Report degraded mode and run locally when delegation is blocked.

## Completion Gate

Use `global/references/verification-system-first.md` for shared proof. Add:

1. **Tidy diff:** archive, status-change, and flag items by ID; add no padding.
2. **Source matrix:** lanes, local commands, external research, skipped or
   failed lanes, and each contribution.
3. **World-class plan:** vision, gaps, themes, sequence, deletions or
   consolidation, and one best next pickup.
4. **Emissions:** edit epics or tickets with `**Why:**` naming the evidence
   lane; cover the domain map, not only the easiest implementation slice.
5. **Residual:** open questions, blocked dependencies, unverified areas, and
   what would strengthen the sweep.

Apply non-destructive edits when requested. Keep deletions, abandonments, and
silent merges as proposals until explicit approval. End with a clean tree after
archives and emissions commit; deletions await ratification.
