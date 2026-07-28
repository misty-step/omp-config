from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "bin") not in sys.path:
    sys.path.insert(0, str(ROOT / "bin"))

import preflight


class PreflightTests(unittest.TestCase):
    def test_missing_siblings_are_reported_with_exact_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-preflight-") as temporary:
            workspace = Path(temporary) / "workspace"
            root = workspace / "omp-config"
            root.mkdir(parents=True)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {
                            "@misty-step/harness-primitives": "file:../harness-primitives",
                            "@misty-step/qa-users": "file:../qa-users",
                        }
                    }
                ),
                encoding="utf-8",
            )
            missing = preflight.missing_first_party_packages(root)
            self.assertEqual(
                missing,
                [
                    ("@misty-step/harness-primitives", (root.parent / "harness-primitives").resolve(strict=False)),
                    ("@misty-step/qa-users", (root.parent / "qa-users").resolve(strict=False)),
                ],
            )

    def test_existing_siblings_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-preflight-") as temporary:
            workspace = Path(temporary) / "workspace"
            root = workspace / "omp-config"
            root.mkdir(parents=True)
            for name, package_name in (
                ("harness-primitives", "@misty-step/harness-primitives"),
                ("qa-users", "@misty-step/qa-users"),
            ):
                package = root.parent / name
                package.mkdir()
                (package / "package.json").write_text(json.dumps({"name": package_name}), encoding="utf-8")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {
                            "@misty-step/harness-primitives": "file:../harness-primitives",
                            "@misty-step/qa-users": "file:../qa-users",
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(preflight.missing_first_party_packages(root), [])


if __name__ == "__main__":
    unittest.main()
