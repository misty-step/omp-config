#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# The hook is projected beside the package in both source and installed layouts.
_LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from claude_safety.bash_policy import destructive_command_guard, permission_auto_approve
from claude_safety.redaction import (
    home_dir,
    redact,
    redact_with_gitleaks,
    secrets_read_guard,
    secrets_read_tool_guard,
    secrets_redaction_command_rewrite,
)
from claude_safety.skill_audit import append_skill_invocation


def json_input() -> dict[str, Any] | None:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def decision(kind: str, **fields: str) -> dict[str, Any]:
    output: dict[str, Any] = {"hookEventName": kind}
    output.update(fields)
    return {"hookSpecificOutput": output}


def time_context() -> dict[str, Any]:
    now = datetime.now().astimezone()
    friendly = now.strftime("%A, %B %d, %Y at %-I:%M %p %Z")
    return {"result": "continue", "message": f"Current time: {friendly} ({now.isoformat()})"}


def run_hook(name: str) -> int:
    data = json_input()
    if name == "permission-auto-approve":
        output = permission_auto_approve(data, home=home_dir())
    elif name == "time-context":
        output = time_context()
    elif name == "destructive-command-guard":
        output = destructive_command_guard(data, Path.cwd())
    elif name == "skill-invocation-tracker":
        append_skill_invocation(data, Path(os.environ.get("SKILL_TRACKER_LOG_PATH", str(home_dir() / ".claude/skill-invocations.jsonl"))))
        output = None
    elif name == "secrets-read-guard":
        output = secrets_read_guard(data, home_dir())
    elif name == "secrets-read-tool-guard":
        output = secrets_read_tool_guard(data, home_dir())
    elif name == "secrets-redaction-rewrite":
        output = secrets_redaction_command_rewrite(data, Path.cwd(), home_dir())
    else:
        print(f"unknown claude-hook {name!r}", file=sys.stderr)
        return 1
    if output is not None:
        print(json.dumps(output, separators=(",", ":")))
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: claude-safety.py claude-hook <name>", file=sys.stderr)
        return 1
    if argv[0] == "redact-stream":
        print(redact_with_gitleaks(redact(sys.stdin.read())), end="")
        return 0
    if argv[0] == "claude-hook" and len(argv) == 2:
        return run_hook(argv[1])
    if argv[0] == "claude-hook":
        print("usage: claude-safety.py claude-hook <name>", file=sys.stderr)
        return 1
    print(f"unknown command {argv[0]!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
