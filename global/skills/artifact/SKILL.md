---
name: artifact
description: |
  Produce a consistently-styled, self-contained HTML report served from a local
  static directory. One house template (Silver Age comic-ops palette, dark/light toggle,
  and a mandatory copy-page button) so every report an agent hands the operator
  looks and behaves the same. Use when: "make an HTML artifact/report", "write
  up a brief/report/dashboard as a page", or any time
  you'd otherwise dump a long analysis into chat. Trigger: /artifact.
argument-hint: "[--title <t> --slug <s> --body-file <f>|--html-file <f>]"
---

# /artifact

The operator reads reports as local HTML pages, not as chat walls. This skill is
the single source of truth for how those pages look and what they can do.

## The contract every artifact honors

- **One house style.** The template (CSS + JS) lives inside `scripts/artifact_create.py`
  as `HOUSE_CSS`/`HOUSE_JS` — edit there, every future report inherits it. Don't
  hand-roll a divergent stylesheet.
- **A copy-page button, always.** Every report carries a header "Copy page" button
  that copies the entire rendered document to the clipboard. Baked into the template;
  injected automatically if you pass an already-authored full HTML file.
- **Self-contained.** Inline CSS/JS, no external assets — the copied HTML is a
  complete, portable page.
- **Informational, not decorative.** Tables, callouts, diagrams that carry
  information prose can't. See the aesthetic repo for the deeper design language.

## Information design doctrine

"It's a little bit silly to be leaning into HTML and then still have it be one
long-ass pile of text." An artifact that is a Markdown report in a browser has
missed the medium. Before authoring, ask: **what is the most effective
articulation of THIS information?** — then climb the ladder only as far as the
content earns:

1. **Prose** — for argument and verdicts. Short. Never the whole page.
2. **Structure** — tables for enumerable facts, callouts for rulings, phase
   lanes for sequence, comparison grids for alternatives. Layout IS analysis.
3. **Diagrams & generated images** — when shape carries the meaning (system
   maps, flows, timelines). Use an operator-selected local or external image
   tool when it is available and appropriate; keep the artifact portable and
   never assume a provider, key, or deployment.
4. **Interactive & animated** — drill-downs, toggles, simulations, canvas/
   three.js/WebGL — when the reader needs to *explore* (a graph, a
   before/after, a what-if), not just read. Inline the library or keep it
   dependency-free; the page must stay self-contained.

Guardrails: single-column narrative spine is generally right; a noisy
dense dashboard is as much a failure as the wall of text. Strong visual
hierarchy, restrained color used semantically, progressive disclosure —
the first viewport carries the verdict, depth unfolds below. Tell a story;
every claim links to its evidence (the atlas principle applies to pages too).

## Publication boundary

`artifact_create.py` always writes a local mirror. Remote publication and
deployment belong to an external shelf or operator-owned product; this public
primitive contains no publisher, token lookup, or network mutation. Generated
URLs are restricted to an HTTP loopback origin; `--base-url` is presentation
metadata, not a deployment hook.

## Do it

```bash
S="$ROSTER_ROOT/primitives/skills/artifact/scripts"
# quick: markdown in, styled page out
python3 $S/artifact_create.py --title "Weekly Ops" --slug weekly-ops \
  --tag "Field Memo" --summary "..." --body-file report.md
# rich: author a full HTML page (best for real reports); the copy button is
# injected if you forgot it. Match HOUSE_CSS class names for consistency.
python3 $S/artifact_create.py --title "The Factory" --slug factory \
  --tag "Field Memo" --html-file factory.html
```

The script writes a local mirror (`~/artifacts/public/a/<slug>/index.html`) and
prints its local URL. Use a 1–2 word slug. Start the local static server from
the same artifacts root when the rendered page needs a browser check. Roots,
input files, and output slug directories fail closed on user-owned symlink
components so rendering cannot escape the selected local tree. One held root
descriptor anchors the complete render, registry update, and reindex
transaction; registry enumeration never re-resolves that root pathname. Each
leaf replacement exchanges through a private descriptor-held transaction
directory, so rollback never trusts a public temporary pathname. A failure
after the rename commit point is reported explicitly as
`COMMITTED/DURABILITY_UNKNOWN`, never as an ordinary precommit failure.

## Serving

`scripts/artifact_serve.py` is a portable local static server for
`~/artifacts/public`. The operator owns any external exposure, persistence, and
service manager. Roster does not install, converge, publish, or bridge that
service.

## Extending

Add reusable block styles (cards, timelines, phase lists) to `HOUSE_CSS` when a
report needs them, so the next report can reuse the class. Keep the template one
file; don't fork per-report CSS.
