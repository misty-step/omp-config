from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
CATALOG = ROOT / "global" / "skill-catalog.json"
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
    """Defend check_skill_catalog (bin/check:268-333): every rule has a test that
    fails if the rule is deleted, inverted, or unwired from check_tree."""

    def test_real_catalog_passes_the_real_gate(self) -> None:
        declared = {path.name for path in SKILLS.iterdir() if path.is_dir()}
        # check.ROOT already points at the real repo, so this drives the actual
        # catalog, the actual first-party skills, and the actual external tier.
        check.check_skill_catalog(_FakeContract(SKILLS), declared)

    def test_bin_check_passes_and_rejects_a_corrupt_catalog(self) -> None:
        # End-to-end defense of the callsite (bin/check check_tree -> 463).
        healthy = subprocess.run(
            [sys.executable, "bin/check"], capture_output=True, cwd=ROOT
        )
        self.assertEqual(healthy.returncode, 0, healthy.stderr.decode())
        self.assertIn(b"OMP source configuration OK", healthy.stdout)

        backup = CATALOG.read_bytes()
        try:
            CATALOG.write_text(
                json.dumps({"schema_version": "not.the.schema", "skills": {}})
            )
            corrupt = subprocess.run(
                [sys.executable, "bin/check"], capture_output=True, cwd=ROOT
            )
        finally:
            CATALOG.write_bytes(backup)
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


if __name__ == "__main__":
    unittest.main()
