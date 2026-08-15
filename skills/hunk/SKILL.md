---
name: hunk
description: Terminal diff viewer and live review session controller. Use to view diffs, navigate changesets, attach inline review annotations, and drive interactive reviews in Herdr panes.
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

### Sidecar annotations

Launch Hunk with pre-loaded agent review notes:

```bash
hunk diff --agent-context /tmp/notes.json
hunk show HEAD --agent-context /tmp/notes.json
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

Target line accepts either `newLine` or `oldLine`.

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
hunk session reload --repo . -- diff
hunk session reload --repo . -- show HEAD~1
```

## Herdr Integration

When running inside Herdr (`HERDR_ENV=1`):

1. **Split a pane beside the active session**:
   ```bash
   herdr pane split --current --direction right --no-focus
   ```
   Or create a dedicated review tab:
   ```bash
   herdr tab create --label "hunk: <topic>"
   ```

2. **Launch Hunk inside the pane**:
   ```bash
   herdr pane run <PANE_ID> hunk diff [target] [--agent-context /tmp/notes.json]
   ```

3. **Close the pane when finished**:
   ```bash
   herdr pane close <PANE_ID>
   ```
