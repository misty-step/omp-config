from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
    current = next((index for index in range(len(entries) - 1, -1, -1) if assistant_invokes_skill(entries[index])), None)
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
