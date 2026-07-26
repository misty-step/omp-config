from __future__ import annotations

import dataclasses
import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
SKILLS = ROOT / "global" / "skills"


def _load_check() -> object:
    """Import bin/check as a module so tests exercise the real gate function."""
    loader = SourceFileLoader("omp_check", str(BIN / "check"))
    spec = importlib.util.spec_from_loader("omp_check", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # bin/check does `from config_contract import ...` from its own directory.
    sys.path.insert(0, str(BIN))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


check = _load_check()


class _FakeSurface:
    def __init__(self, source: Path) -> None:
        self.source = source


class _FakeContract:
    """Minimal stand-in: check_skill_catalog only touches surface('skills').source."""

    def __init__(self, skills_source: Path) -> None:
        self._skills_source = skills_source

    def surface(self, name: str) -> _FakeSurface:
        if name == "skills":
            return _FakeSurface(self._skills_source)
        raise AssertionError(f"unexpected surface {name!r}")


def _workflow_entry(**overrides) -> dict:
    entry = {
        "classification": "evidence-backed workflow",
        "basis": "keeps the gate honest",
        "evidence": {
            "report": "~/Development/crucible/runs/local/sweep/report.md",
            "fixtures": 2,
            "trials_per_cell": 1,
            "verdict": "keep",
            "limits": "one worker trial per arm; proxy result is unanchored",
        },
    }
    entry.update(overrides)
    return entry


def _valid_catalog() -> dict:
    return {
        "schema_version": "omp.skill-catalog.v1",
        "skills": {
            "alpha": _workflow_entry(),
            "beta": {"classification": "merged guidance", "basis": "doc"},
        },
    }


def _write_tree(root: Path, catalog_doc: dict, skill_names: list[str]) -> Path:
    """Lay out a temp repo root with a catalog, skills, and an empty external dir."""
    global_dir = root / "global"
    global_dir.mkdir()
    (global_dir / "skill-catalog.json").write_text(json.dumps(catalog_doc))
    skills = global_dir / "skills"
    skills.mkdir()
    for name in skill_names:
        directory = skills / name
        directory.mkdir()
        (directory / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: x\n---\nbody\n"
        )
    (global_dir / "external").mkdir()
    return skills


def _run_gate(tmp: Path, catalog_doc: dict, skill_names: list[str]) -> None:
    skills = _write_tree(tmp, catalog_doc, skill_names)
    contract = _FakeContract(skills)
    with patch.object(check, "ROOT", tmp):
        check.check_skill_catalog(contract, set(skill_names))


class SkillCatalogGateTests(unittest.TestCase):
    """Defend check_skill_catalog and check_presets: every rule has a test that
    fails if the rule is deleted, inverted, or unwired from check_tree."""

    def test_real_catalog_passes_the_real_gate(self) -> None:
        declared = {path.name for path in SKILLS.iterdir() if path.is_dir()}
        # check.ROOT already points at the real repo, so this drives the actual
        # catalog, the actual first-party skills, and the actual external tier.
        check.check_skill_catalog(_FakeContract(SKILLS), declared)

    def test_bin_check_passes_and_rejects_a_corrupt_catalog(self) -> None:
        # End-to-end defense of the check_tree -> check_skill_catalog callsite.
        # Runs against a tmpdir copy of the repo so the tracked catalog is never
        # mutated in place: a crash or SIGKILL mid-test cannot corrupt the tree
        # and parallel runs cannot race on the shared file.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            shutil.copytree(ROOT / "bin", repo / "bin")
            shutil.copytree(ROOT / "global", repo / "global")
            shutil.copy2(ROOT / "provenance.yaml", repo / "provenance.yaml")

            healthy = subprocess.run(
                [sys.executable, str(repo / "bin" / "check")],
                capture_output=True,
                cwd=repo,
            )
            self.assertEqual(healthy.returncode, 0, healthy.stderr.decode())
            self.assertIn(b"OMP source configuration OK", healthy.stdout)

            (repo / "global" / "skill-catalog.json").write_text(
                json.dumps({"schema_version": "not.the.schema", "skills": {}})
            )
            corrupt = subprocess.run(
                [sys.executable, str(repo / "bin" / "check")],
                capture_output=True,
                cwd=repo,
            )
        self.assertNotEqual(corrupt.returncode, 0)
        self.assertIn(b"schema_version", corrupt.stderr)

    def test_bad_schema_version_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["schema_version"] = "omp.skill-catalog.v0"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_workflow_without_crucible_report_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["alpha"]["evidence"]["report"] = "/tmp/elsewhere/report.md"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_non_workflow_with_evidence_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["beta"]["evidence"] = {"report": "crucible/x", "fixtures": 2}
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_invalid_classification_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["beta"]["classification"] = "magic"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_workflow_missing_evidence_block_is_rejected(self) -> None:
        catalog = _valid_catalog()
        del catalog["skills"]["alpha"]["evidence"]
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_workflow_with_too_few_fixtures_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["alpha"]["evidence"]["fixtures"] = 1
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_workflow_without_keep_verdict_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["alpha"]["evidence"]["verdict"] = "drop"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_entry_without_basis_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["beta"]["basis"] = "  "
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_catalog_skill_drift_is_rejected(self) -> None:
        catalog = _valid_catalog()
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            # declared skills differ from catalog keys
            _run_gate(Path(tmp), catalog, ["alpha"])

    def test_duplicate_payload_between_tiers_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            skills = _write_tree(tmp, _valid_catalog(), ["alpha", "beta"])
            external = tmp / "global" / "external" / "beta-copy"
            external.mkdir()
            (external / "SKILL.md").write_bytes(
                (skills / "beta" / "SKILL.md").read_bytes()
            )
            contract = _FakeContract(skills)
            with patch.object(check, "ROOT", tmp), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    check.check_skill_catalog(contract, {"alpha", "beta"})


    def test_workflow_without_sample_limits_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["alpha"]["evidence"]["limits"] = "  "
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_workflow_with_invalid_trials_per_cell_is_rejected(self) -> None:
        catalog = _valid_catalog()
        catalog["skills"]["alpha"]["evidence"]["trials_per_cell"] = 0
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_missing_classification_key_is_rejected(self) -> None:
        catalog = _valid_catalog()
        del catalog["skills"]["beta"]["classification"]
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta"])

    def test_catalog_missing_a_skill_dir_is_rejected(self) -> None:
        # The mirror of test_catalog_skill_drift_is_rejected: a skill dir on
        # disk that the catalog omits must also fail.
        catalog = _valid_catalog()
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            _run_gate(Path(tmp), catalog, ["alpha", "beta", "gamma"])

    def test_preset_naming_a_missing_skill_is_rejected(self) -> None:
        # Defends the check_presets missing-skill rule (bin/check:208-212).
        # Requires omp on PATH (CI installs it); the message assertion
        # guarantees we reached the existence check rather than failing
        # earlier at the omp subprocess. The callsite is defended separately
        # by test_bin_check_rejects_a_preset_naming_a_missing_skill.
        real_contract = check.load_contract(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            preset_dir = tmp / "presets"
            preset_dir.mkdir()
            (preset_dir / "bad.yml").write_text(
                "skills:\n  includeSkills:\n    - this-skill-does-not-exist\n"
            )
            surfaces = tuple(
                dataclasses.replace(surface, source=preset_dir)
                if surface.name == "presets"
                else surface
                for surface in real_contract.surfaces
            )
            contract = dataclasses.replace(real_contract, surfaces=surfaces)
            err = io.StringIO()
            with redirect_stderr(err), self.assertRaises(SystemExit):
                check.check_presets(contract)
        self.assertIn("names missing skill", err.getvalue())

    def test_bin_check_rejects_a_preset_naming_a_missing_skill(self) -> None:
        # End-to-end defense of the check_tree -> check_presets callsite: if
        # that callsite were removed, bin/check would skip preset validation
        # and this bad-preset projection would pass. Runs against a tmpdir
        # copy so no tracked preset is mutated.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            shutil.copytree(ROOT / "bin", repo / "bin")
            shutil.copytree(ROOT / "global", repo / "global")
            shutil.copy2(ROOT / "provenance.yaml", repo / "provenance.yaml")
            (repo / "global" / "presets" / "zzz-bad.yml").write_text(
                "skills:\n  includeSkills:\n    - this-skill-does-not-exist\n"
            )
            result = subprocess.run(
                [sys.executable, str(repo / "bin" / "check")],
                capture_output=True,
                cwd=repo,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"names missing skill", result.stderr)

if __name__ == "__main__":
    unittest.main()
