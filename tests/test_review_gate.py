from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import review_bundle
import review_common
import review_receipt

FIXTURE = ROOT / "tests" / "fixtures" / "review-gate"
GATE = ROOT / "bin" / "review_gate.py"
REVIEWERS = tuple(review_common.REVIEWERS)


class ReviewGateProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="review-gate-test-")
        self.repo = Path(self.temp.name) / "repo"
        shutil.copytree(FIXTURE, self.repo)
        self.run_command("git", "init", "--quiet")
        self.run_command("git", "config", "user.name", "Review Gate Test")
        self.run_command("git", "config", "user.email", "review-gate@example.test")
        self.run_command("git", "add", ".")
        self.run_command("git", "commit", "--quiet", "-m", "fixture")
        self.base_oid = self.git_oid("HEAD")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_command(self, *command: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(command),
            cwd=self.repo,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_gate(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return self.run_command(sys.executable, str(GATE), *arguments)

    def git_oid(self, revision: str) -> str:
        result = self.run_command("git", "rev-parse", revision)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, message: str, *paths: str) -> str:
        self.run_command("git", "add", *paths)
        result = self.run_command("git", "commit", "--quiet", "-m", message)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.git_oid("HEAD")

    def freeze_range(self) -> dict[str, object]:
        (self.repo / "app.py").write_text('def result():\n    return "reviewed"\n', encoding="utf-8")
        new_oid = self.commit("reviewed change", "app.py")
        frozen = self.run_gate(
            "freeze",
            "--repo",
            str(self.repo),
            "--old-oid",
            self.base_oid,
            "--new-oid",
            new_oid,
        )
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        return json.loads((self.repo / ".omp" / "review-freeze.json").read_text(encoding="utf-8"))

    def identity(self) -> dict[str, object]:
        return json.loads((self.repo / ".omp" / "review-freeze.json").read_text(encoding="utf-8"))

    def result_for(
        self,
        reviewer: str,
        *,
        status: str = "clean",
        findings: list[dict[str, object]] | None = None,
        skill_sha256: str | None = None,
        schema: str = review_common.RESULT_SCHEMA,
    ) -> dict[str, object]:
        identity = self.identity()
        finding_list = findings or []
        result: dict[str, object] = {
            "schema": schema,
            "reviewer": reviewer,
            "old_oid": identity["old_oid"],
            "new_oid": identity["new_oid"],
            "bundle_digest": identity["bundle_digest"],
            "skill_sha256": skill_sha256 or review_common.skill_identity(reviewer)["sha256"],
            "status": status,
            "actionable_findings": len(finding_list),
            "findings": finding_list,
        }
        if status in {"failed", "unavailable"}:
            result["error"] = "synthetic failure"
        return result

    def attribution(self, reviewer: str, *, harness: str | None = None, run_id: str | None = None) -> dict[str, str]:
        return {
            "actor": f"actor-{reviewer}",
            "harness": harness or f"harness-{reviewer}",
            "model": f"model-{reviewer}",
            "run_id": run_id or f"run-{reviewer}",
        }

    def adapter(self) -> dict[str, str]:
        executable = BIN / "review_gate.py"
        return {
            "name": "test-adapter",
            "executable": str(executable),
            "executable_sha256": review_common.sha256_bytes(executable.read_bytes()),
            "engine": "test-engine",
        }

    def submit(
        self,
        reviewer: str,
        *,
        result: dict[str, object] | None = None,
        attribution: dict[str, str] | None = None,
        adapter: dict[str, str] | None = None,
    ) -> Path:
        return review_receipt.submit_result(
            self.repo,
            self.repo / ".omp" / "review-freeze.json",
            reviewer,
            attribution or self.attribution(reviewer),
            result or self.result_for(reviewer),
            adapter=adapter,
        )

    def submit_all(self, *, duplicate_identity: bool = False, reviewers: list[str] | None = None) -> list[Path]:
        paths: list[Path] = []
        lanes = reviewers or self.identity().get("planned_lanes", list(REVIEWERS))
        for reviewer in lanes:
            attribution = self.attribution(
                reviewer,
                harness="same-harness" if duplicate_identity else None,
                run_id="same-run" if duplicate_identity else None,
            )
            paths.append(
                self.submit(
                    reviewer,
                    attribution=attribution,
                    adapter=self.adapter() if reviewer == "autoreview" else None,
                )
            )
        return paths

    def record(self) -> Path:
        return review_receipt.record_receipt(
            self.repo,
            self.repo / ".omp" / "review-freeze.json",
        )

    def verify(self) -> None:
        receipt, identity = review_receipt.load_receipt(
            self.repo,
            self.repo / ".omp" / "review-receipt.json",
        )
        review_receipt.verify_receipt(self.repo, receipt, identity, review_common.review_scope)

    def test_cli_freeze_record_verify_with_direct_submissions(self) -> None:
        identity = self.freeze_range()
        lanes = identity.get("planned_lanes", list(REVIEWERS))
        self.submit_all(reviewers=lanes)

        recorded = self.run_gate("record", "--repo", str(self.repo))
        self.assertEqual(recorded.returncode, 0, recorded.stderr)
        verified = self.run_gate(
            "verify",
            "--repo",
            str(self.repo),
            "--old-oid",
            str(identity["old_oid"]),
            "--new-oid",
            str(identity["new_oid"]),
        )
        self.assertEqual(verified.returncode, 0, verified.stderr)

        receipt = json.loads((self.repo / ".omp" / "review-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["schema"], review_common.RECEIPT_SCHEMA)
        self.assertEqual([item["reviewer"] for item in receipt["reviewers"]], list(lanes))
        self.assertIn("adapter", receipt["reviewers"][0])
        for item in receipt["reviewers"]:
            self.assertEqual(item["schema"], review_common.PASS_SCHEMA)
            self.assertEqual(set(item["worker"]), {"actor", "harness", "model", "run_id"})
    def test_forged_v2_result_is_rejected(self) -> None:
        self.freeze_range()
        result = self.result_for("thermo-nuclear-review", schema="omp.review-result.v2")
        with self.assertRaises(review_common.GateError):
            self.submit("thermo-nuclear-review", result=result)

    def test_malformed_finding_locations_are_rejected(self) -> None:
        self.freeze_range()
        malformed = (
            {"path": "/absolute.py"},
            {"path": "../outside.py"},
            {"path": "./app.py"},
            {"path": "app.py", "line_start": 3, "line_end": 2},
        )
        for location in malformed:
            finding = {
                "severity": "medium",
                "title": "bad location",
                "evidence": "synthetic malformed location",
                "locations": [location],
            }
            with self.subTest(location=location), self.assertRaises(review_common.GateError):
                self.submit(
                    "thermo-nuclear-review",
                    result=self.result_for("thermo-nuclear-review", status="findings", findings=[finding]),
                )

    def test_worker_attribution_is_explicit_and_actor_syntax_is_checked(self) -> None:
        self.freeze_range()
        with self.assertRaises(review_common.GateError):
            self.submit(
                "thermo-nuclear-review",
                attribution={"actor": "bad actor", "harness": "h", "model": "m", "run_id": "r"},
            )
        with self.assertRaises(review_common.GateError):
            self.submit(
                "thermo-nuclear-review",
                attribution={"actor": "actor", "harness": "h", "model": "m"},
            )
        path = self.submit("thermo-nuclear-review")
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(document["worker"], self.attribution("thermo-nuclear-review"))
        self.assertNotIn("executable", document["worker"])
        self.assertNotIn("provider", document["worker"])

    def test_identical_resubmission_is_idempotent_but_drift_rejected(self) -> None:
        self.freeze_range()
        result = self.result_for("thermo-nuclear-review")
        attribution = self.attribution("thermo-nuclear-review")
        with mock.patch.object(
            review_receipt,
            "now",
            side_effect=("2026-07-28T00:00:00Z", "2026-07-28T00:00:01Z"),
        ):
            path = self.submit("thermo-nuclear-review", result=result, attribution=attribution)
            original_bytes = path.read_bytes()
            original_submitted_at = json.loads(original_bytes)["submitted_at"]
            resubmitted = self.submit("thermo-nuclear-review", result=result, attribution=attribution)
        self.assertEqual(resubmitted, path)
        self.assertEqual(path.read_bytes(), original_bytes)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["submitted_at"], original_submitted_at)

        changed_result = dict(result)
        changed_result.update({"status": "failed", "error": "changed result"})
        with self.assertRaises(review_common.GateError):
            self.submit("thermo-nuclear-review", result=changed_result, attribution=attribution)
        changed_attribution = dict(attribution)
        changed_attribution["run_id"] = "different-run"
        with self.assertRaises(review_common.GateError):
            self.submit("thermo-nuclear-review", result=result, attribution=changed_attribution)

    def test_status_and_findings_must_agree(self) -> None:
        self.freeze_range()
        finding = {
            "severity": "low",
            "title": "finding",
            "evidence": "synthetic finding",
            "locations": [{"path": "app.py", "line_start": 1}],
        }
        with self.assertRaises(review_common.GateError):
            self.submit(
                "thermo-nuclear-review",
                result=self.result_for("thermo-nuclear-review", status="clean", findings=[finding]),
            )
        with self.assertRaises(review_common.GateError):
            self.submit(
                "thermo-nuclear-review",
                result=self.result_for("thermo-nuclear-review", status="findings"),
            )

    def test_forged_pass_schema_is_rejected_at_record(self) -> None:
        self.freeze_range()
        path = self.submit("thermo-nuclear-review")
        document = json.loads(path.read_text(encoding="utf-8"))
        document["schema"] = "omp.review-pass.v2"
        path.write_text(json.dumps(document), encoding="utf-8")
        self.submit_all_for_remaining("thermo-nuclear-review")
        with self.assertRaises(review_common.GateError):
            self.record()

    def submit_all_for_remaining(self, already_submitted: str) -> None:
        lanes = self.identity().get("planned_lanes", list(REVIEWERS))
        for reviewer in lanes:
            if reviewer == already_submitted:
                continue
            self.submit(reviewer, adapter=self.adapter() if reviewer == "autoreview" else None)

    def test_duplicate_harness_run_identity_is_rejected(self) -> None:
        self.freeze_range()
        self.submit_all(duplicate_identity=True)
        with self.assertRaises(review_common.GateError):
            self.record()

    def test_pass_status_drift_is_rejected_at_record(self) -> None:
        self.freeze_range()
        path = self.submit("thermo-nuclear-review")
        document = json.loads(path.read_text(encoding="utf-8"))
        document["status"] = "findings"
        path.write_text(json.dumps(document), encoding="utf-8")
        self.submit_all_for_remaining("thermo-nuclear-review")
        with self.assertRaises(review_common.GateError):
            self.record()

    def test_post_record_pass_drift_is_rejected_at_verify(self) -> None:
        self.freeze_range()
        self.submit_all()
        self.record()
        path = self.repo / ".omp" / "review-passes" / "autoreview.json"
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaises(review_common.GateError):
            self.verify()

    def test_post_record_skill_drift_is_rejected_at_verify(self) -> None:
        self.freeze_range()
        self.submit_all()
        self.record()
        receipt_path = self.repo / ".omp" / "review-receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["reviewers"][1]["skill"]["sha256"] = "sha256:" + "0" * 64
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaises(review_common.GateError):
            self.verify()

    def _push_input(self, old_oid: str, new_oid: str) -> str:
        return f"refs/heads/master {new_oid} refs/heads/master {old_oid}\n"

    def _hook_commit(self, message: str, content: str) -> str:
        path = self.repo / "hooks.txt"
        path.write_text(content, encoding="utf-8")
        return self.commit(message, "hooks.txt")

    def test_hook_advisory_allows_push_without_receipt(self) -> None:
        new_oid = self._hook_commit("advisory change", "advisory payload\n")
        result = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            "--repo",
            str(self.repo),
            input_text=self._push_input(self.base_oid, new_oid),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("advisory", result.stderr)

    def test_hook_enforce_blocks_push_without_receipt(self) -> None:
        new_oid = self._hook_commit("enforced change", "enforced payload\n")
        result = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            "--repo",
            str(self.repo),
            "--enforce",
            input_text=self._push_input(self.base_oid, new_oid),
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        # A prose-only change needs a waiver; a substantive change needs the
        # full sequence — both block in enforce mode without evidence.
        self.assertIn("review-gate:", result.stderr)
        self.assertTrue(
            "waiver" in result.stderr or "no clean receipt" in result.stderr,
            result.stderr,
        )

    def test_hook_advisory_clean_receipt_still_verifies(self) -> None:
        identity = self.freeze_range()
        self.submit_all(reviewers=identity.get("planned_lanes", list(REVIEWERS)))
        self.record()
        result = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            "--repo",
            str(self.repo),
            input_text=self._push_input(self.base_oid, str(identity["new_oid"])),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("clean", result.stdout)

    def test_hook_safety_failures_block_in_advisory_mode(self) -> None:
        result = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            "--repo",
            str(self.repo),
            input_text="refs/heads/master deadbeef refs/heads/master\n",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("malformed", result.stderr)


    def test_cli_submit_autoreview_requires_adapter_flags(self) -> None:
        identity = self.freeze_range()
        lanes = identity.get("planned_lanes", list(REVIEWERS))
        if "autoreview" not in lanes:
            self.skipTest("floor did not plan autoreview")
        result = self.result_for("autoreview")
        path = self.repo / "ar.json"
        path.write_text(json.dumps(result), encoding="utf-8")
        missing = self.run_gate(
            "submit",
            "--repo",
            str(self.repo),
            "--reviewer",
            "autoreview",
            "--actor",
            "tester",
            "--harness",
            "test",
            "--model",
            "test-model",
            "--run-id",
            "run-ar-missing",
            "--result",
            str(path),
        )
        self.assertNotEqual(missing.returncode, 0, missing.stdout + missing.stderr)
        self.assertIn("adapter", (missing.stderr + missing.stdout).lower())
        adapter = self.adapter()
        ok = self.run_gate(
            "submit",
            "--repo",
            str(self.repo),
            "--reviewer",
            "autoreview",
            "--actor",
            "tester",
            "--harness",
            "test",
            "--model",
            "test-model",
            "--run-id",
            "run-ar-ok",
            "--result",
            str(path),
            "--adapter-name",
            adapter["name"],
            "--adapter-executable",
            adapter["executable"],
            "--adapter-executable-sha256",
            adapter["executable_sha256"],
            "--adapter-engine",
            adapter["engine"],
        )
        self.assertEqual(ok.returncode, 0, ok.stderr)

if __name__ == "__main__":
    unittest.main()
