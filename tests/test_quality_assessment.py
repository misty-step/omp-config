from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "global/skills/quality/scripts/validate-assessment.py"


class QualityAssessmentTests(unittest.TestCase):
    def _assessment(self) -> dict[str, object]:
        return {
            "schema_version": "omp.quality-assessment.v2",
            "domain": "tests",
            "mode": "audit-only",
            "repository": "fixture",
            "revision": "fixture-v1",
            "dirty": False,
            "generated_at": "2026-08-01T00:00:00Z",
            "inventory": [
                {
                    "id": "unit",
                    "present": True,
                    "evidence": [{"path": "tests/", "observed": "Unit suite exists."}],
                    "missing_reason": None,
                }
            ],
            "targets": [
                {
                    "id": "unit-contract",
                    "claim": "Unit tests defend observable behavior.",
                    "failure_mode": "A contract regression passes.",
                    "falsifier": "Revert the behavior and observe a failing test.",
                    "selection": "selected",
                    "reason": None,
                }
            ],
            "findings": [
                {
                    "id": "tests-001",
                    "target": "unit-contract",
                    "severity": "medium",
                    "observed": "The contract lacked one boundary case.",
                    "evidence": [{"path": "tests/test_unit.py", "observed": "The boundary is now covered."}],
                    "decision": "remediate",
                    "waiver": None,
                    "ticket": None,
                    "rejection_reason": None,
                    "remediation": {
                        "change": "Added the boundary case.",
                        "verified_by": "independent verifier",
                        "evidence": "The repaired test passes and fails against the seeded regression.",
                        "blocker": None,
                    },
                    "status": "remediated",
                }
            ],
            "gates": [
                {
                    "id": "unit-suite",
                    "driver": "python3 -m unittest",
                    "report": "assessment.json",
                    "exit_code": 0,
                    "seed": "boundary-regression",
                    "falsifier_verified": True,
                }
            ],
            "strengths": ["The suite is deterministic."],
            "domain_data": {},
            "residual_risk": [],
        }

    def _validate(self, assessment: dict[str, object]) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="quality-assessment-") as directory:
            path = Path(directory) / "assessment.json"
            path.write_text(json.dumps(assessment))
            return subprocess.run(
                ["python3", str(VALIDATOR), str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

    def test_valid_assessment_passes(self) -> None:
        result = self._validate(self._assessment())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("quality assessment valid", result.stdout)

    def test_present_surface_requires_evidence(self) -> None:
        assessment = self._assessment()
        inventory = assessment["inventory"]
        self.assertIsInstance(inventory, list)
        surface = inventory[0]
        self.assertIsInstance(surface, dict)
        surface["evidence"] = []

        result = self._validate(assessment)

        self.assertEqual(result.returncode, 1)
        self.assertIn("minItems", result.stderr)

    def test_remediated_finding_rejects_a_blocker(self) -> None:
        assessment = self._assessment()
        findings = assessment["findings"]
        self.assertIsInstance(findings, list)
        finding = findings[0]
        self.assertIsInstance(finding, dict)
        remediation = finding["remediation"]
        self.assertIsInstance(remediation, dict)
        remediation["blocker"] = "Verification is incomplete."

        result = self._validate(assessment)

        self.assertEqual(result.returncode, 1)
        self.assertIn("/remediation/blocker", result.stderr)


if __name__ == "__main__":
    unittest.main()
