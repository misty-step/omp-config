# The black box

Every session writes its own handoff as a side effect: the transcript on
disk, the working tree, the claimed card and its work log, commits, receipts.
None of it cost the writer a token, none of it required foresight — which is
why it survives the deaths that matter: usage-limit exhaustion, crashes,
kills mid-turn. The successor pays the reconstruction cost at its own rates.
The black box IS the handoff artifact; an explicit one (handoff notes, a lane
report) is a bonus when present, never a precondition.

## Reading order (cheap → expensive)

Stop as soon as you can state: what was in flight, what was proven, what the
next edit was going to be.

1. **Board card + work log.** The claimed card carries intent, acceptance
   criteria with check state, comments, and — where the repo uses it —
   high-frequency work-log entries. Cheapest read, highest intent density.
2. **Git.** `git status`, `git diff`, branch, `git log` on the branch. The
   uncommitted diff is the truest statement of where work physically
   stopped. When the diff and the card disagree, trust the diff and note the
   discrepancy in your report.
3. **Explicit receipts, if present.** Lane reports, `handoff.json`, receipt
   paths named in the card, scratchpad evidence directories.
4. **Transcript tail.** The most expensive read; go here for the *why* —
   decisions, dead ends already explored, constraints the predecessor
   discovered. Read the tail first (last ~100 lines), widen only if intent
   is still unclear.

## Where transcripts live (verify at read time — locations drift)

Prefer semantic search when a qmd index is available: the
`claude-code-transcripts` and `codex-sessions` collections already index
session history (`qmd query "<topic>" -c claude-code-transcripts`).
Direct locations:

- **Claude Code** — `~/.claude/projects/<cwd-slug>/*.jsonl`, where the slug
  is the workspace path with `/` → `-` (e.g. `-Users-x-Development-repo`).
  Newest file = most recent session. JSONL: filter for `"role":"user"` /
  `"role":"assistant"` messages; tool results are bulky, skim them.
- **Codex CLI** — `~/.codex/sessions/` (rollout JSONL, dated).
- **opencode** — `~/.local/share/opencode/` (per-project storage).
- **goose** — `~/.local/share/goose/sessions/`.
- **pi / omp / others** — check the harness config dir (`~/.pi/`, `~/.omp/`)
  or its docs; if the location isn't obvious in one look, proceed on card +
  git alone and say the transcript went unread.

## Report the seam honestly

The reconstruction is a claim like any other: name which black-box surfaces
you read and which you skipped. Mid-turn reasoning that was never
externalized is genuinely gone — where the trail ends, say so rather than
smoothing over it, and let the routed skill re-derive.
