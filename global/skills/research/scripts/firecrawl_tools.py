#!/usr/bin/env python3
"""Deterministic Firecrawl REST clients through Mint."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

VERSION = "1.0.0"
MINT_API = "http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.firecrawl.dev"
KEY_MARKER = "__mint.firecrawl.default__"
CRAWL_POLL_SECONDS = 2.0
CRAWL_MAX_WAIT_SECONDS = 120.0


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> int:
    data = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {KEY_MARKER}",
    }
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(
        f"{MINT_API}/{path.lstrip('/')}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=90) as response:
            sys.stdout.buffer.write(response.read())
            sys.stdout.buffer.write(b"\n")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(body or f"Firecrawl request failed with HTTP {error.code}", file=sys.stderr)
        return 1
    except (TimeoutError, URLError, OSError):
        print("Firecrawl request failed: upstream unavailable", file=sys.stderr)
        return 1
    return 0


def request_json_value(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {KEY_MARKER}",
    }
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(
        f"{MINT_API}/{path.lstrip('/')}",
        data=data,
        headers=headers,
        method=method,
    )
    with urlopen(request, timeout=90) as response:
        parsed = json.loads(response.read().decode("utf-8"))
    if not isinstance(parsed, dict):
        raise RuntimeError("Firecrawl response was not a JSON object")
    return parsed


def scrape_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="firecrawl-scrape",
        description="Scrape one URL through Firecrawl and Mint.",
    )
    parser.add_argument("url", help="page URL")
    parser.add_argument(
        "--format",
        dest="formats",
        action="append",
        default=None,
        help="output format (repeatable); default markdown",
    )
    parser.add_argument("--full", action="store_true", help="keep full page, not main content only")
    parser.add_argument("--version", action="version", version=f"firecrawl-scrape {VERSION}")
    return parser


def run_scrape(argv: list[str]) -> int:
    args = scrape_parser().parse_args(argv)
    payload: dict[str, Any] = {
        "url": args.url,
        "formats": args.formats or ["markdown"],
        "onlyMainContent": not args.full,
    }
    return request_json("POST", "v1/scrape", payload)


def map_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="firecrawl-map",
        description="Map a site through Firecrawl and Mint.",
    )
    parser.add_argument("url", help="site or docs root URL")
    parser.add_argument("--limit", type=positive_int, default=20)
    parser.add_argument("--search", help="optional link filter query")
    parser.add_argument("--subdomains", action="store_true")
    parser.add_argument("--version", action="version", version=f"firecrawl-map {VERSION}")
    return parser


def run_map(argv: list[str]) -> int:
    args = map_parser().parse_args(argv)
    payload: dict[str, Any] = {
        "url": args.url,
        "limit": args.limit,
        "includeSubdomains": args.subdomains,
    }
    if args.search:
        payload["search"] = args.search
    return request_json("POST", "v1/map", payload)


def search_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="firecrawl-search",
        description="Search through Firecrawl and Mint.",
    )
    parser.add_argument("query", nargs="+", help="search query")
    parser.add_argument("--limit", type=positive_int, default=5)
    parser.add_argument("--version", action="version", version=f"firecrawl-search {VERSION}")
    return parser


def run_search(argv: list[str]) -> int:
    args = search_parser().parse_args(argv)
    payload = {"query": " ".join(args.query), "limit": args.limit}
    return request_json("POST", "v1/search", payload)


def crawl_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="firecrawl-crawl",
        description="Crawl a bounded site through Firecrawl and Mint.",
    )
    parser.add_argument("url", help="start URL")
    parser.add_argument("--limit", type=positive_int, default=10)
    parser.add_argument("--depth", type=int, default=2, help="max discovery depth")
    parser.add_argument("--no-wait", action="store_true", help="return crawl id without polling")
    parser.add_argument("--version", action="version", version=f"firecrawl-crawl {VERSION}")
    return parser


def run_crawl(argv: list[str]) -> int:
    args = crawl_parser().parse_args(argv)
    payload: dict[str, Any] = {
        "url": args.url,
        "limit": args.limit,
        "maxDiscoveryDepth": args.depth,
        "allowExternalLinks": False,
        "scrapeOptions": {"formats": ["markdown"], "onlyMainContent": True},
    }
    try:
        started = request_json_value("POST", "v1/crawl", payload)
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(body or f"Firecrawl request failed with HTTP {error.code}", file=sys.stderr)
        return 1
    except (TimeoutError, URLError, OSError, RuntimeError, json.JSONDecodeError):
        print("Firecrawl request failed: upstream unavailable", file=sys.stderr)
        return 1
    if args.no_wait or not started.get("id"):
        sys.stdout.write(json.dumps(started) + "\n")
        return 0
    crawl_id = started["id"]
    deadline = time.monotonic() + CRAWL_MAX_WAIT_SECONDS
    try:
        while time.monotonic() < deadline:
            status = request_json_value("GET", f"v1/crawl/{crawl_id}")
            state = str(status.get("status") or "").lower()
            if state in {"completed", "failed", "cancelled"}:
                sys.stdout.write(json.dumps(status) + "\n")
                return 0 if state == "completed" else 1
            time.sleep(CRAWL_POLL_SECONDS)
    except (HTTPError, TimeoutError, URLError, OSError, RuntimeError, json.JSONDecodeError):
        print("Firecrawl crawl poll failed", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "success": False,
                "id": crawl_id,
                "status": "timeout",
                "message": f"crawl did not finish within {int(CRAWL_MAX_WAIT_SECONDS)}s",
            }
        ),
        file=sys.stderr,
    )
    return 1


def resolve_command(argv: list[str] | None) -> tuple[str, list[str]]:
    args = list(sys.argv[1:] if argv is None else argv)
    name = Path(sys.argv[0]).name
    known = {
        "firecrawl-scrape",
        "firecrawl-map",
        "firecrawl-search",
        "firecrawl-crawl",
    }
    if name in known:
        return name, args
    if args and args[0] in known:
        return args[0], args[1:]
    return name, args


def main(argv: list[str] | None = None) -> int:
    name, args = resolve_command(argv)
    if name == "firecrawl-scrape":
        return run_scrape(args)
    if name == "firecrawl-map":
        return run_map(args)
    if name == "firecrawl-search":
        return run_search(args)
    if name == "firecrawl-crawl":
        return run_crawl(args)
    print(
        "Invoke as firecrawl-scrape|map|search|crawl, or "
        "python3 firecrawl_tools.py firecrawl-scrape <url>",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
