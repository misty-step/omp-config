#!/usr/bin/env python3
"""Local Firecrawl MCP server over Mint REST (stdio JSON-RPC)."""

from __future__ import annotations

import json
import math
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = "http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev"
KEY_MARKER = "__mint.firecrawl.default__"
PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "firecrawl-mint"
SERVER_VERSION = "1.0.0"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
DEFAULT_TIMEOUT = 90
CRAWL_POLL_SECONDS = 2.0
CRAWL_MAX_WAIT_SECONDS = 120.0


def reject_json_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant: {value}")


def parse_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON number: {value}")
    return parsed


def emit(message: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message, separators=(",", ":"), allow_nan=False) + "\n")
    sys.stdout.flush()


def emit_result(request_id: Any, result: Any) -> None:
    emit({"jsonrpc": "2.0", "id": request_id, "result": result})


def emit_error(request_id: Any, code: int, message: str) -> None:
    emit(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
    )


def text_content(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": False}


def error_content(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def api_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    data = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {KEY_MARKER}",
        "User-Agent": f"{SERVER_NAME}/{SERVER_VERSION}",
    }
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(f"{API}/{path.lstrip('/')}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise ValueError(f"response exceeded {MAX_RESPONSE_BYTES} bytes")
            if not body:
                return {}
            parsed = json.loads(body.decode("utf-8"))
            if not isinstance(parsed, dict):
                raise ValueError("Firecrawl response was not a JSON object")
            return parsed
    except HTTPError as error:
        detail = error.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"Firecrawl HTTP {error.code}: {detail[:800]}") from error
    except (TimeoutError, URLError, OSError) as error:
        raise RuntimeError(f"Firecrawl unavailable: {error}") from error


def tool_defs() -> list[dict[str, Any]]:
    return [
        {
            "name": "firecrawl_scrape",
            "description": (
                "Scrape one known URL into clean markdown or structured fields. "
                "Use for page content acquisition, not interactive UI proof."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "formats": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["markdown"],
                    },
                    "onlyMainContent": {"type": "boolean", "default": True},
                    "maxAge": {"type": "integer"},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
        {
            "name": "firecrawl_map",
            "description": (
                "Map a site or docs root to discovered URLs. "
                "Use before crawl when you need a bounded page list."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "default": 20},
                    "search": {"type": "string"},
                    "includeSubdomains": {"type": "boolean", "default": False},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
        {
            "name": "firecrawl_search",
            "description": (
                "Search the web through Firecrawl and optionally return page content. "
                "Prefer Exa for code and technical discovery; use this for page-backed search."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "default": 5},
                    "tbs": {"type": "string"},
                    "scrapeOptions": {"type": "object"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
        {
            "name": "firecrawl_crawl",
            "description": (
                "Crawl a bounded docs site or path tree. "
                "Always set limit. Prefer map + selective scrape for small jobs."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "default": 10},
                    "maxDiscoveryDepth": {"type": "integer", "minimum": 0, "default": 2},
                    "includePaths": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "excludePaths": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "allowExternalLinks": {"type": "boolean", "default": False},
                    "scrapeOptions": {"type": "object"},
                    "wait": {"type": "boolean", "default": True},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    ]


def call_scrape(args: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "url": args["url"],
        "formats": args.get("formats") or ["markdown"],
        "onlyMainContent": args.get("onlyMainContent", True),
    }
    if "maxAge" in args:
        payload["maxAge"] = args["maxAge"]
    return api_request("POST", "v1/scrape", payload)


def call_map(args: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "url": args["url"],
        "limit": int(args.get("limit") or 20),
        "includeSubdomains": bool(args.get("includeSubdomains", False)),
    }
    if args.get("search"):
        payload["search"] = args["search"]
    return api_request("POST", "v1/map", payload)


def call_search(args: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "query": args["query"],
        "limit": int(args.get("limit") or 5),
    }
    if args.get("tbs"):
        payload["tbs"] = args["tbs"]
    if args.get("scrapeOptions"):
        payload["scrapeOptions"] = args["scrapeOptions"]
    return api_request("POST", "v1/search", payload)


def call_crawl(args: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "url": args["url"],
        "limit": int(args.get("limit") or 10),
        "maxDiscoveryDepth": int(args.get("maxDiscoveryDepth") or 2),
        "allowExternalLinks": bool(args.get("allowExternalLinks", False)),
        "scrapeOptions": args.get("scrapeOptions")
        or {"formats": ["markdown"], "onlyMainContent": True},
    }
    if args.get("includePaths"):
        payload["includePaths"] = args["includePaths"]
    if args.get("excludePaths"):
        payload["excludePaths"] = args["excludePaths"]
    started = api_request("POST", "v1/crawl", payload)
    if not args.get("wait", True):
        return started
    crawl_id = started.get("id")
    if not crawl_id:
        return started
    deadline = time.monotonic() + CRAWL_MAX_WAIT_SECONDS
    while time.monotonic() < deadline:
        status = api_request("GET", f"v1/crawl/{crawl_id}")
        state = str(status.get("status") or "").lower()
        if state in {"completed", "failed", "cancelled"}:
            return status
        time.sleep(CRAWL_POLL_SECONDS)
    return {
        "success": False,
        "id": crawl_id,
        "status": "timeout",
        "message": f"crawl did not finish within {int(CRAWL_MAX_WAIT_SECONDS)}s",
        "start": started,
    }


TOOLS = {
    "firecrawl_scrape": call_scrape,
    "firecrawl_map": call_map,
    "firecrawl_search": call_search,
    "firecrawl_crawl": call_crawl,
}


def handle_initialize(request_id: Any, _params: dict[str, Any]) -> None:
    emit_result(
        request_id,
        {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": (
                "Mint-backed Firecrawl tools for scrape, map, search, and bounded crawl. "
                "Use Exa for technical discovery. Use agent-browser or the builtin browser "
                "for interactive pages."
            ),
        },
    )


def handle_tools_list(request_id: Any, _params: dict[str, Any]) -> None:
    emit_result(request_id, {"tools": tool_defs()})


def handle_tools_call(request_id: Any, params: dict[str, Any]) -> None:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if not isinstance(name, str) or name not in TOOLS:
        emit_result(request_id, error_content(f"Unknown tool: {name!r}"))
        return
    if not isinstance(arguments, dict):
        emit_result(request_id, error_content("Tool arguments must be an object"))
        return
    try:
        result = TOOLS[name](arguments)
        emit_result(
            request_id,
            text_content(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)),
        )
    except Exception as error:  # noqa: BLE001 - surface tool failure to MCP client
        emit_result(request_id, error_content(str(error)))


def handle_ping(request_id: Any, _params: dict[str, Any]) -> None:
    emit_result(request_id, {})


HANDLERS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
    "ping": handle_ping,
}


def valid_request_id(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, float):
        return math.isfinite(value)
    return isinstance(value, (str, int))


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(
                line,
                parse_float=parse_json_float,
                parse_constant=reject_json_constant,
            )
        except (json.JSONDecodeError, ValueError):
            emit_error(None, -32700, "Parse error")
            continue
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            emit_error(None, -32600, "Invalid Request")
            continue
        method = message.get("method")
        request_id = message.get("id") if "id" in message else None
        if not isinstance(method, str):
            if valid_request_id(request_id):
                emit_error(request_id, -32600, "Invalid Request")
            continue
        # notifications have no id
        if "id" not in message:
            if method in {"notifications/initialized", "notifications/cancelled"}:
                continue
            continue
        if not valid_request_id(request_id):
            emit_error(None, -32600, "Invalid Request")
            continue
        handler = HANDLERS.get(method)
        if handler is None:
            emit_error(request_id, -32601, f"Method not found: {method}")
            continue
        params = message.get("params") or {}
        if params is None:
            params = {}
        if not isinstance(params, dict):
            emit_error(request_id, -32602, "Invalid params")
            continue
        handler(request_id, params)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
