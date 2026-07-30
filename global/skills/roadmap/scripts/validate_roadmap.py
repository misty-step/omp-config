#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

HORIZONS = {"current", "next", "later", "explore"}
ITEM_FIELDS = ("id", "horizon", "title", "outcome", "proof", "question", "research")
VISION_FIELDS = ("purpose", "target", "humanRole", "systemRule")
REMOTE_URL = re.compile(r"^(?:https?:)?//", re.IGNORECASE)
ITEM_ID = re.compile(r"^R[0-9]{2,}$")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class RoadmapHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_data = False
        self.data_blocks: list[str] = []
        self._parts: list[str] = []
        self.remote_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "script" and values.get("id") == "roadmap-data":
            self._in_data = True
            self._parts = []
        asset = values.get("src") if tag in {"script", "img", "iframe", "source"} else None
        if tag == "link":
            asset = values.get("href")
        if asset and REMOTE_URL.match(asset):
            self.remote_assets.append(asset)

    def handle_data(self, data: str) -> None:
        if self._in_data:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_data:
            self.data_blocks.append("".join(self._parts))
            self._in_data = False
            self._parts = []


def fail(message: str) -> None:
    raise ValueError(message)


def require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{name} must be an object")
    return value


def require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{name} must be a list")
    return value


def require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{name} must be non-empty text")
    return value.strip()


def validate(path: Path) -> tuple[int, int]:
    source = path.read_text(encoding="utf-8")
    if "__ROADMAP_DATA__" in source:
        fail("template marker remains")
    if re.search(r"@import\s+url|url\(\s*['\"]?(?:https?:)?//", source, re.IGNORECASE):
        fail("remote CSS asset found")

    parser = RoadmapHTMLParser()
    parser.feed(source)
    if parser.remote_assets:
        fail(f"remote asset found: {parser.remote_assets[0]}")
    if len(parser.data_blocks) != 1:
        fail("exactly one roadmap-data script is required")

    try:
        data = require_object(json.loads(parser.data_blocks[0]), "roadmap data")
    except json.JSONDecodeError as error:
        fail(f"roadmap data is not valid JSON: {error.msg}")

    if data.get("schemaVersion") != 1:
        fail("schemaVersion must equal 1")
    require_text(data.get("project"), "project")
    updated = require_text(data.get("updated"), "updated")
    if not DATE.fullmatch(updated):
        fail("updated must use YYYY-MM-DD")
    require_text(data.get("visionSource"), "visionSource")

    vision = require_object(data.get("vision"), "vision")
    for field in VISION_FIELDS:
        require_text(vision.get(field), f"vision.{field}")

    measures = require_list(data.get("measures"), "measures")
    if not 3 <= len(measures) <= 6:
        fail("measures must contain three to six entries")
    for index, value in enumerate(measures):
        measure = require_object(value, f"measures[{index}]")
        require_text(measure.get("name"), f"measures[{index}].name")
        require_text(measure.get("description"), f"measures[{index}].description")

    work_authority = require_object(data.get("workAuthority"), "workAuthority")
    require_text(work_authority.get("name"), "workAuthority.name")
    require_text(work_authority.get("description"), "workAuthority.description")

    items = require_list(data.get("items"), "items")
    if not 5 <= len(items) <= 12:
        fail("items must contain five to twelve entries")

    identifiers: set[str] = set()
    coverage: set[str] = set()
    current_count = 0
    for index, value in enumerate(items):
        item = require_object(value, f"items[{index}]")
        for field in ITEM_FIELDS:
            require_text(item.get(field), f"items[{index}].{field}")
        identifier = item["id"].strip()
        if not ITEM_ID.fullmatch(identifier):
            fail(f"items[{index}].id must match R followed by at least two digits")
        if identifier in identifiers:
            fail(f"duplicate item identifier: {identifier}")
        identifiers.add(identifier)

        horizon = item["horizon"].strip()
        if horizon not in HORIZONS:
            fail(f"items[{index}].horizon is not valid: {horizon}")
        current_count += horizon == "current"

        topics = require_list(item.get("coverage"), f"items[{index}].coverage")
        if not topics:
            fail(f"items[{index}].coverage must not be empty")
        for topic_value in topics:
            topic = require_text(topic_value, f"items[{index}].coverage entry")
            if topic in coverage:
                fail(f"duplicate coverage topic: {topic}")
            coverage.add(topic)

    if current_count != 1:
        fail("items must contain exactly one current item")

    exclusions = require_list(data.get("exclusions"), "exclusions")
    exclusion_set: set[str] = set()
    for index, value in enumerate(exclusions):
        exclusion = require_text(value, f"exclusions[{index}]")
        if exclusion in coverage or exclusion in exclusion_set:
            fail(f"duplicate or covered exclusion: {exclusion}")
        exclusion_set.add(exclusion)

    return len(items), len(coverage)


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "ROADMAP.html")
    try:
        item_count, coverage_count = validate(path)
    except (OSError, ValueError) as error:
        print(f"ROADMAP ERROR: {error}", file=sys.stderr)
        return 1
    print(f"ROADMAP OK: {path} ({item_count} items, {coverage_count} coverage topics, one current item)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
