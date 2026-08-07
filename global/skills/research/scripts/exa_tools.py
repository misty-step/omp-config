#!/usr/bin/env python3
"""Small deterministic Exa REST clients for agent shell environments.

All requests use the Mint proxy and a value-free credential marker.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

VERSION = "1.0.0"
MINT_EXA_API = "http://mint.tail5f5eb4.ts.net:4949/proxy/https/api.exa.ai"
EXA_KEY_MARKER = "__mint.exa.default__"


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def request_json(path: str, payload: dict[str, Any]) -> int:
    request = Request(
        f"{MINT_EXA_API}/{path}",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": EXA_KEY_MARKER,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            sys.stdout.buffer.write(response.read())
            sys.stdout.buffer.write(b"\n")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(body or f"Exa request failed with HTTP {error.code}", file=sys.stderr)
        return 1
    except (TimeoutError, URLError, OSError):
        print("Exa request failed: upstream unavailable", file=sys.stderr)
        return 1
    return 0


def search_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exa-search",
        description="Search the web through Exa and the Mint credential broker.",
    )
    parser.add_argument("query", nargs="+", help="natural-language search query")
    parser.add_argument("--num", type=positive_int, default=5, help="number of results")
    parser.add_argument("--chars", type=positive_int, default=1000, help="maximum text characters per result")
    parser.add_argument("--type", choices=("instant", "fast", "auto", "deep-lite", "deep", "deep-reasoning"), default="auto")
    parser.add_argument("--category", help="Exa search category")
    parser.add_argument("--start-published-date", dest="start_published_date")
    parser.add_argument("--include-domain", dest="include_domains", action="append")
    parser.add_argument("--exclude-domain", dest="exclude_domains", action="append")
    parser.add_argument("--no-autoprompt", action="store_true")
    parser.add_argument("--version", action="version", version=f"exa-search {VERSION}")
    return parser


def run_search(argv: list[str]) -> int:
    args = search_parser().parse_args(argv)
    payload: dict[str, Any] = {
        "query": " ".join(args.query),
        "type": args.type,
        "numResults": args.num,
        "useAutoprompt": not args.no_autoprompt,
        "contents": {"text": {"maxCharacters": args.chars}},
    }
    for key, value in (
        ("category", args.category),
        ("startPublishedDate", args.start_published_date),
        ("includeDomains", args.include_domains),
        ("excludeDomains", args.exclude_domains),
    ):
        if value:
            payload[key] = value
    return request_json("search", payload)


def fetch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exa-fetch",
        description="Fetch known URLs through Exa and the Mint credential broker.",
    )
    parser.add_argument("urls", nargs="+", help="one or more URLs")
    parser.add_argument("--chars", type=positive_int, default=2000, help="maximum text characters per URL")
    parser.add_argument("--version", action="version", version=f"exa-fetch {VERSION}")
    return parser


def run_fetch(argv: list[str]) -> int:
    args = fetch_parser().parse_args(argv)
    return request_json(
        "contents",
        {"ids": args.urls, "text": {"maxCharacters": args.chars}},
    )


def resolve_command(argv: list[str] | None) -> tuple[str, list[str]]:
    args = list(sys.argv[1:] if argv is None else argv)
    name = Path(sys.argv[0]).name
    known = {"exa-search", "exa-fetch"}
    if name in known:
        return name, args
    if args and args[0] in known:
        return args[0], args[1:]
    return name, args


def main(argv: list[str] | None = None) -> int:
    name, args = resolve_command(argv)
    if name == "exa-search":
        return run_search(args)
    if name == "exa-fetch":
        return run_fetch(args)
    print(
        "Invoke as exa-search|exa-fetch, or python3 exa_tools.py exa-search <query>",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
