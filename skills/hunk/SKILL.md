---
name: hunk
description: Terminal diff viewer and live review session controller. Use to view diffs, navigate changesets, attach inline review annotations, and drive interactive reviews in dedicated Herdr tabs or panes.
---

# Hunk

Hunk is an interactive terminal diff viewer built on OpenTUI. It displays
multi-file review streams with split or stacked layouts, syntax highlighting,
and inline review annotations.

## Core Commands

### Inspect changesets

```bash
hunk diff [target] [-- <pathspec...>]   # Working tree diff
hunk diff --staged                      # Staged changes diff
hunk diff <left> <right>                # File-to-file diff
hunk show [commit-sha]                  # Commit diff
hunk patch [file | -]                   # Unified diff from file or stdin
```

### Readable long lines

Use wrapping by default for walkthroughs and full-file reviews:

```bash
hunk diff [target] --wrap
hunk show HEAD --wrap
```

`--wrap` renders long diff lines on continuation rows without changing their
logical old/new line targets. `--no-wrap` truncates each diff line to one
terminal row. Prefer `--no-wrap` only when horizontal density is intentional.

### Sidecar annotations

Launch Hunk with pre-loaded agent review notes:

```bash
hunk diff --wrap --agent-context /tmp/notes.json --agent-notes
hunk show HEAD --wrap --agent-context /tmp/notes.json --agent-notes
```

Sidecar JSON schema:

```json
{
  "comments": [
    {
      "filePath": "src/index.ts",
      "newLine": 42,
      "summary": "Short description of the note",
      "rationale": "Detailed explanation, context, or trade-off."
    }
  ]
}
```

Target line accepts either `newLine` or `oldLine` and must be a changed line
covered by a diff hunk; unchanged context lines are rejected.

## Walkthrough (required)

Opening Hunk is not a walkthrough. A walkthrough is a numbered tour of
inline notes the operator can step with next/prev comment.

MUST:

- Write the sidecar **before** launching Hunk. Include a tour of the
  change, not only review findings.
- One note per load-bearing decision: owner, interface, each migrated
  caller cluster, proof, then findings. Typical floor: every file with
  a behavior change, plus tests that define the contract. Two notes on
  a 20-file diff is a failed walkthrough.
- Order notes as a tour (`1/N …`). Start on the owner, not an incidental
  first file in `git` order.
- Quote the entire Hunk argv for `herdr pane run`. Unquoted `--wrap` and
  `--agent-context` are parsed by Herdr and never reach Hunk:
  ```bash
  herdr pane run <ROOT_PANE_ID> \
    "hunk show HEAD --wrap --agent-context /tmp/notes.json --agent-notes"
  ```
- After launch, `hunk session get --repo .` MUST show `liveCommentCount` > 0.
  If it is 0, apply the sidecar immediately (`comment apply --stdin`) and
  do not tell the operator the walkthrough is open.
- `hunk session navigate --repo . --next-comment` (or `--file` + `--new-line`
  of note `1/N`) so the viewport is on the first note, not an unannotated
  file at the top of the changeset.

Do not annotate every test-fixture line. Annotate decisions, migrations,
and findings the operator should stop on.


## Live Session Control (`hunk session`)

When Hunk runs in a terminal, it connects to a local loopback daemon. Agents
can query, steer, and annotate the live session without restarting the viewer.

### 1. Discover sessions

```bash
hunk session list                       # List all active sessions
hunk session get --repo .               # Match session by repository root
hunk session context --repo .           # Read current focus and viewport state
```

### 2. Inspect review structure

```bash
hunk session review --repo . --json     # File and hunk hierarchy (no raw diffs)
hunk session review --repo . --include-patch --json  # Include raw patch text
```

### 3. Navigate the viewport

```bash
hunk session navigate --repo . --file <path> --hunk <n>      # Jump to hunk (1-based)
hunk session navigate --repo . --file <path> --new-line <n>  # Jump to new line
hunk session navigate --repo . --file <path> --old-line <n>  # Jump to old line
hunk session navigate --repo . --next-comment                # Jump to next note
hunk session navigate --repo . --prev-comment                # Jump to previous note
```

### 4. Add or clear inline notes

```bash
# Add single note
hunk session comment add --repo . --file <path> --new-line <n> --summary "<text>" [--rationale "<text>"] [--focus]

# Apply batch notes over stdin
cat /tmp/notes.json | hunk session comment apply --repo . --stdin [--focus]

# List active notes
hunk session comment list --repo .

# Clear notes (agent notes only; preserves human notes)
hunk session comment rm --repo . <comment-id>
hunk session comment clear --repo . --file <path> --yes
hunk session comment clear --repo . --yes

# Clear all notes (destructively removes human 'c' notes too)
hunk session comment clear --repo . --all --yes

### 5. Reload session contents

```bash
hunk session reload --repo . -- diff --wrap
hunk session reload --repo . -- show HEAD~1 --wrap
```

Reloading retains live comments. Include `--wrap` when an existing session was
launched without it.

## Herdr Integration

When running inside Herdr (`HERDR_ENV=1`), prefer a dedicated review tab. A
full-width tab keeps diffs and annotations readable and isolates the review
from the coding conversation.

1. **Create a dedicated review tab without changing operator focus**:
   ```bash
   herdr tab create \
     --workspace "$HERDR_WORKSPACE_ID" \
     --cwd "$PWD" \
     --label "hunk: <topic>" \
     --no-focus
   ```
   Read the tab ID and root pane ID from `.result.tab.tab_id` and
   `.result.root_pane.pane_id`; never predict them.

2. **Launch wrapped Hunk in the tab's root pane**. Quote the entire
   Hunk argv. Unquoted `--wrap` / `--agent-context` are eaten by Herdr:
   ```bash
   herdr pane run <ROOT_PANE_ID> \
     "hunk show HEAD --wrap --agent-context /tmp/notes.json --agent-notes"
   ```
   Then `hunk session get --repo .`. If `liveCommentCount` is 0, apply
   the sidecar and navigate to note `1/N`. Do not stop on the first
   unannotated file.


3. **Use a same-tab split only when side-by-side context is the point**, the
   diff is small, or the operator explicitly requests it:
   ```bash
   herdr pane split --current --direction right --cwd "$PWD" --no-focus
   ```
   Read `.result.pane.pane_id`, then launch Hunk with `--wrap` in that pane.

4. **Retain the review surface during the walkthrough.** Report the workspace,
   tab, pane, and Hunk session IDs. Confirm that operator focus stayed
   unchanged. When the review is finished, inspect focus: close the created
   tab or pane only while it remains unfocused; if the operator focused it,
   leave it open and report it.
   ```bash
   herdr tab close <TAB_ID>
   # or, for the split fallback:
   herdr pane close <PANE_ID>
   ```
