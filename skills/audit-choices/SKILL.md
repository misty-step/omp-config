---
name: audit-choices
description: Audit the choices an implementer made, not its diff — a pure decision audit that traces the session's history into a choices ledger, changes no code, and never blocks. Working code embeds architecture the operator never chose; surface it because future work inherits it. Use before merging or committing AI-implemented work, when integrating a delegated subagent's pass, or when a fix "works" but might be a point fix.
disable-model-invocation: true
license: MIT; from dzhng/skills audit-choices
---

# Audit Choices

Given a good decision, an agent implements it faithfully; wherever the task is
underspecified, it makes the decision itself — silently, and the diff won't
flag it. Reviewing thousands of changed lines doesn't scale, and it inspects
the execution, which was probably fine. The audit that scales is of the
**choices**: surface every decision the implementer made on its own, judge
that list, and record the verdicts.

This is about architecture more than bugs. An implementation can work
perfectly and still rest on decisions the operator never made — a data shape,
a storage location, a dependency, an API contract, a tradeoff of memory for
speed, what the code may read, write, print, or exfiltrate — and every one of
them is load-bearing for future work. The operator needs to know them not
because they're wrong, but because they now own them.

Purely a decision audit: it changes no code and can be called at any time.
Trace back — walk every step this session took and every step each subagent
took (a live implementer traces its own; otherwise reconstruct from reports,
transcripts, and diffs) — and surface every decision made on the operator's
behalf that was not in the original spec or prompt. Acting on verdicts belongs
to the caller: the implementing workflow mid-run, or the operator after
reading the report.

Two ways in, same audit:

- **Called by a workflow** (per pass or per slice): audit that pass, append
  its entries to the ledger, and return; the workflow presents the
  accumulated ledger when it hands back.
- **Called directly by the operator**: audit the whole body of work in front
  of you (session, branch, or named change) and present the report
  immediately. Recommend; change nothing.

## Workflow

1. **Elicit and trace back.** When an implementer reports done, ask: *"While
   working on this, which choices did you make that you're not confident of?
   List all."* — but treat the self-report as a starting point, not the
   boundary: agents under-report. Trace the history yourself and collect
   every decision in the work but not in the original spec or prompt. Sweep
   the architectural categories, not just the suspect fixes: data shapes and
   formats, storage and naming schemes, API contracts and their error
   behavior, dependencies added, concurrency/perf tradeoffs, scope
   interpretations, patterns future code will imitate — and the **attack
   surface**: what the work may read, write, print, or exfiltrate, including
   credentials, environment, and network reach. Choices the plan explicitly
   delegated to the implementer are discretion, not audit items.
2. **Triage each choice on evidence.** Forced by the plan, or invented?
   Invented ones get the scrutiny: is this the general solution, or a fix
   shaped to the one failing case? Verdict per choice: **sound**,
   **unsound**, or **needs-user** — plus a **confidence**: how sure the audit
   is that the operator would have made this same call. Confidence ranks the
   report. Reserve needs-user for genuinely operator-only calls (taste,
   product direction, external cost); every needs-user entry records a
   recommended call and its reversal path, and the caller stops on it — a run
   does not proceed past a needs-user verdict without the operator. Reversible
   two-way-door choices that are not human-owned may proceed provisionally
   under TH-03, logged in the ledger. The audit itself never stalls: it
   reports and hands back.
3. **State the corrected decision, don't sketch a patch.** For each unsound
   choice, name the decision the work should be redone from — the property
   that must hold in general — not an edit to layer on top.
4. **Bank every choice in the ledger** (below), and promote load-bearing
   sound ones into the plan's handoff so later passes inherit them as givens.
5. **Present the ledger: grouped by verdict, ranked by confidence.** Each
   verdict group maps to an action — needs-user (decide, with the provisional
   calls), unsound (redo, with the corrected decisions), sound (acknowledge:
   the architecture the operator now owns) — ranked least confident first
   within each group. When the ledger is long, open with the two or three
   least-confident choices overall: the "review these first" line. Sound is
   not skippable; only trivial discretion compresses to a one-line count.

## Entry format

Every entry stands alone — the reader didn't live the session. No diff, no
spec, no transcript, no labels the work invented:

- **When** — pass or commit it landed in.
- **The choice** — one-line headline, then the walked scenario: the
  triggering event, what the work does today, what the unbuilt alternative
  would do. Define every term of art at first use. For choices about control
  flow, ordering, or timing, include pseudocode at the level of the decision
  — the conditions and their order, not real signatures.
- **The gap** — what the plan left unspecified that forced it.
- **The reach** — what future work this decision constrains or enables.
- **Attack surface** — what this piece may read, write, print, or exfiltrate,
  and what changed about that surface. "None" is a claim; state it.
- **Verdict** — sound / unsound / needs-user, one-line why. For unsound: the
  corrected decision. For needs-user: the provisional call and how to reverse
  it.
- **Confidence** — low / medium / high that the operator would have made the
  same call. Ranks the report, ascending.

A compressed entry that makes the operator ask "explain this one" has failed.
When entries are consolidated or re-audited, each surviving entry keeps or
regains its full scenario — a rewrite that shrinks entries to headlines has
failed even if every fact survives.

## The Choices Ledger

A dedicated file that outlives every pass, beside the work it audits: the
ticket's spec for a single ticket, `specs/<feature>/choices.md` when a spec
ladder owns the work. Rules:

- **Banked is settled:** a choice already in the ledger is a given for later
  passes — never re-listed, never re-decided.
- **The ledger is a plan-quality signal.** Entries clustering around one area
  mean the plan is foggy there — route that part back through
  `/explore-unknowns` rather than triaging the same class of choice forever.
- **Consolidation at close:** when the work ships, re-audit every banked
  choice against the final shipped code, collapse provisional verdicts to
  their actual end state, drop what later passes superseded, merge
  duplicates. Present the consolidated ledger, never the raw append.

## Rules

- **"It works" is not a verdict on the choice.** The recurring smell is the
  coincidental fix: a resized buffer, bumped timeout, or special case whose
  magnitude happens to cover the failing input. Ask what property
  *guarantees* the fix in general; if the answer is "this case passes," the
  choice is unsound even though the code is green.
- **Declared success is the point of maximum risk.** Never skip the audit
  because the result looks clean.
- **An empty list on nontrivial work is a red flag, not a pass.** Something
  filled the gaps the task left open.
- **Independence.** Run the auditor as a fresh subagent that did not
  implement; prefer a different model family or a non-frontier model than the
  implementer's, per SE-05 routing within OR-07 limits. A model reviewing its
  own intent rationalizes.
- The audit changes no code, tests, or build state. Evidence-gathering is
  fair game — read anything, run existing tests, write transient probes —
  but remove every probe before handback.

## Done

Every invented choice in the pass has a ledger entry with a verdict; every
unsound entry names the corrected decision to redo from; every needs-user
entry carries a reversible provisional call; the ledger has been presented —
grouped by verdict, least-confident first, every entry standing alone — to
whoever acts next; and the tree is exactly as audited. A handback that shows
the diff instead of the choices, or a "fix" applied during the audit, is not
done.
