#!/usr/bin/env python3
"""Forward OMP stdio MCP frames to Exa through the Mint broker."""

from __future__ import annotations

import json
import math
import sys
from http.client import HTTPException
from typing import Any, Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "http://mint.tail5f5eb4.ts.net:4949/proxy/https/mcp.exa.ai/mcp"
KEY_MARKER = "__mint.exa.default__"
PROTOCOL_VERSION = "2025-03-26"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_ERROR_BYTES = 64 * 1024
MAX_SSE_READ_BYTES = 64 * 1024
MAX_SSE_LINE_BYTES = 1024 * 1024


class ResponseTooLarge(Exception):
    """Raised when an upstream response exceeds the bridge limit."""


def emit_error(request_id: Any, code: int, message: str) -> None:
    emit(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
    )


def reject_json_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant: {value}")


def parse_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON number: {value}")
    return parsed


def parse_message(payload: str) -> dict[str, Any] | None:
    try:
        message = json.loads(
            payload.removeprefix("\ufeff"),
            parse_float=parse_json_float,
            parse_constant=reject_json_constant,
        )
    except (json.JSONDecodeError, ValueError):
        return None
    return message if isinstance(message, dict) else None


def read_body(response: Any, limit: int = MAX_RESPONSE_BYTES) -> str:
    body = response.read(limit + 1)
    if len(body) > limit:
        raise ResponseTooLarge(f"response exceeded {limit} bytes")
    return body.decode("utf-8", errors="replace")


def sse_lines(response: Any) -> Iterator[bytes]:
    buffered = bytearray()
    total_bytes = 0
    read_chunk = getattr(response, "read1", response.read)

    while True:
        chunk = read_chunk(MAX_SSE_READ_BYTES)
        if not chunk:
            break
        next_total = total_bytes + len(chunk)
        if next_total > MAX_RESPONSE_BYTES:
            raise ResponseTooLarge(f"response exceeded {MAX_RESPONSE_BYTES} bytes")
        total_bytes = next_total
        buffered.extend(chunk)
        while True:
            delimiters = [position for position in (buffered.find(b"\n"), buffered.find(b"\r")) if position >= 0]
            if not delimiters:
                if len(buffered) > MAX_SSE_LINE_BYTES:
                    raise ResponseTooLarge(f"SSE line exceeded {MAX_SSE_LINE_BYTES} bytes")
                break
            delimiter = min(delimiters)
            if delimiter > MAX_SSE_LINE_BYTES:
                raise ResponseTooLarge(f"SSE line exceeded {MAX_SSE_LINE_BYTES} bytes")
            if buffered[delimiter] == 13 and delimiter + 1 == len(buffered):
                break
            delimiter_size = 2 if buffered[delimiter : delimiter + 2] == b"\r\n" else 1
            line = bytes(buffered[:delimiter])
            del buffered[: delimiter + delimiter_size]
            yield line
    if len(buffered) > MAX_SSE_LINE_BYTES:
        raise ResponseTooLarge(f"SSE line exceeded {MAX_SSE_LINE_BYTES} bytes")
    if buffered.endswith(b"\r"):
        yield bytes(buffered[:-1])
        yield b""
    elif buffered:
        yield bytes(buffered)


def sse_messages(response: Any) -> Iterator[dict[str, Any]]:
    data_lines: list[str] = []
    first_line = True

    def finish_event() -> dict[str, Any] | None:
        if not data_lines:
            return None
        message = parse_message("\n".join(data_lines))
        data_lines.clear()
        return message

    for raw_line in sse_lines(response):
        line = raw_line.decode("utf-8", errors="replace")
        if first_line:
            line = line.removeprefix("\ufeff")
            first_line = False
        if line.startswith("data:"):
            value = line[5:]
            data_lines.append(value[1:] if value.startswith(" ") else value)
            continue
        if line.startswith((":", "event:", "id:", "retry:")):
            continue
        if line == "":
            message = finish_event()
            if message is not None:
                yield message
    message = finish_event()
    if message is not None:
        yield message


def response_messages(response: Any) -> Iterator[dict[str, Any]]:
    content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if content_type == "text/event-stream":
        yield from sse_messages(response)
        return
    message = parse_message(read_body(response))
    if message is not None:
        yield message

def valid_request_id(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, float):
        return math.isfinite(value)
    return isinstance(value, (str, int))


def valid_request(message: Any) -> bool:
    return (
        isinstance(message, dict)
        and message.get("jsonrpc") == "2.0"
        and isinstance(message.get("method"), str)
        and ("id" not in message or valid_request_id(message["id"]))
        and ("params" not in message or isinstance(message["params"], (dict, list)))
    )


def valid_error(error: Any) -> bool:
    return (
        isinstance(error, dict)
        and isinstance(error.get("code"), int)
        and not isinstance(error.get("code"), bool)
        and isinstance(error.get("message"), str)
    )

def valid_response(message: dict[str, Any]) -> bool:
    if message.get("jsonrpc") != "2.0":
        return False
    if "method" in message:
        return isinstance(message["method"], str) and "result" not in message and "error" not in message
    if "id" not in message or not valid_request_id(message["id"]):
        return False
    has_result = "result" in message
    has_error = "error" in message
    return has_result != has_error and (not has_error or valid_error(message["error"]))


def emit(message: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message, separators=(",", ":"), allow_nan=False) + "\n")
    sys.stdout.flush()


def send_request(message: dict[str, Any], session_id: str | None) -> str | None:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
        "User-Agent": "omp-exa-mcp/1.0",
        "x-api-key": KEY_MARKER,
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    request = Request(
        ENDPOINT,
        data=json.dumps(message, separators=(",", ":"), allow_nan=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    has_request_id = "id" in message
    request_id = message.get("id")
    try:
        with urlopen(request, timeout=60) as response:
            next_session = response.headers.get("Mcp-Session-Id") or session_id
            if not has_request_id:
                return next_session
            matched = False
            for response_message in response_messages(response):
                if not valid_response(response_message):
                    continue
                emit(response_message)
                if (
                    response_message.get("id") == request_id
                    and ("result" in response_message or "error" in response_message)
                ):
                    matched = True
                    break
            if not matched:
                emit_error(request_id, -32603, "Exa MCP returned no matching JSON-RPC response")
            return next_session
    except HTTPError as error:
        try:
            body = error.read(MAX_ERROR_BYTES + 1).decode("utf-8", errors="replace")
        except (HTTPException, OSError):
            body = ""
        if len(body) > MAX_ERROR_BYTES:
            body = body[:MAX_ERROR_BYTES] + "..."
        if has_request_id:
            emit_error(request_id, -32000, f"Exa MCP HTTP {error.code}: {body[:500]}")
        return session_id
    except ResponseTooLarge as error:
        if has_request_id:
            emit_error(request_id, -32002, f"Exa MCP response too large: {error}")
        return session_id
    except (HTTPException, TimeoutError, URLError, OSError) as error:
        if has_request_id:
            emit_error(request_id, -32001, f"Exa MCP unavailable: {error}")
        return session_id


def main() -> int:
    session_id: str | None = None
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line, parse_float=parse_json_float, parse_constant=reject_json_constant)
        except (json.JSONDecodeError, ValueError):
            emit_error(None, -32700, "Parse error")
            continue
        request_id = message.get("id") if isinstance(message, dict) and valid_request_id(message.get("id")) else None
        if not valid_request(message):
            emit_error(request_id, -32600, "Invalid Request")
            continue
        session_id = send_request(message, session_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
