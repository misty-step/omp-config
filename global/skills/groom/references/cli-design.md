# CLI Design Contract

Use this when a context packet creates or changes a command-line interface.
Base this contract on Peter Steinberger's `create-cli` skill and the public CLI
guidelines at https://clig.dev/.

## Lock The Interface

- Command name and one-sentence purpose.
- Primary user: human, script, or both.
- Inputs: args, stdin, files, URLs, config, env.
- Outputs: human text, `--json`, `--plain`, files, artifacts.
- Interactivity: prompts allowed, `--no-input`, confirmations.
- Safety: `--dry-run`, `--force`, `--confirm`, destructive operations.
- Config precedence: flags > env > project config > user config > defaults.
- Platform/runtime: macOS/Linux/Windows, single binary vs runtime.

## Defaults

- Make `-h` and `--help` show help and ignore other args.
- Make `--version` print the version to stdout.
- Send primary data to stdout. Send diagnostics and progress to stderr.
- Use `--json` for machine output and `--plain` for stable line output.
- Prompt only when stdin is a TTY. Let `--no-input` disable prompts.
- Require `--force` or explicit confirmation for destructive non-interactive
  runs.
- Respect `NO_COLOR` and `TERM=dumb`. Provide `--no-color` when colored output
  is otherwise the default.
- Make Ctrl-C exit quickly with bounded cleanup.

## Packet Requirements

For CLI work, include these fields in the context packet:

```markdown
## CLI Surface
- Command tree:
- Usage:
- Args/flags:
- Output contract:
- Error/exit code map:
- Config/env precedence:
- Safety controls:
- Examples:
```

For script-facing commands, include golden examples for stdout/stderr and exit
codes.
For human-facing commands, include at least one common happy path and one
failure example.
