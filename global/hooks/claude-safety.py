#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
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
DESTRUCTIVE_SUBSTRINGS = (("git reset --hard", "Destroys all uncommitted work. Use 'git stash' first."), ("git push --force", "Overwrites remote history. Use '--force-with-lease' instead."), ("git push -f ", "Overwrites remote history. Use '--force-with-lease' instead."), ("git stash drop", "Permanently deletes stashed changes."), ("git stash clear", "Permanently deletes ALL stashed changes."), ("gh repo delete", "Permanently deletes repository. Extremely destructive."), ("gh issue delete", "Permanently deletes an issue."), ("gh repo archive", "Archives repository, making it read-only."))
DANGEROUS_FLAGS = (("--no-verify", "Skips git hooks. Hooks enforce quality gates."), ("--no-gpg-sign", "Skips commit signing. May violate repo policy."))
SECRET_PREFIXES = ("sk-", "ghp_", "gho_", "ghs_", "ghu_", "ghr_", "github_pat_", "AKIA", "ASIA", "xoxb-", "xoxp-", "xoxa-", "xoxr-")
PEM_HEADERS = ("-----BEGIN PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN EC PRIVATE KEY-----", "-----BEGIN OPENSSH PRIVATE KEY-----", "-----BEGIN PGP PRIVATE KEY BLOCK-----")
REDACTED = "[REDACTED]"


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


def permission_auto_approve(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    safe = tool_name in {"Read", "Glob", "Grep", "LS", "WebFetch", "WebSearch"}
    if tool_name == "Bash":
        command = tool_input.get("command")
        safe = isinstance(command, str) and is_safe_bash(command)
    elif tool_name == "Task":
        safe = tool_input.get("subagent_type") in {"Explore", "Plan"}
    if not safe:
        return None
    return decision("PreToolUse", permissionDecision="allow", permissionDecisionReason=f"Auto-approved: {tool_name} is read-only")


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


def is_safe_bash(command: str) -> bool:
    if has_shell_control_syntax(command):
        return False
    if (find_destructive_action(command) or secret_path_mentioned(command, home_dir()) or
            git_reset_is_blocked(command) or git_push_is_forced(command) or
            contains_destructive_file_verb(command)):
        return False
    if any(re.search(pattern, command, re.IGNORECASE) for pattern in NEVER_APPROVE):
        return False
    tokens = command_tokens(command.strip())
    if tokens and tokens[0] == "env" and len(tokens) > 1:
        return False
    trimmed = command.strip()
    return any(re.search(pattern, trimmed, re.IGNORECASE) for pattern in SAFE_BASH_COMMANDS)
def time_context() -> dict[str, Any]:
    now = datetime.now().astimezone()
    friendly = now.strftime("%A, %B %d, %Y at %-I:%M %p %Z")
    return {"result": "continue", "message": f"Current time: {friendly} ({now.isoformat()})"}


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
    return decision("PreToolUse", permissionDecision="deny", permissionDecisionReason=f"BLOCKED: {reason}\n\nCommand: {command}\n\nRun this yourself if truly needed.")


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
        if len(tokens) >= 1 and tokens[0] == "push":
            if any(token == "-f" or token == "--force" or token.startswith("--force=") for token in tokens[1:]):
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




def normalized_secret_path(value: str, home: Path) -> Path | None:
    value = value.strip().strip("\\\"'")
    home_var = "$" + "{HOME}"
    if value == "~/.secrets":
        value = str(home / ".secrets")
    elif value.startswith("~/"):
        value = str(home / value[2:])
    elif value == "$HOME/.secrets" or value.startswith("$HOME/"):
        value = str(home) + value[len("$HOME"):]
    elif value == home_var + "/.secrets" or value.startswith(home_var + "/"):
        value = str(home) + value[len(home_var):]
    try:
        candidate = Path(value).expanduser().resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None
    target = (home / ".secrets").resolve(strict=False)
    return candidate if candidate == target else None



def secret_path_mentioned(command: str, home: Path) -> bool:
    for segment in split_simple_commands(command):
        for token in command_tokens(segment):
            if normalized_secret_path(token, home) is not None:
                return True
        for prefix in ("~", "$HOME", "$" + "{HOME}", str(home)):
            pattern = rf"(?<![A-Za-z0-9_.-]){re.escape(prefix)}/(?:\./)*\.secrets(?![A-Za-z0-9_.-])"
            if re.search(pattern, segment):
                return True
    return False
def secrets_read_reason(command: str, home: Path) -> str | None:
    if secret_path_mentioned(command, home):
        return "Access to a designated secret file, including sourcing it, is blocked."
    return None
def secrets_read_guard(data: dict[str, Any] | None, home: Path) -> dict[str, Any] | None:
    if data is None or data.get("tool_name") != "Bash":
        return None
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not command:
        return None
    reason = secrets_read_reason(command, home)
    if reason is None:
        return None
    return decision("PreToolUse", permissionDecision="deny", permissionDecisionReason=(f"BLOCKED: {reason}\n\nCommand: {command}\n\nUse an operator-approved secret broker or explicit environment injection instead. Never cat/grep/head/tail/source a secret file; its value can land in this transcript, which is QMD-indexed and permanently searchable."))


def secrets_read_tool_guard(data: dict[str, Any] | None, home: Path) -> dict[str, Any] | None:
    if data is None or data.get("tool_name") != "Read":
        return None
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or normalized_secret_path(file_path, home) is None:
        return None
    return decision("PreToolUse", permissionDecision="deny", permissionDecisionReason=("BLOCKED: Direct Read of a designated secret file. Its value can be printed into this transcript, which is QMD-indexed and permanently searchable.\n\n" + f"File: {file_path}\n\nUse an operator-approved secret broker or explicit environment injection instead; never source a secret file."))
def secrets_redaction_command_rewrite(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None or data.get("tool_name") != "Bash":
        return None
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not command or "redact-stream" in command:
        return None
    if destructive_command_guard(data, Path.cwd()) is not None or secrets_read_guard(data, home_dir()) is not None:
        return None
    escaped = command.replace("'", "'\\''")
    redactor = 'python3 "$HOME/.omp/agent/hooks/claude-safety.py" redact-stream'
    rewritten = ("__omp_out=$(mktemp); __omp_err=$(mktemp); "
                 f"( eval '{escaped}' ) > \"$__omp_out\" 2> \"$__omp_err\"; __omp_rc=$?; "
                 f"{redactor} < \"$__omp_out\"; {redactor} < \"$__omp_err\" >&2; "
                 '/usr/bin/trash "$__omp_out" "$__omp_err" 2>/dev/null; exit $__omp_rc')
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "modifiedToolInput": {"command": rewritten, "description": tool_input.get("description", "Bash command (output redacted for secret shapes)")}}}


def build_skill_invocation_entry(data: dict[str, Any]) -> dict[str, Any] | None:
    if data.get("tool_name") != "Skill":
        return None
    tool_input = data.get("tool_input")
    skill = tool_input.get("skill") if isinstance(tool_input, dict) else None
    if not isinstance(skill, str) or not skill:
        return None
    cwd = data.get("cwd", "") if isinstance(data.get("cwd", ""), str) else ""
    entry: dict[str, Any] = {"schema_version": data.get("schema_version", 2), "event_type": data.get("event_type", "skill_invocation"), "ts": datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"), "harness": data.get("harness", "claude"), "source_protocol": data.get("source_protocol", "post_tool_use"), "skill": skill, "args": tool_input.get("args", ""), "session_id": data.get("session_id", ""), "cwd": cwd, "project": Path(cwd).name if cwd else "", "invocation_kind": classify_invocation(data)}
    for field in ("model_id", "outcome", "duration_ms", "usage"):
        if field in data:
            entry[field] = data[field]
    return entry


def classify_invocation(data: dict[str, Any]) -> str:
    path = data.get("transcript_path")
    if not isinstance(path, str):
        return "unknown"
    try:
        text = Path(path).read_text()
    except OSError:
        return "unknown"
    entries: list[Any] = []
    for line in text.splitlines():
        try:
            entries.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            pass
    current = next((i for i in range(len(entries) - 1, -1, -1) if assistant_invokes_skill(entries[i])), None)
    if current is None:
        return "unknown"
    for entry in reversed(entries[:current]):
        if not isinstance(entry, dict):
            continue
        message = entry.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if entry.get("type") == "assistant" and assistant_invokes_skill(entry):
            return "routed"
        if entry.get("type") == "user" and genuine_user_turn(content):
            return "direct"
    return "direct"


def genuine_user_turn(content: Any) -> bool:
    if isinstance(content, str):
        return True
    return isinstance(content, list) and any(not isinstance(block, dict) or block.get("type") != "tool_result" for block in content)


def assistant_invokes_skill(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    message = entry.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    return isinstance(content, list) and any(isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill" for block in content)


def append_skill_invocation(data: dict[str, Any] | None, path: Path) -> None:
    if data is None:
        return
    entry = build_skill_invocation_entry(data)
    if entry is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except OSError:
        pass


def home_dir() -> Path:
    return Path(os.environ.get("HOME", "."))


def redact(text: str, extra: list[str] | tuple[str, ...] = ()) -> str:
    for value in extra:
        if len(value) >= 6:
            text = text.replace(value, "[REDACTED]")
    for header in PEM_HEADERS:
        start = text.find(header)
        if start < 0:
            continue
        end_marker = text.find("-----END ", start)
        if end_marker < 0:
            text = text[:start] + "[REDACTED]"
        else:
            line_end = text.find("\n", end_marker)
            if line_end < 0:
                line_end = len(text)
            text = text[:start] + "[REDACTED]" + text[line_end:]
        break
    return re.compile(r"[A-Za-z0-9_+\-/.~:]+").sub(_redact_token, text)


def _redact_token(match: re.Match[str]) -> str:
    token = match.group(0)
    before = match.string[:match.start()]
    previous_word = re.search(r"([A-Za-z0-9_+\-]+)\s*$", before)
    shell_reference = before.endswith("$") or before.endswith("$" + "{")
    if previous_word and previous_word.group(1).lower() == "bearer" and len(token) >= 8 and not shell_reference:
        return "[REDACTED]"
    if looks_like_jwt(token) or any(looks_like_fal_key(part) for part in token.split("/")):
        return "[REDACTED]"
    start = find_secret_prefix(token)
    return token[:start] + "[REDACTED]" if start is not None else token


def find_secret_prefix(token: str) -> int | None:
    positions: list[int] = []
    for prefix in SECRET_PREFIXES:
        index = token.find(prefix)
        if index >= 0:
            after = token[index + len(prefix):]
            material = re.split(r"[/:@=]", after, maxsplit=1)[0]
            if len(material) >= 8:
                positions.append(index)
    return min(positions) if positions else None


def looks_like_jwt(token: str) -> bool:
    parts = token.split(".")
    return len(parts) == 3 and all(part and len(part) >= 8 and re.fullmatch(r"[A-Za-z0-9_-]+", part) for part in parts[:2]) and bool(parts[2])


def looks_like_fal_key(token: str) -> bool:
    if ":" not in token:
        return False
    identifier, secret = token.split(":", 1)
    return len(identifier) >= 8 and bool(re.fullmatch(r"[A-Fa-f0-9-]+", identifier)) and len(secret) >= 16 and bool(re.fullmatch(r"[A-Fa-f0-9]+", secret))


def redact_with_gitleaks(text: str) -> str:
    try:
        result = subprocess.run(["gitleaks", "stdin", "--report-format", "json", "--report-path", "-", "--exit-code", "0", "--log-level", "fatal"], input=text, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return text
    try:
        findings = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        return text
    if not isinstance(findings, list):
        return text
    secrets = {item.get("Secret") for item in findings if isinstance(item, dict) and isinstance(item.get("Secret"), str) and len(item["Secret"]) >= 6}
    return redact(text, sorted(secrets)) if secrets else text


def run_hook(name: str) -> int:
    data = json_input()
    if name == "permission-auto-approve":
        output = permission_auto_approve(data)
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
        output = secrets_redaction_command_rewrite(data)
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
