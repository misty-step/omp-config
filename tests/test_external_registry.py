from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

import external_registry


class FirstPartySkillLinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="omp-first-party-links-")
        temp_root = Path(self.temp.name)
        self.root = temp_root / "repo"
        self.package_root = temp_root / "harness-primitives"
        skills = self.root / "global" / "skills"
        (self.root / "global" / "external").mkdir(parents=True)
        skills.mkdir(parents=True)
        (self.package_root / "skills" / "research-core").mkdir(parents=True)
        (self.package_root / "skills" / "deliver-core").mkdir(parents=True)
        (self.package_root / "package.json").write_text(
            json.dumps({"name": "@misty-step/harness-primitives"}), encoding="utf-8"
        )
        for name in ("research-core", "deliver-core"):
            (self.package_root / "skills" / name / "SKILL.md").write_text(
                f"name: {name}\n", encoding="utf-8"
            )
            (skills / name).symlink_to(
                self.package_root / "skills" / name, target_is_directory=True
            )
        (self.root / "global" / "external" / "registry.yaml").write_text(
            "sources:\n  - repo: default\n    default: true\n", encoding="utf-8"
        )
        (self.root / "package.json").write_text(
            json.dumps(
                {
                    "name": "@misty-step/omp-config",
                    "dependencies": {
                        "@misty-step/harness-primitives": "file:../harness-primitives"
                    },
                    "omp": {
                        "firstPartySkillLinks": {
                            "global/skills/research-core": {
                                "package": "@misty-step/harness-primitives",
                                "target": "skills/research-core",
                            },
                            "global/skills/deliver-core": {
                                "package": "@misty-step/harness-primitives",
                                "target": "skills/deliver-core",
                            },
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        self.contract = SimpleNamespace(
            surface=lambda name: SimpleNamespace(source=skills),
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_mapped_links_resolve_to_declared_package_targets(self) -> None:
        external_registry.check_external_skills(self.contract)

    def test_package_identity_drift_is_rejected(self) -> None:
        package_manifest = self.package_root / "package.json"
        package_manifest.write_text(json.dumps({"name": "wrong-package"}), encoding="utf-8")
        with self.assertRaises(external_registry.ExternalRegistryError):
            external_registry.check_external_skills(self.contract)

    def test_unmapped_skill_symlink_is_rejected(self) -> None:
        skills = self.root / "global" / "skills"
        (skills / "unmapped").symlink_to(
            self.package_root / "skills" / "research-core", target_is_directory=True
        )
        with self.assertRaises(external_registry.ExternalRegistryError):
            external_registry.check_external_skills(self.contract)


if __name__ == "__main__":
    unittest.main()
