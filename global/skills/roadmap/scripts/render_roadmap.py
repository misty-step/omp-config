#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from validate_roadmap import validate

DATA_BLOCK = re.compile(
    r"(<script\b[^>]*\bid=[\"']roadmap-data[\"'][^>]*>).*?(</script>)",
    re.IGNORECASE | re.DOTALL,
)
MARKER = "__ROADMAP_DATA__"


def encode(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def render(data_path: Path, output_path: Path) -> tuple[int, int]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    encoded = encode(data)

    if output_path.exists():
        source = output_path.read_text(encoding="utf-8")
        if len(DATA_BLOCK.findall(source)) != 1:
            raise ValueError("existing artifact must contain one roadmap-data script")
        rendered = DATA_BLOCK.sub(lambda match: f"{match.group(1)}\n{encoded}\n{match.group(2)}", source)
    else:
        template = Path(__file__).resolve().parents[1] / "templates" / "ROADMAP.html"
        source = template.read_text(encoding="utf-8")
        if source.count(MARKER) != 1:
            raise ValueError("roadmap template must contain one data marker")
        rendered = source.replace(MARKER, f"\n{encoded}\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary.write(rendered)
        temporary_path = Path(temporary.name)

    try:
        result = validate(temporary_path)
        temporary_path.replace(output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_roadmap.py DATA.json OUTPUT.html", file=sys.stderr)
        return 2
    data_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    try:
        item_count, coverage_count = render(data_path, output_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ROADMAP RENDER ERROR: {error}", file=sys.stderr)
        return 1
    print(f"ROADMAP RENDERED: {output_path} ({item_count} items, {coverage_count} coverage topics)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
