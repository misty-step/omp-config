#!/usr/bin/env python3
"""Persist OMP assistant usage metadata while keeping prompts, completions, and credentials outside the privacy boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_SESSIONS_ROOT = Path.home() / ".omp" / "agent" / "sessions"
DEFAULT_DB = Path.home() / ".omp" / "agent" / "usage-ledger.sqlite3"
GROUP_FIELDS = {
    "day": "substr(timestamp, 1, 10)",
    "model": "COALESCE(model, 'unknown')",
    "provider": "COALESCE(provider, 'unknown')",
    "agent": "COALESCE(agent_type, 'unknown')",
    "workspace": "COALESCE(workspace, 'unknown')",
    "repo": "COALESCE(repo, 'unknown')",
    "session": "COALESCE(session_id, 'unknown')",
}
SCHEMA = """
CREATE TABLE IF NOT EXISTS responses (
    response_key TEXT PRIMARY KEY,
    response_id TEXT,
    session_id TEXT,
    session_file TEXT NOT NULL,
    lane TEXT,
    agent_type TEXT,
    workspace TEXT,
    repo TEXT,
    provider TEXT,
    model TEXT,
    reasoning_level TEXT,
    timestamp TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cache_read_tokens INTEGER,
    cache_write_tokens INTEGER,
    total_tokens INTEGER,
    reasoning_tokens INTEGER,
    cost_input REAL,
    cost_output REAL,
    cost_cache_read REAL,
    cost_cache_write REAL,
    cost_total REAL,
    duration REAL,
    ttft REAL,
    UNIQUE(response_id)
);
CREATE INDEX IF NOT EXISTS responses_timestamp ON responses(timestamp);
CREATE INDEX IF NOT EXISTS responses_provider ON responses(provider);
CREATE INDEX IF NOT EXISTS responses_model ON responses(model);
CREATE TABLE IF NOT EXISTS sessions (
    session_file TEXT PRIMARY KEY,
    session_id TEXT,
    workspace TEXT,
    repo TEXT
);
CREATE TABLE IF NOT EXISTS lane_agents (
    parent_file TEXT NOT NULL,
    lane TEXT NOT NULL,
    agent_type TEXT,
    PRIMARY KEY(parent_file, lane)
);
CREATE TABLE IF NOT EXISTS file_state (
    path TEXT PRIMARY KEY,
    inode INTEGER NOT NULL,
    offset INTEGER NOT NULL
);
"""


def _connect(path: Path) -> sqlite3.Connection:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.stat().st_mode & 0o077:
        raise PermissionError(f"ledger directory must be private: {path.parent}")
    if not path.exists():
        path.touch(mode=0o600)
    path.chmod(0o600)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript(SCHEMA)
    return connection


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _integer(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return int(value)
    return None


def _number(value: Any) -> float | int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)) and math.isfinite(value):
        return value
    return None


def _repo_slug(workspace: str | None) -> str | None:
    if not workspace:
        return None
    name = Path(workspace.rstrip("/\\")).name
    return name or None


def _parent_file(path: Path) -> Path | None:
    if path.parent.name == path.stem:
        return None
    candidate = path.parent.parent / f"{path.parent.name}.jsonl"
    if candidate.is_file() and candidate != path:
        return candidate
    return None


def _session_context(connection: sqlite3.Connection, parent: Path) -> dict[str, str | None]:
    key = str(parent)
    row = connection.execute(
        "SELECT session_id, workspace, repo FROM sessions WHERE session_file = ?", (key,)
    ).fetchone()
    context = {
        "session_id": row["session_id"] if row else None,
        "workspace": row["workspace"] if row else None,
        "repo": row["repo"] if row else None,
    }
    return context


def _store_session(
    connection: sqlite3.Connection, path: Path, session_id: str | None, workspace: str | None
) -> dict[str, str | None]:
    context = {
        "session_id": session_id,
        "workspace": workspace,
        "repo": _repo_slug(workspace),
    }
    connection.execute(
        """
        INSERT INTO sessions(session_file, session_id, workspace, repo)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_file) DO UPDATE SET
            session_id = excluded.session_id,
            workspace = excluded.workspace,
            repo = excluded.repo
        """,
        (str(path), context["session_id"], context["workspace"], context["repo"]),
    )
    return context


def _task_mappings(obj: dict[str, Any]) -> list[tuple[str, str | None]]:
    message = obj.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant":
        return []
    content = message.get("content")
    if not isinstance(content, list):
        return []
    mappings: list[tuple[str, str | None]] = []
    for item in content:
        if not isinstance(item, dict) or item.get("type") != "toolCall" or item.get("name") != "task":
            continue
        arguments = item.get("arguments")
        if not isinstance(arguments, dict) or not isinstance(arguments.get("tasks"), list):
            continue
        for task in arguments["tasks"]:
            if not isinstance(task, dict):
                continue
            lane = _text(task.get("name"))
            if lane:
                mappings.append((lane, _text(task.get("agent"))))
    return mappings


def _upsert_mappings(
    connection: sqlite3.Connection, parent: Path, mappings: list[tuple[str, str | None]]
) -> None:
    parent_key = str(parent)
    for lane, agent_type in mappings:
        connection.execute(
            """
            INSERT INTO lane_agents(parent_file, lane, agent_type)
            VALUES (?, ?, ?)
            ON CONFLICT(parent_file, lane) DO UPDATE SET agent_type = excluded.agent_type
            """,
            (parent_key, lane, agent_type),
        )
        connection.execute(
            "UPDATE responses SET agent_type = ? WHERE session_file = ? AND lane = ?",
            (agent_type, str(parent.with_suffix("") / f"{lane}.jsonl"), lane),
        )


def _agent_map(connection: sqlite3.Connection, parent: Path) -> dict[str, str | None]:
    rows = connection.execute(
        "SELECT lane, agent_type FROM lane_agents WHERE parent_file = ?", (str(parent),)
    )
    return {row["lane"]: row["agent_type"] for row in rows}


def _response_row(
    obj: dict[str, Any],
    *,
    session_file: Path,
    context: dict[str, str | None],
    lane: str | None,
    agent_type: str | None,
) -> dict[str, Any] | None:
    if obj.get("type") != "message":
        return None
    message = obj.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant":
        return None
    usage = message.get("usage")
    if not isinstance(usage, dict):
        return None
    cost = usage.get("cost")
    if not isinstance(cost, dict):
        cost = {}
    reasoning_level = None
    for source in (message, obj):
        for key in ("reasoningLevel", "thinkingLevel", "reasoning"):
            candidate = _text(source.get(key))
            if candidate:
                reasoning_level = candidate
                break
        if reasoning_level:
            break
    row = {
        "response_id": _text(message.get("responseId")) or _text(obj.get("responseId")),
        "session_id": context.get("session_id"),
        "session_file": str(session_file),
        "lane": lane,
        "agent_type": agent_type,
        "workspace": context.get("workspace"),
        "repo": context.get("repo"),
        "provider": _text(message.get("provider")),
        "model": _text(message.get("model")),
        "reasoning_level": reasoning_level,
        "timestamp": _text(obj.get("timestamp")) or _text(message.get("timestamp")),
        "input_tokens": _integer(usage.get("input")),
        "output_tokens": _integer(usage.get("output")),
        "cache_read_tokens": _integer(usage.get("cacheRead")),
        "cache_write_tokens": _integer(usage.get("cacheWrite")),
        "total_tokens": _integer(usage.get("totalTokens")),
        "reasoning_tokens": _integer(usage.get("reasoningTokens")),
        "cost_input": _number(cost.get("input")),
        "cost_output": _number(cost.get("output")),
        "cost_cache_read": _number(cost.get("cacheRead")),
        "cost_cache_write": _number(cost.get("cacheWrite")),
        "cost_total": _number(cost.get("total")),
        "duration": _number(message.get("duration"))
        if "duration" in message
        else _number(obj.get("duration")),
        "ttft": _number(message.get("ttft")) if "ttft" in message else _number(obj.get("ttft")),
    }
    row["response_key"] = row["response_id"] or _synthetic_key(row)
    return row


def _synthetic_key(row: dict[str, Any]) -> str:
    """Identify a response with no provider id by its own recorded facts.

    A transcript can be inherited into another log, so the key must not use the
    file or byte offset. Two copies of one response then collapse to one row.
    """
    parts = (
        row["timestamp"],
        row["model"],
        row["provider"],
        row["input_tokens"],
        row["output_tokens"],
        row["total_tokens"],
        row["cost_total"],
    )
    digest = hashlib.sha256("\0".join("" if part is None else str(part) for part in parts).encode("utf-8"))
    return f"synthetic:{digest.hexdigest()}"


def _insert_response(connection: sqlite3.Connection, row: dict[str, Any]) -> None:
    columns = ", ".join(row)
    placeholders = ", ".join(f":{name}" for name in row)
    connection.execute(f"INSERT INTO responses({columns}) VALUES ({placeholders})", row)


def _ingest_file(
    connection: sqlite3.Connection,
    path: Path,
    *,
    is_parent: bool,
    contexts: dict[str, dict[str, str | None]],
) -> tuple[int, int]:
    skipped = 0
    inserted = 0
    path = path.absolute()
    try:
        initial_stat = path.stat()
    except OSError:
        return 0, 1
    state = connection.execute(
        "SELECT inode, offset FROM file_state WHERE path = ?", (str(path),)
    ).fetchone()
    offset = 0
    if state and int(state["inode"]) == int(initial_stat.st_ino) and int(initial_stat.st_size) >= int(state["offset"]):
        offset = int(state["offset"])
    parent = None if is_parent else _parent_file(path)
    parent_key = str(parent.absolute()) if parent else None
    if is_parent:
        context = contexts.get(str(path)) or _session_context(connection, path)
        mappings = _agent_map(connection, path)
    else:
        if parent:
            context = contexts.get(parent_key) or _session_context(connection, parent)
        else:
            context = {"session_id": None, "workspace": None, "repo": None}
        mappings = _agent_map(connection, parent) if parent else {}
    lane = None if is_parent else path.stem
    if is_parent:
        agent_type = "chief"
    elif lane.startswith("__"):
        agent_type = lane.lstrip("_")
    else:
        agent_type = mappings.get(lane)
    processed_offset = offset
    try:
        with path.open("rb") as stream:
            stream.seek(offset)
            while True:
                line_start = stream.tell()
                raw = stream.readline()
                if not raw:
                    processed_offset = line_start
                    break
                if not raw.endswith(b"\n"):
                    skipped += 1
                    processed_offset = line_start
                    break
                candidate_usage = b'"usage"' in raw and b'"assistant"' in raw
                candidate_task = b'"toolCall"' in raw and b'"task"' in raw
                candidate_context = candidate_task or (is_parent and b'"session"' in raw)
                if not candidate_usage and not candidate_context:
                    processed_offset = stream.tell()
                    continue
                try:
                    decoded = raw.decode("utf-8")
                    obj = json.loads(decoded)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    skipped += 1
                    processed_offset = stream.tell()
                    continue
                if not isinstance(obj, dict):
                    processed_offset = stream.tell()
                    continue
                if is_parent and obj.get("type") == "session":
                    session_id = _text(obj.get("id"))
                    workspace = _text(obj.get("cwd"))
                    context = _store_session(connection, path, session_id, workspace)
                    contexts[str(path)] = context
                if candidate_task and (mapping_root := path if is_parent else parent):
                    _upsert_mappings(connection, mapping_root, _task_mappings(obj))
                    if lane and not agent_type:
                        agent_type = _agent_map(connection, mapping_root).get(lane)
                values = _response_row(
                    obj,
                    session_file=path,
                    context=context,
                    lane=lane,
                    agent_type=agent_type,
                )
                if values is not None:
                    try:
                        _insert_response(connection, values)
                    except sqlite3.IntegrityError:
                        skipped += 1
                    else:
                        inserted += 1
                processed_offset = stream.tell()
    except OSError:
        skipped += 1
    connection.execute(
        """
        INSERT INTO file_state(path, inode, offset) VALUES (?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET inode = excluded.inode, offset = excluded.offset
        """,
        (str(path), int(initial_stat.st_ino), int(processed_offset)),
    )
    if is_parent:
        contexts[str(path)] = context
    return inserted, skipped


def ingest(args: argparse.Namespace) -> int:
    root = Path(args.sessions_root).expanduser().absolute()
    database = Path(args.db).expanduser()
    try:
        files = sorted(path for path in root.rglob("*.jsonl") if path.is_file())
    except OSError as error:
        print(f"usage-ledger: cannot scan {root}: {error}", file=sys.stderr)
        return 1
    parents: list[Path] = []
    children: list[Path] = []
    for path in files:
        if _parent_file(path) is None:
            parents.append(path)
        else:
            children.append(path)
    connection = _connect(database)
    inserted = 0
    skipped = 0
    contexts: dict[str, dict[str, str | None]] = {}
    try:
        for path in parents + children:
            added, ignored = _ingest_file(
                connection, path, is_parent=path in parents, contexts=contexts
            )
            inserted += added
            skipped += ignored
        connection.commit()
    finally:
        connection.close()
    print(f"scanned files: {len(files)}; inserted rows: {inserted}; skipped rows: {skipped}")
    return 0


def _date_bound(value: str, *, until: bool) -> tuple[str, bool]:
    if len(value) == 10:
        parsed = date.fromisoformat(value)
        if until:
            return (parsed + timedelta(days=1)).isoformat(), False
        return parsed.isoformat() + "T00:00:00", True
    parsed_datetime = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed_datetime.isoformat(), True


def _report_rows(connection: sqlite3.Connection, args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    clauses: list[str] = []
    parameters: list[Any] = []
    if args.since:
        bound, inclusive = _date_bound(args.since, until=False)
        clauses.append("datetime(timestamp) >= datetime(?)" if inclusive else "datetime(timestamp) > datetime(?)")
        parameters.append(bound)
    if args.until:
        bound, inclusive = _date_bound(args.until, until=True)
        clauses.append("datetime(timestamp) <= datetime(?)" if inclusive else "datetime(timestamp) < datetime(?)")
        parameters.append(bound)
    if args.provider:
        clauses.append("provider = ?")
        parameters.append(args.provider)
    if args.model:
        clauses.append("model = ?")
        parameters.append(args.model)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    expression = GROUP_FIELDS[args.by]
    query = f"""
        SELECT {expression} AS dimension,
               COUNT(*) AS requests,
               COALESCE(SUM(cost_total), 0) AS total_cost,
               COALESCE(SUM(total_tokens), 0) AS total_tokens,
               COALESCE(SUM(cache_read_tokens), 0) AS cached_tokens
        FROM responses{where}
        GROUP BY {expression}
        ORDER BY total_cost DESC, dimension ASC
    """
    rows = [dict(row) for row in connection.execute(query, parameters)]
    totals = {
        "requests": sum(int(row["requests"]) for row in rows),
        "total_cost": sum(float(row["total_cost"]) for row in rows),
        "total_tokens": sum(int(row["total_tokens"]) for row in rows),
        "cached_tokens": sum(int(row["cached_tokens"]) for row in rows),
    }
    for row in rows:
        row["total_cost"] = float(row["total_cost"])
        row["cost_share"] = row["total_cost"] / totals["total_cost"] if totals["total_cost"] else 0.0
    return rows, totals


def report(args: argparse.Namespace) -> int:
    connection = _connect(Path(args.db).expanduser())
    try:
        rows, totals = _report_rows(connection, args)
    finally:
        connection.close()
    if args.json:
        print(json.dumps({"by": args.by, "rows": rows, "totals": totals}, sort_keys=True))
        return 0
    print(f"{args.by}\trequests\ttotal_cost\ttotal_tokens\tcached_tokens\tcost_share")
    for row in rows:
        print(
            f"{row['dimension']}\t{row['requests']}\t{row['total_cost']:.6f}\t"
            f"{row['total_tokens']}\t{row['cached_tokens']}\t{row['cost_share']:.2%}"
        )
    total_share = "100.00%" if totals["total_cost"] else "0.00%"
    print(
        f"total\t{totals['requests']}\t{totals['total_cost']:.6f}\t"
        f"{totals['total_tokens']}\t{totals['cached_tokens']}\t{total_share}"
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and report an OMP model usage ledger")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest_parser = subparsers.add_parser("ingest", help="ingest OMP session metadata")
    ingest_parser.add_argument("--sessions-root", type=Path, default=DEFAULT_SESSIONS_ROOT)
    ingest_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    ingest_parser.set_defaults(handler=ingest)
    report_parser = subparsers.add_parser("report", help="report usage aggregates")
    report_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    report_parser.add_argument("--since")
    report_parser.add_argument("--until")
    report_parser.add_argument("--by", choices=sorted(GROUP_FIELDS), default="day")
    report_parser.add_argument("--provider")
    report_parser.add_argument("--model")
    report_parser.add_argument("--json", action="store_true")
    report_parser.set_defaults(handler=report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"usage-ledger: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
