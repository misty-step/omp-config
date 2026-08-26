---
name: exocortex
description: Read, search, write, and lint registered knowledge cortices (daybook first) via the exocortex CLI — use when orienting before work or writing durable results back to fleet memory.
---

# Exocortex

Exocortex is the fleet memory kernel: one binary over registered knowledge
corpora (**cortices**). Daybook is cortex `daybook`. Foreign sources (Notion,
Drive, harness session logs) enter through **feeds** as provenance-stamped
notes — never by editing raw sources.

Status: Exocortex is built, tested under race detection, and installed as
`~/.local/bin/exocortex`. The CLI is the official, universal fleet interface.
All operations speak structured JSON (`--json` default) and evaluate against
an isolated, kernel-owned publisher clone. **Never edit or commit to Daybook
via raw Git directly**; always use `exocortex note` or `exocortex put` to protect
CAS preconditions and keep working trees clean.
## When to use

- **Before work (orient):** search the cortex for prior decisions, project
  context, and recurring patterns instead of inferring from memory.
- **After work (write-back):** durable decisions, corrected facts, and
  reusable syntheses go into the cortex; raw session logs stay on disk.

```sh
exocortex brief "powder"                                  # single-call orientation briefing
exocortex search "who owns powder credentials"            # omitted mode is hybrid (BM25 + Qwen rerank; BM25 fallback)
exocortex search "claim procedure" --mode bm25 --type decision  # deterministic BM25; memo uses journal_prefix
exocortex get areas/work-philosophy.md                    # read note from committed HEAD snapshot
exocortex note "decision or bug fix"                     # atomic memo to the daily board (~2s)
exocortex put misty-step/new-decision.md --from draft.md              # create-only: fails if it exists
exocortex put misty-step/decision.md --from draft.md --expects <sha>  # update: stored-revision hash REQUIRED
exocortex log misty-step/new-decision.md                # git lineage
exocortex lint misty-step/new-decision.md               # frontmatter floor gate
exocortex sync [--cortex <name>]                     # refresh QMD index + embeddings after writes
exocortex status [--cortex <name>]                   # dirty markers, last synced commit, last error
```

## Write often, write small

The journal (`note`) exists so capturing costs seconds: status updates,
non-obvious things that bit you and how you fixed them, decisions in
flight, facts a future agent would thank you for. One line each; the file
naming makes collisions impossible, so just write. Full wiki notes remain
the home for durable, linked decisions.

If you are a SUBAGENT: do not run `note` or `put` against memory — you
cannot judge what the fleet already knows, and duplicates erode trust.
Report back to your parent instead.


Write rules enforced by `put` (do not pre-satisfy by hand):

- Frontmatter: the cortex's validation profile decides. Daybook cortex
  follows the `/wiki` floor — parseable YAML with non-empty `type` required;
  `description` strongly recommended; everything else warned, never failed.
  `created` is immutable — an update that changes or drops it fails
  `created_immutable` (resubmit with the stored value); unknown keys and
  `type` values are tolerated.
- Provenance stamped automatically (agent, time, source); never fake it.
- Payload and destination are separate: `--from <file|->` supplies the
  content; `<path>` is where it lands in the cortex. Concurrency is
  structural: bare `put` creates only — on ANY existing path it fails
  `exists` with a hint; updating REQUIRES `--expects <sha>` naming the
  STORED revision (`get` reports it). A stale or malformed hash fails
  `revision_conflict`. There is no way to overwrite without the hash.
  On mismatch, re-read with `get`, re-apply your change on top, retry.
  Never overwrite a conflict.

## Sole-Publisher Isolation

For Daybook cortices, the kernel manages its own persistent clone under
`~/.config/exocortex/writers/<cortex>`. Writes land, commit, and push from
there; `get` reads the committed Git HEAD snapshot. Registered human checkouts
are never preflighted, stashed, or mutated by the kernel. Failures fail closed
with structured data conflicts.
## Naming and linking

Notes are claims, not topics ("distribution is the moat", not "thoughts on
distribution"). Link densely with full paths
(`[[misty-step/exocortex-kernel]]`). Full conventions: the `/wiki` skill.
