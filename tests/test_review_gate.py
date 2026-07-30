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
import review_packet
import review_receipt
import review_runner

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

    def freeze_and_prepare(self) -> dict[str, object]:
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
        prepared = self.run_gate("prepare", "--repo", str(self.repo))
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        return json.loads((self.repo / ".omp" / "review-freeze.json").read_text(encoding="utf-8"))

    def packet(self) -> dict[str, object]:
        return review_packet.load_packet(self.repo, self.identity())

    def identity(self) -> dict[str, object]:
        return json.loads((self.repo / ".omp" / "review-freeze.json").read_text(encoding="utf-8"))

    def result_for(
        self,
        reviewer: str,
        *,
        status: str = "clean",
        findings: list[dict[str, object]] | None = None,
        packet_digest: str | None = None,
        skill_sha256: str | None = None,
        schema: str = review_common.RESULT_SCHEMA,
    ) -> dict[str, object]:
        identity = self.identity()
        packet = self.packet()
        finding_list = findings or []
        result: dict[str, object] = {
            "schema": schema,
            "reviewer": reviewer,
            "old_oid": identity["old_oid"],
            "new_oid": identity["new_oid"],
            "bundle_digest": identity["bundle_digest"],
            "packet_digest": packet_digest or packet["packet_digest"],
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
        executable = BIN / "review_runner.py"
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

    def submit_all(self, *, duplicate_identity: bool = False) -> list[Path]:
        paths: list[Path] = []
        for reviewer in REVIEWERS:
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

    def test_cli_freeze_prepare_record_verify_with_direct_submissions(self) -> None:
        identity = self.freeze_and_prepare()
        self.submit_all()

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
        self.assertEqual([item["reviewer"] for item in receipt["reviewers"]], list(REVIEWERS))
        self.assertIn("adapter", receipt["reviewers"][0])
        self.assertNotIn("adapter", receipt["reviewers"][1])
        self.assertNotIn("adapter", receipt["reviewers"][2])
        for item in receipt["reviewers"]:
            self.assertEqual(item["schema"], review_common.PASS_SCHEMA)
            self.assertEqual(set(item["worker"]), {"actor", "harness", "model", "run_id"})

    def test_prepare_rejects_stale_frozen_range(self) -> None:
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        new_oid = self.commit("initial reviewed change", "app.py")
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
        (self.repo / "app.py").write_text("value = 2\n", encoding="utf-8")
        self.commit("unfrozen change", "app.py")
        with self.assertRaises(review_common.GateError):
            review_packet.prepare_packet(self.repo, self.repo / ".omp" / "review-freeze.json")
    def test_oversized_png_binary_patch_is_compacted_with_identity_metadata(self) -> None:
        encoded_body = b"z" * 170_000
        diff = (
            b"diff --git a/docs/pr-evidence/after.png b/docs/pr-evidence/after.png\n"
            b"new file mode 100644\n"
            b"index 0000000..c11fdde\n"
            b"GIT binary patch\n"
            b"literal 170000\n"
            + encoded_body
            + b"\n"
        )

        chunks = review_packet._dataset_chunks(diff)
        evidence = b"".join(chunks)

        self.assertGreater(len(diff), review_packet.DATASET_BYTES)
        self.assertTrue(chunks)
        self.assertTrue(all(len(chunk) <= review_packet.DATASET_BYTES for chunk in chunks))
        self.assertIn(b"docs/pr-evidence/after.png", evidence)
        self.assertIn(b"GIT binary patch", evidence)
        self.assertIn(b"Binary patch body omitted", evidence)
        self.assertIn(b"Binary literal sizes: 170000", evidence)
        self.assertNotIn(encoded_body, evidence)
        modified_body = b"y" * 180_000
        modified_diff = (
            b"diff --git a/docs/pr-evidence/updated.png b/docs/pr-evidence/updated.png\n"
            b"index 1111111..2222222 100644\n"
            b"GIT binary patch\n"
            b"delta 180000\n"
            + modified_body
            + b"\n"
        )
        modified_evidence = b"".join(review_packet._dataset_chunks(modified_diff))
        self.assertIn(b"docs/pr-evidence/updated.png", modified_evidence)
        self.assertIn(b"Binary delta payload sizes: 180000", modified_evidence)
        self.assertNotIn(modified_body, modified_evidence)

    def test_packet_chunks_reset_after_flushing_multiple_large_sections(self) -> None:
        payload = b"+" + (b"x" * 100_000) + b"\n"
        first = b"diff --git a/first.txt b/first.txt\n--- a/first.txt\n+++ b/first.txt\n@@ -0,0 +1 @@\n" + payload
        second = b"diff --git a/second.txt b/second.txt\n--- a/second.txt\n+++ b/second.txt\n@@ -0,0 +1 @@\n" + payload

        chunks = review_packet._dataset_chunks(first + second)

        self.assertEqual(len(chunks), 2)
        self.assertTrue(all(len(chunk) <= review_packet.DATASET_BYTES for chunk in chunks))
        self.assertIn(b"first.txt", chunks[0])
        self.assertNotIn(b"first.txt", chunks[1])
        self.assertIn(b"second.txt", chunks[1])

    def test_packet_dataset_mutation_is_rejected(self) -> None:
        self.freeze_and_prepare()
        dataset = self.repo / ".omp" / "review-packet" / "bundle.review.000.diff"
        dataset.chmod(0o644)
        dataset.write_bytes(dataset.read_bytes() + b"\nmutated\n")
        with self.assertRaises(review_common.GateError):
            review_packet.load_packet(self.repo, self.identity())

    def test_packet_extra_file_is_rejected(self) -> None:
        self.freeze_and_prepare()
        (self.repo / ".omp" / "review-packet" / "extra.txt").write_text("unexpected\n", encoding="utf-8")
        with self.assertRaises(review_common.GateError):
            review_packet.load_packet(self.repo, self.identity())

    def test_wrong_packet_digest_is_rejected_at_submission(self) -> None:
        self.freeze_and_prepare()
        result = self.result_for("thermo-nuclear-review", packet_digest="sha256:" + "0" * 64)
        with self.assertRaises(review_common.GateError):
            self.submit("thermo-nuclear-review", result=result)

    def test_wrong_skill_digest_is_rejected_at_submission(self) -> None:
        self.freeze_and_prepare()
        result = self.result_for("thermo-nuclear-review", skill_sha256="sha256:" + "0" * 64)
        with self.assertRaises(review_common.GateError):
            self.submit("thermo-nuclear-review", result=result)

    def test_forged_v2_result_is_rejected(self) -> None:
        self.freeze_and_prepare()
        result = self.result_for("thermo-nuclear-review", schema="omp.review-result.v2")
        with self.assertRaises(review_common.GateError):
            self.submit("thermo-nuclear-review", result=result)

    def test_malformed_finding_locations_are_rejected(self) -> None:
        self.freeze_and_prepare()
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
        self.freeze_and_prepare()
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
        self.freeze_and_prepare()
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
        self.freeze_and_prepare()
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
        self.freeze_and_prepare()
        path = self.submit("thermo-nuclear-review")
        document = json.loads(path.read_text(encoding="utf-8"))
        document["schema"] = "omp.review-pass.v2"
        path.write_text(json.dumps(document), encoding="utf-8")
        self.submit_all_for_remaining("thermo-nuclear-review")
        with self.assertRaises(review_common.GateError):
            self.record()

    def submit_all_for_remaining(self, already_submitted: str) -> None:
        for reviewer in REVIEWERS:
            if reviewer == already_submitted:
                continue
            self.submit(reviewer, adapter=self.adapter() if reviewer == "autoreview" else None)

    def test_duplicate_harness_run_identity_is_rejected(self) -> None:
        self.freeze_and_prepare()
        self.submit_all(duplicate_identity=True)
        with self.assertRaises(review_common.GateError):
            self.record()

    def test_pass_status_drift_is_rejected_at_record(self) -> None:
        self.freeze_and_prepare()
        path = self.submit("thermo-nuclear-review")
        document = json.loads(path.read_text(encoding="utf-8"))
        document["status"] = "findings"
        path.write_text(json.dumps(document), encoding="utf-8")
        self.submit_all_for_remaining("thermo-nuclear-review")
        with self.assertRaises(review_common.GateError):
            self.record()

    def test_post_record_pass_drift_is_rejected_at_verify(self) -> None:
        self.freeze_and_prepare()
        self.submit_all()
        self.record()
        path = self.repo / ".omp" / "review-passes" / "autoreview.json"
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaises(review_common.GateError):
            self.verify()

    def test_post_record_skill_drift_is_rejected_at_verify(self) -> None:
        self.freeze_and_prepare()
        self.submit_all()
        self.record()
        receipt_path = self.repo / ".omp" / "review-receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["reviewers"][1]["skill"]["sha256"] = "sha256:" + "0" * 64
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaises(review_common.GateError):
            self.verify()

    def test_post_record_packet_drift_is_rejected_at_verify(self) -> None:
        self.freeze_and_prepare()
        self.submit_all()
        self.record()
        dataset = self.repo / ".omp" / "review-packet" / "bundle.review.000.diff"
        dataset.chmod(0o644)
        dataset.write_bytes(dataset.read_bytes() + b"\npost-record mutation\n")
        with self.assertRaises(review_common.GateError):
            self.verify()

    def test_direct_leaf_submissions_need_no_coordinator(self) -> None:
        self.freeze_and_prepare()
        for reviewer in REVIEWERS[1:]:
            path = self.submit(reviewer)
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("adapter", document)
        self.submit("autoreview", adapter=self.adapter())
        self.assertEqual(self.record().name, "review-receipt.json")

    def test_run_one_invokes_explicit_leaf_and_preserves_non_clean_exit(self) -> None:
        self.freeze_and_prepare()
        helper = Path(self.temp.name) / "review-helper.py"
        helper.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "args = sys.argv[1:]\n"
            "output = args[args.index('--json-output') + 1]\n"
            "model = args[args.index('--model') + 1]\n"
            "findings = [] if model == 'test-clean' else ["
            "{'severity':'medium','title':'Synthetic finding','evidence':'Observable test evidence','locations':[]}]\n"
            "json.dump({'findings': findings, 'actionable_findings': len(findings)}, open(output, 'w'))\n"
            "raise SystemExit(1 if findings else 0)\n",
            encoding="utf-8",
        )
        helper.chmod(0o755)
        for reviewer, model, expected in (
            ("thermo-nuclear-review", "test-clean", 0),
            ("thermo-nuclear-code-quality-review", "test-findings", 1),
        ):
            result = self.run_command(
                sys.executable,
                str(BIN / "review_runner.py"),
                "run-one",
                "--repo",
                str(self.repo),
                "--reviewer",
                reviewer,
                "--actor",
                "test-actor",
                "--harness",
                "test-harness",
                "--engine",
                "test-engine",
                "--model",
                model,
                "--run-id",
                f"run-{reviewer}",
                "--executable",
                str(helper),
            )
            self.assertEqual(result.returncode, expected, result.stderr)
            passed = json.loads(
                (self.repo / ".omp" / "review-passes" / f"{reviewer}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(passed["worker"]["harness"], "test-harness")
            self.assertEqual(passed["status"], "clean" if expected == 0 else "findings")

    def test_run_one_autoreview_uses_current_harness_command_shape(self) -> None:
        self.freeze_and_prepare()
        helper = Path(self.temp.name) / "review-helper.py"
        helper.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "args = sys.argv[1:]\n"
            "if '--allow-empty' in args:\n"
            "    raise SystemExit(91)\n"
            "output = args[args.index('--json-output') + 1]\n"
            "datasets = [args[index + 1] for index, value in enumerate(args) if value == '--dataset']\n"
            "report = {'findings': [], 'actionable_findings': 0, 'overall_correctness': 'patch is correct'}\n"
            "if any('bundle.review.' in dataset for dataset in datasets):\n"
            "    report.update({'change_summary': 'Synthetic clean review', 'interface_effects': []})\n"
            "with open(output, 'w', encoding='utf-8') as handle:\n"
            "    json.dump(report, handle)\n",
            encoding="utf-8",
        )
        helper.chmod(0o755)

        result = self.run_command(
            sys.executable,
            str(BIN / "review_runner.py"),
            "run-one",
            "--repo",
            str(self.repo),
            "--reviewer",
            "autoreview",
            "--actor",
            "test-actor",
            "--harness",
            "test-harness",
            "--engine",
            "test-engine",
            "--model",
            "test-model",
            "--run-id",
            "run-autoreview",
            "--executable",
            str(helper),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        passed = json.loads((self.repo / ".omp" / "review-passes" / "autoreview.json").read_text(encoding="utf-8"))
        self.assertEqual(passed["status"], "clean")
        self.assertEqual(passed["worker"]["harness"], "test-harness")

    def test_codex_adapter_keeps_tools_for_isolated_review_workspace(self) -> None:
        command = review_runner._adapter_command(
            Path("/tmp/autoreview"),
            "codex",
            "gpt-test",
            "high",
            "Review the packet.",
            [".omp/review-packet/bundle.review.000.diff"],
            Path("/tmp/review-result.json"),
        )

        self.assertNotIn("--no-tools", command)

    def test_autoreview_worker_isolated_from_repo_and_tools(self) -> None:
        self.freeze_and_prepare()
        sentinel = self.repo / "review-author-sentinel.txt"
        sentinel.write_text("untouched\n", encoding="utf-8")
        helper = Path(self.temp.name) / "adversarial-review-helper.py"
        helper.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "if '--no-tools' not in args:\n"
            "    raise SystemExit(92)\n"
            "if '--allow-empty' in args:\n"
            "    raise SystemExit(91)\n"
            "Path('review-author-sentinel.txt').write_text('mutated\\n', encoding='utf-8')\n"
            "output = args[args.index('--json-output') + 1]\n"
            "json.dump({'findings': [], 'actionable_findings': 0, 'overall_correctness': 'patch is correct', "
            "'change_summary': 'Synthetic clean review', 'interface_effects': [], 'worker_cwd': os.getcwd()}, "
            "open(output, 'w', encoding='utf-8'))\n",
            encoding="utf-8",
        )
        helper.chmod(0o755)
        with tempfile.TemporaryDirectory(prefix="review-runner-report-") as report_dir:
            result = review_runner.run_autoreview_chunks(
                self.identity(),
                self.repo,
                self.packet(),
                30,
                Path(report_dir),
                helper,
                "test-engine",
                "test-model",
                None,
            )

        self.assertEqual(result["actionable_findings"], 0)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "untouched\n")
        worker_cwd = result["reports"][0]["report"]["worker_cwd"]
        self.assertNotEqual(worker_cwd, str(self.repo))
        self.assertFalse(Path(worker_cwd).exists())

    def test_failed_adapter_result_does_not_forge_missing_findings(self) -> None:
        self.freeze_and_prepare()
        _, identity = review_bundle.load_freeze(self.repo, self.repo / ".omp" / "review-freeze.json")
        result = review_runner._result_document(
            identity,
            self.packet(),
            "autoreview",
            {"findings": [], "actionable_findings": 1},
            exit_code=2,
            status="failed",
            error="worker failed before returning structured findings",
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["actionable_findings"], 0)
        self.assertEqual(result["findings"], [])
        self.assertIn("worker failed", result["error"])

    def test_autoreview_report_count_without_details_is_rejected(self) -> None:
        report = {"findings": [], "actionable_findings": 1}

        with self.assertRaisesRegex(review_common.GateError, "does not match normalized"):
            review_runner._validated_findings(report, "autoreview")


if __name__ == "__main__":
    unittest.main()
