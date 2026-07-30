from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "global" / "skills" / "roadmap"
SCRIPTS = SKILL / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from render_roadmap import render
from validate_roadmap import validate


def roadmap_data() -> dict[str, object]:
    items = []
    for number, horizon in enumerate(("current", "next", "next", "later", "explore"), start=1):
        items.append(
            {
                "id": f"R{number:02d}",
                "horizon": horizon,
                "title": f"Reach outcome {number}",
                "outcome": f"The project reaches outcome {number}.",
                "proof": f"A named check proves outcome {number}.",
                "question": f"Which decision settles outcome {number}?",
                "research": f"Compare two options for outcome {number}.",
                "coverage": [f"Source concern {number}"],
            }
        )
    return {
        "schemaVersion": 1,
        "project": "Example project",
        "updated": "2026-07-30",
        "visionSource": "inline",
        "vision": {
            "purpose": "The project gives one useful result.",
            "target": "Users get the result without repeated operator work.",
            "humanRole": "Humans set intent and review measured outcomes.",
            "systemRule": "The system keeps authority and proof separate.",
        },
        "measures": [
            {"name": "Time", "description": "Human minutes per outcome"},
            {"name": "Proof", "description": "Outcomes with complete proof"},
            {"name": "Value", "description": "Measured value per outcome"},
        ],
        "workAuthority": {
            "name": "Example ledger",
            "description": "Tasks, attempts, relations, and proof records",
        },
        "items": items,
        "exclusions": [],
    }


class RoadmapSkillTests(unittest.TestCase):
    def render(self, data: dict[str, object]) -> Path:
        template = (SKILL / "templates" / "ROADMAP.html").read_text(encoding="utf-8")
        self.assertEqual(template.count("__ROADMAP_DATA__"), 1)
        directory = tempfile.TemporaryDirectory(prefix="roadmap-skill-")
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "ROADMAP.html"
        path.write_text(template.replace("__ROADMAP_DATA__", json.dumps(data)), encoding="utf-8")
        return path

    def test_template_renders_a_valid_self_contained_artifact(self) -> None:
        path = self.render(roadmap_data())
        self.assertEqual(validate(path), (5, 5))

    def test_renderer_preserves_layout_during_a_data_update(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="roadmap-render-")
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        data_path = root / "data.json"
        output_path = root / "ROADMAP.html"
        data = roadmap_data()
        data_path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(render(data_path, output_path), (5, 5))
        output_path.write_text(
            output_path.read_text(encoding="utf-8").replace("<body>", "<body><!-- keep-layout -->", 1),
            encoding="utf-8",
        )
        data["project"] = "Updated example"
        data_path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(render(data_path, output_path), (5, 5))
        rendered = output_path.read_text(encoding="utf-8")
        self.assertIn("<!-- keep-layout -->", rendered)
        self.assertIn("\"project\": \"Updated example\"", rendered)

    def test_factory_example_preserves_all_thread_topics(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="roadmap-example-")
        self.addCleanup(directory.cleanup)
        output_path = Path(directory.name) / "ROADMAP.html"
        data_path = SKILL / "examples" / "dark-software-factory.json"
        self.assertEqual(render(data_path, output_path), (10, 25))

    def test_validator_rejects_multiple_current_items(self) -> None:
        data = roadmap_data()
        data["items"][1]["horizon"] = "current"  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "exactly one current item"):
            validate(self.render(data))

    def test_validator_rejects_duplicate_coverage(self) -> None:
        data = roadmap_data()
        data["items"][1]["coverage"] = ["Source concern 1"]  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "duplicate coverage topic"):
            validate(self.render(data))


if __name__ == "__main__":
    unittest.main()
