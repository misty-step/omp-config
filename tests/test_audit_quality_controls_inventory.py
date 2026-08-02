from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "global/skills/audit-quality-controls/scripts/inventory.py"


class InventoryTests(unittest.TestCase):
    def test_reports_effective_hooks_and_unwired_versioned_hook(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True)
            (repo / ".githooks").mkdir()
            (repo / ".githooks/pre-push").write_text("#!/bin/sh\nexit 0\n")
            (repo / ".github/workflows").mkdir(parents=True)
            (repo / ".github/workflows/ci.yml").write_text("uses: action/example@main\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            before = subprocess.run(["git", "status", "--porcelain"], cwd=repo, text=True, stdout=subprocess.PIPE, check=True).stdout
            output = subprocess.run(["python3", str(SCRIPT), str(repo)], text=True, stdout=subprocess.PIPE, check=True).stdout
            after = subprocess.run(["git", "status", "--porcelain"], cwd=repo, text=True, stdout=subprocess.PIPE, check=True).stdout
            data = json.loads(output)
            self.assertIn(".githooks/pre-push", data["surfaces"]["hooks"])
            self.assertIn(".github/workflows/ci.yml", data["surfaces"]["ci"])
            self.assertIsNone(data["effective_hooks"]["configured_core_hooks_path"])
            self.assertFalse(data["effective_hooks"]["pre_push_executable"])
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
