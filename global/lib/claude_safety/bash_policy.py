from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

SAFE_BASH_COMMANDS = (
    r"^ls\b", r"^cat\b", r"^head\b", r"^tail\b",
    r"^wc\b", r"^file\b", r"^stat\b", r"^du\b", r"^df\b", r"^tree\b",
    r"^find\b.*-print", r"^find\b.*-name", r"^find\b.*-type",
    r"^git\s+(?:status|log|diff|show)(?:\s|$)",
    r"^git\s+branch(?:\s+--show-current)?\s*$",
    r"^git\s+remote(?:\s+-v)?\s*$",
    r"^git\s+tag(?:\s+--list)?\s*$",
    r"^git\s+stash\s+list(?:\s|$)",
    r"^git\s+ls-", r"^git\s+rev-parse", r"^git\s+describe",
    r"^git\s+config\s+(?:--get|-l|--list)(?:\s|$)",
    r"^git\s+shortlog", r"^git\s+blame", r"^git\s+annotate",
    r"^git\s+worktree\s+list(?:\s|$)",
    r"^jq\b", r"^bat\b", r"^eza?\b", r"^tokei\b", r"^cloc\b", r"^scc\b",
    r"^pip\s+(?:list|show|freeze)(?:\s|$)", r"^uname\b",
    r"^whoami\b", r"^hostname\b", r"^pwd\b", r"^env\s*$", r"^printenv\b",
    r"^echo\s+\$", r"^which\b", r"^whereis\b", r"^type\b", r"^command\s+-v",
    r"^ps\b", r"^top\s+-l\s+1", r"^uptime\b", r"^date\b", r"^cal\b",
    r"^gh\s+(?:repo|issue|pr|release|workflow|run)\s+(?:view|list|status|diff)(?:\s|$)",
    r"^gh\s+api\s+.*-X\s+GET(?:\s|$)", r"^gh\s+api\s+[^-]*$",
    r"^gh\s+auth\s+status(?:\s|$)",
    r"^vercel\s+(?:list|ls|inspect|logs|env\s+ls)(?:\s|$)", r"^vercel\s+--help\s*$",
)
NEVER_APPROVE = (
    r"rm\s", r"rmdir\s", r"unlink\s", r"--output(?:=|\s)", r">\s", r">>\s", r"\|\s*tee\b",
    r"curl.*-[dXP]", r"wget\s", r"sudo\b", r"su\b", r"chmod\b", r"chown\b",
    r"chgrp\b", r"kill\b", r"pkill\b", r"killall\b",
)
DESTRUCTIVE_SUBSTRINGS = (
    ("git reset --hard", "Destroys all uncommitted work. Use 'git stash' first."),
    ("git push --force", "Overwrites remote history. Use '--force-with-lease' instead."),
    ("git push -f ", "Overwrites remote history. Use '--force-with-lease' instead."),
    ("git stash drop", "Permanently deletes stashed changes."),
    ("git stash clear", "Permanently deletes ALL stashed changes."),
    ("gh repo delete", "Permanently deletes repository. Extremely destructive."),
    ("gh issue delete", "Permanently deletes an issue."),
    ("gh repo archive", "Archives repository, making it read-only."),
)
DANGEROUS_FLAGS = (
    ("--no-verify", "Skips git hooks. Hooks enforce quality gates."),
    ("--no-gpg-sign", "Skips commit signing. May violate repo policy."),
)


def _decision(kind: str, **fields: str) -> dict[str, Any]:
    output: dict[str, Any] = {"hookEventName": kind}
    output.update(fields)
    return {"hookSpecificOutput": output}


def permission_auto_approve(data: dict[str, Any] | None, home: Path | None = None) -> dict[str, Any] | None:
    if data is None:
        return None
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    safe = tool_name in {"Read", "Glob", "Grep", "LS", "WebFetch", "WebSearch"}
    if tool_name == "Bash":
        command = tool_input.get("command")
        safe = isinstance(command, str) and is_safe_bash(command, home=home)
    elif tool_name == "Task":
        safe = tool_input.get("subagent_type") in {"Explore", "Plan"}
    if not safe:
        return None
    return _decision("PreToolUse", permissionDecision="allow", permissionDecisionReason=f"Auto-approved: {tool_name} is read-only")


def find_destructive_action(command: str) -> bool:
    actions = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls"}
    for segment in split_simple_commands(command):
        tokens = command_tokens(segment)
        if executable_name(tokens) == "find" and any(token in actions or any(token.startswith(action + "=") for action in actions) for token in tokens):
            return True
    return False


def has_shell_control_syntax(command: str) -> bool:
    in_single = False
    in_double = False
    escaped = False
    index = 0
    while index < len(command):
        char = command[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if char == "\\" and not in_single:
            escaped = True
            index += 1
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            index += 1
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            index += 1
            continue
        if not in_single and not in_double:
            if char in ";|&\n<>" or char == chr(96):
                return True
            if char == "$" and index + 1 < len(command) and command[index + 1] == "(":
                return True
        index += 1
    return False


def is_safe_bash(command: str, *, home: Path | None = None) -> bool:
    if has_shell_control_syntax(command):
        return False
    if find_destructive_action(command) or git_reset_is_blocked(command) or git_push_is_forced(command) or contains_destructive_file_verb(command):
        return False
    if any(re.search(pattern, command, re.IGNORECASE) for pattern in NEVER_APPROVE):
        return False
    from .redaction import home_dir, secret_path_mentioned
    if secret_path_mentioned(command, home or home_dir()):
        return False
    tokens = command_tokens(command.strip())
    if tokens and tokens[0] == "env" and len(tokens) > 1:
        return False
    trimmed = command.strip()
    return any(re.search(pattern, trimmed, re.IGNORECASE) for pattern in SAFE_BASH_COMMANDS)


def destructive_command_guard(data: dict[str, Any] | None, cwd: Path) -> dict[str, Any] | None:
    if data is None or data.get("tool_name") != "Bash":
        return None
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not command:
        return None
    reason = destructive_command_reason(command, cwd)
    if reason is None:
        return None
    return _decision("PreToolUse", permissionDecision="deny", permissionDecisionReason=f"BLOCKED: {reason}\n\nCommand: {command}\n\nRun this yourself if truly needed.")


def split_simple_commands(command: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"[;&|\x60\n]", command.replace("$(", ";")) if segment.strip()]


def command_tokens(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def unwrapped_tokens(tokens: list[str]) -> list[str]:
    index = 0
    while index < len(tokens):
        base = Path(tokens[index]).name
        if base == "env":
            index += 1
            while index < len(tokens):
                token = tokens[index]
                if token in {"-u", "--unset"}:
                    index += 2
                    continue
                if token.startswith("-") or "=" in token:
                    index += 1
                    continue
                break
            continue
        if base == "nice":
            index += 1
            if index < len(tokens) and tokens[index] in {"-n", "--adjustment"}:
                index += 2
            continue
        if base in {"command", "nohup"}:
            index += 1
            if base == "command":
                while index < len(tokens) and tokens[index] in {"-p", "--help"}:
                    index += 1
            if index < len(tokens) and tokens[index] == "--":
                index += 1
            continue
        return tokens[index:]
    return []


def executable_name(tokens: list[str]) -> str | None:
    unwrapped = unwrapped_tokens(tokens)
    return Path(unwrapped[0]).name if unwrapped else None


def contains_destructive_file_verb(command: str) -> bool:
    for segment in split_simple_commands(command):
        if executable_name(command_tokens(segment)) in {"rm", "rmdir", "unlink"}:
            return True
    return False


def git_subcommand(tokens: list[str]) -> list[str]:
    tokens = unwrapped_tokens(tokens)
    if not tokens or Path(tokens[0]).name != "git":
        return []
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in {"-C", "-c"}:
            index += 2
            continue
        if token.startswith("-C") or token.startswith("-c"):
            index += 1
            continue
        break
    return tokens[index:]


def git_push_is_forced(command: str) -> bool:
    for segment in split_simple_commands(command):
        tokens = git_subcommand(command_tokens(segment))
        if tokens and tokens[0] == "push" and any(token == "-f" or token == "--force" or token.startswith("--force=") for token in tokens[1:]):
            return True
    return False


def git_reset_is_blocked(command: str) -> bool:
    for segment in split_simple_commands(command):
        tokens = git_subcommand(command_tokens(segment))
        if len(tokens) >= 2 and tokens[:2] == ["reset", "--hard"]:
            return True
    return False


def destructive_command_reason(command: str, cwd: Path) -> str | None:
    for flag, reason in DANGEROUS_FLAGS:
        if flag in command:
            return reason
    if find_destructive_action(command):
        return "Find action may mutate files. Inspect and run it yourself if truly needed."
    if git_reset_is_blocked(command):
        return "Destroys all uncommitted work. Use 'git stash' first."
    if git_push_is_forced(command):
        return "Overwrites remote history. Use '--force-with-lease' instead."
    branch = current_branch(cwd)
    if re.search(r"^git\s+merge\s+\S+", command) and branch in {"main", "master"}:
        return f"Merging into {branch} is blocked. Create a PR instead."
    match = re.search(r"git\s+branch\s+-D\s+(.*)", command)
    if match:
        for candidate in match.group(1).split():
            if candidate in {"main", "master"}:
                return f"Force-deleting {candidate} is blocked. Protected branch."
    stripped = strip_quoted_content(command)
    if contains_destructive_file_verb(command) or re.search(r"(?m)(^|[;&|\x60]|\$\()\s*rm\s", stripped):
        return "Use /usr/bin/trash instead. Moves to Trash (recoverable). Example: /usr/bin/trash file.txt"
    for pattern, reason in DESTRUCTIVE_SUBSTRINGS:
        if pattern.startswith("git reset --hard") or pattern.startswith("git push"):
            continue
        if pattern in stripped:
            return reason
    return None


def current_branch(cwd: Path) -> str | None:
    try:
        result = subprocess.run(["git", "branch", "--show-current"], cwd=cwd, capture_output=True, text=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def strip_quoted_content(command: str) -> str:
    result: list[str] = []
    in_single = False
    in_double = False
    index = 0
    while index < len(command):
        char = command[index]
        if char == "\\" and index + 1 < len(command):
            if not in_single and not in_double:
                result.extend((char, command[index + 1]))
            index += 2
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            result.append(char)
        elif char == "'" and not in_double:
            in_single = not in_single
            result.append(char)
        elif not in_single and not in_double:
            result.append(char)
        index += 1
    return "".join(result)
