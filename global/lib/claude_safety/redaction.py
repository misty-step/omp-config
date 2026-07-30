from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from .bash_policy import command_tokens, split_simple_commands
from typing import Any

SECRET_PREFIXES = ("sk-", "ghp_", "gho_", "ghs_", "ghu_", "ghr_", "github_pat_", "AKIA", "ASIA", "xoxb-", "xoxp-", "xoxa-", "xoxr-")
PEM_HEADERS = ("-----BEGIN PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN EC PRIVATE KEY-----", "-----BEGIN OPENSSH PRIVATE KEY-----", "-----BEGIN PGP PRIVATE KEY BLOCK-----")
REDACTED = "[REDACTED]"


def _decision(kind: str, **fields: str) -> dict[str, Any]:
    output: dict[str, Any] = {"hookEventName": kind}
    output.update(fields)
    return {"hookSpecificOutput": output}


def home_dir() -> Path:
    return Path(os.environ.get("HOME", "."))


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


def secrets_read_guard(data: dict[str, Any] | None, home: Path | None = None) -> dict[str, Any] | None:
    if data is None or data.get("tool_name") != "Bash":
        return None
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not command:
        return None
    reason = secrets_read_reason(command, home or home_dir())
    if reason is None:
        return None
    return _decision("PreToolUse", permissionDecision="deny", permissionDecisionReason=(f"BLOCKED: {reason}\n\nCommand: {command}\n\nUse an operator-approved secret broker or explicit environment injection instead. Never cat/grep/head/tail/source a secret file; its value can land in this transcript, which is QMD-indexed and permanently searchable."))


def secrets_read_tool_guard(data: dict[str, Any] | None, home: Path | None = None) -> dict[str, Any] | None:
    if data is None or data.get("tool_name") != "Read":
        return None
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or normalized_secret_path(file_path, home or home_dir()) is None:
        return None
    return _decision("PreToolUse", permissionDecision="deny", permissionDecisionReason=("BLOCKED: Direct Read of a designated secret file. Its value can be printed into this transcript, which is QMD-indexed and permanently searchable.\n\n" + f"File: {file_path}\n\nUse an operator-approved secret broker or explicit environment injection instead; never source a secret file."))


def secrets_redaction_command_rewrite(
    data: dict[str, Any] | None,
    cwd: Path | None = None,
    home: Path | None = None,
) -> dict[str, Any] | None:
    if data is None or data.get("tool_name") != "Bash":
        return None
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not command or "redact-stream" in command:
        return None
    from .bash_policy import destructive_command_reason

    active_home = home or home_dir()
    if destructive_command_reason(command, cwd or Path.cwd()) is not None or secret_path_mentioned(command, active_home):
        return None
    escaped = command.replace("'", "'\\''")
    redactor = 'python3 "$HOME/.omp/agent/hooks/claude-safety.py" redact-stream'
    rewritten = ("__omp_out=$(mktemp); __omp_err=$(mktemp); "
                 f"( eval '{escaped}' ) > \"$__omp_out\" 2> \"$__omp_err\"; __omp_rc=$?; "
                 f"{redactor} < \"$__omp_out\"; {redactor} < \"$__omp_err\" >&2; "
                 '/usr/bin/trash "$__omp_out" "$__omp_err" 2>/dev/null; exit $__omp_rc')
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "modifiedToolInput": {"command": rewritten, "description": tool_input.get("description", "Bash command (output redacted for secret shapes)")}}}


def redact(text: str, extra: list[str] | tuple[str, ...] = ()) -> str:
    for value in extra:
        if len(value) >= 6:
            text = text.replace(value, REDACTED)
    for header in PEM_HEADERS:
        start = text.find(header)
        if start < 0:
            continue
        end_marker = text.find("-----END ", start)
        if end_marker < 0:
            text = text[:start] + REDACTED
        else:
            line_end = text.find("\n", end_marker)
            if line_end < 0:
                line_end = len(text)
            text = text[:start] + REDACTED + text[line_end:]
        break
    return re.compile(r"[A-Za-z0-9_+\-/.~:]+").sub(_redact_token, text)


def _redact_token(match: re.Match[str]) -> str:
    token = match.group(0)
    before = match.string[:match.start()]
    previous_word = re.search(r"([A-Za-z0-9_+\-]+)\s*$", before)
    shell_reference = before.endswith("$") or before.endswith("$" + "{")
    if previous_word and previous_word.group(1).lower() == "bearer" and len(token) >= 8 and not shell_reference:
        return REDACTED
    if looks_like_jwt(token) or any(looks_like_fal_key(part) for part in token.split("/")):
        return REDACTED
    start = find_secret_prefix(token)
    return token[:start] + REDACTED if start is not None else token


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


