from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

from external_registry import ExternalRegistryError, check_external_skills


LOCAL_SKILL_CORES = (
    "research-core",
    "deliver-core",
    "qa-users",
    "simplified-technical-english",
)
DEPENDENCY_SECTIONS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)


class SkillOwnershipTests(unittest.TestCase):
    def test_package_manifest_has_no_file_dependencies_or_first_party_skill_links(self) -> None:
        manifest = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        for section in DEPENDENCY_SECTIONS:
            dependencies = manifest.get(section, {})
            self.assertIsInstance(dependencies, dict, section)
            self.assertFalse(
                any(
                    isinstance(version, str) and version.startswith("file:")
                    for version in dependencies.values()
                ),
                f"{section} must not use file: dependencies",
            )
        omp = manifest.get("omp", {})
        self.assertIsInstance(omp, dict)
        self.assertNotIn("firstPartySkillLinks", omp)

    def test_local_skill_cores_are_real_directories_with_skill_files(self) -> None:
        skills = ROOT / "global" / "skills"
        for name in LOCAL_SKILL_CORES:
            skill = skills / name
            self.assertTrue(skill.is_dir(), skill)
            self.assertFalse(skill.is_symlink(), skill)
            self.assertTrue((skill / "SKILL.md").is_file(), skill / "SKILL.md")

    def test_external_registry_rejects_undeclared_skill_symlinks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-skill-ownership-") as temporary:
            root = Path(temporary)
            external = root / "global" / "external"
            shutil.copytree(
                ROOT / "global" / "external",
                external,
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            skills = root / "global" / "skills"
            skills.mkdir(parents=True)
            (skills / "undeclared").symlink_to(
                external / "cursor-thermos",
                target_is_directory=True,
            )
            contract = SimpleNamespace(
                surface=lambda name: SimpleNamespace(source=skills),
            )

            with self.assertRaises(ExternalRegistryError):
                check_external_skills(contract)


if __name__ == "__main__":
    unittest.main()
