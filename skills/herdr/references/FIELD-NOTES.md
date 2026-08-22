# Herdr Field Notes

Observed during an exe.dev Habitat workflow on 2026-08-15.

## What worked

- `--no-focus` preserved the operator's tab.
- Creation commands returned stable workspace, tab, and pane IDs.
- JSON results made later commands safe.
- `pane run` and `pane read` kept remote work visible.
- Separate panes isolated the agent, server, database, and SSH tunnel.

## Friction

### Output waits

`pane wait-output` searches the current terminal buffer first. It can match:

- old output from an earlier command;
- the echoed command instead of its result;
- a stale readiness line from an earlier service start.

A timeout does not prove process failure. PTY progress output can complete without a successful match. After every timeout, read the pane before any restart or recovery action.

Prefer a unique result line that is not present in the submitted command. This is not always possible because the shell echoes input.

### Remote process state

A process behind SSH appears to Herdr as `ssh`. Herdr cannot identify the remote child process. It cannot classify remote Shelley, Next.js, Supabase, or tunnel state without a reporting bridge.

Use independent probes for remote readiness:

- an HTTP status request;
- a port check;
- the remote service client;
- a process query on the VM.

### Long output

Long JSON lines and alternate-screen output can hide the useful result. If increasing `--lines` does not help, request a file artifact and read that file.

### Help exit status

Bare command-group help can print valid usage and still exit with status `2`. Do not treat the status alone as a command failure when the intent was discovery.

## Remote workflow

1. Confirm `HERDR_ENV=1`.
2. Record the current workspace, tab, and pane IDs.
3. Create the requested tab with `--no-focus`.
4. Split panes with explicit IDs and `--no-focus`.
5. Open SSH in a pane.
6. Wait for the exact remote shell prompt.
7. Run one long-lived process per pane.
8. Verify each process through its real interface.
9. Report all pane IDs, retained processes, and focus state.

Do not create a workspace when the operator asked for tabs or panes in the current workspace.

## Skill improvements

The Herdr skill should state:

- `wait-output` can match old or echoed text;
- timeout requires `pane read` before recovery;
- SSH hides remote child state;
- unsupported remote agents remain `unknown`;
- process readiness needs an independent probe.

Herdr itself would benefit from:

- `wait-output --after-revision <revision>`;
- a log cursor for pane output;
- an option that ignores echoed input;
- remote agent-state reporting;
- optional secret-pattern redaction in pane reads.
