from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "global" / "skills"
CATALOG = ROOT / "global" / "skill-catalog.json"


class SkillCatalogTests(unittest.TestCase):
    def test_catalog_classifies_every_surviving_skill_and_records_workflow_limits(self) -> None:
        document = json.loads(CATALOG.read_text())
        entries = document["skills"]
        directories = {path.name for path in SKILLS.iterdir() if path.is_dir()}

        self.assertEqual(set(entries), directories)
        allowed = {
            "evidence-backed workflow",
            "narrow live operations contract",
            "merged guidance",
        }
        for name, entry in entries.items():
            self.assertIn(entry["classification"], allowed, name)
            self.assertTrue(entry["basis"].strip(), name)
            if entry["classification"] == "evidence-backed workflow":
                evidence = entry["evidence"]
                self.assertGreaterEqual(evidence["fixtures"], 2, name)
                self.assertGreaterEqual(evidence["trials_per_cell"], 1, name)
                self.assertEqual(evidence["verdict"], "keep", name)
                self.assertTrue(evidence["limits"].strip(), name)

    def test_local_skill_payloads_have_no_exact_external_copy(self) -> None:
        local_hashes = {
            hashlib.sha256((path / "SKILL.md").read_bytes()).hexdigest()
            for path in SKILLS.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }
        external_hashes = {
            hashlib.sha256((path / "SKILL.md").read_bytes()).hexdigest()
            for path in (ROOT / "global" / "external").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }
        self.assertTrue(local_hashes.isdisjoint(external_hashes))


if __name__ == "__main__":
    unittest.main()
