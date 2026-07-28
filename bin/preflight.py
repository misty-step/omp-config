#!/usr/bin/env python3
"""Fail fast when a standalone checkout lacks declared first-party siblings."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def missing_first_party_packages(root: Path) -> list[tuple[str, Path]]:
    manifest_path = root / "package.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dependencies = manifest.get("dependencies", {})
    if not isinstance(dependencies, dict):
        return []
    missing: list[tuple[str, Path]] = []
    for name, spec in dependencies.items():
        if not isinstance(name, str) or not isinstance(spec, str) or not spec.startswith("file:"):
            continue
        package_root = (root / Path(spec[5:])).resolve(strict=False)
        if not (package_root / "package.json").is_file():
            missing.append((name, package_root))
    return missing


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = missing_first_party_packages(root)
    if not missing:
        return 0
    print("omp-config preinstall: missing declared first-party sibling package(s):", file=sys.stderr)
    for name, package_root in missing:
        print(f"  {name}: expected {package_root / 'package.json'}", file=sys.stderr)
    print(
        "Bootstrap a standalone checkout with the sibling repositories at those exact paths "
        "before running npm install; omp-config does not duplicate those packages.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
