from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from unittest.mock import patch
from pathlib import Path

if str(Path(__file__).resolve().parents[1] / "bin") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import review_gate
import review_runner

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "review-gate"
GATE = ROOT / "bin" / "review_gate.py"
ZERO_OID = "0" * 40
TEST_WORKER = {
    "principal": "test-worker",
    "harness": "test-harness",
    "model": "test-model",
    "executable": "test-worker",
    "executable_sha256": "sha256:" + "0" * 64,
    "payload": "test-payload",
    "payload_sha256": "sha256:" + "1" * 64,
}


class ReviewGateTests(unittest.TestCase):
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

    def git_oid(self, revision: str) -> str:
        result = self.run_command("git", "rev-parse", revision)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, message: str, *paths: str) -> str:
        self.run_command("git", "add", *paths)
        result = self.run_command("git", "commit", "--quiet", "-m", message)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.git_oid("HEAD")

    def freeze(self, old_oid: str, new_oid: str) -> subprocess.CompletedProcess[str]:
        return self.run_command(
            sys.executable,
            str(GATE),
            "freeze",
            "--old-oid",
            old_oid,
            "--new-oid",
            new_oid,
        )

    def identity(self) -> dict[str, object]:
        return json.loads((self.repo / ".omp" / "review-freeze.json").read_text())

    def worker_for(self, reviewer: str) -> dict[str, str]:
        executable, payload = review_gate.PINNED_WORKERS[reviewer]
        executable = executable.resolve(strict=True)
        payload = payload.resolve(strict=True)
        return {
            "principal": reviewer,
            "harness": "test-harness",
            "model": "test-model",
            "executable": str(executable),
            "executable_sha256": review_gate._sha256_bytes(executable.read_bytes()),
            "payload": str(payload),
            "payload_sha256": review_gate._directory_digest(payload),
        }
    def write_pass(self, identity: dict[str, object], reviewer: str, *, status: str = "clean", findings: int = 0) -> Path:
        path = self.repo / ".omp" / "review-passes" / f"{reviewer}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        raw_report: dict[str, object] = {"findings": []}
        if reviewer == "autoreview":
            raw_report["overall_correctness"] = "patch is correct"
            raw_report["overall_explanation"] = "synthetic internal receipt fixture"
            raw_report["overall_confidence"] = "high"
        worker = self.worker_for(reviewer)
        path.write_text(
            json.dumps(
                {
                    "schema": "omp.review-pass.v2",
                    "repository": identity["repository"],
                    "old_oid": identity["old_oid"],
                    "new_oid": identity["new_oid"],
                    "commits": identity["commits"],
                    "paths": identity["paths"],
                    "bundle_digest": identity["bundle_digest"],
                    "reviewer": reviewer,
                    "status": status,
                    "actionable_findings": findings,
                    "exit_code": 0 if status == "clean" else 1,
                    "worker": worker,
                    "raw_report": raw_report,
                }
            )
        )
        return path

    def record_clean(self, identity: dict[str, object] | None = None) -> subprocess.CompletedProcess[str]:
        identity = identity or self.identity()
        autoreview = self.write_pass(identity, "autoreview")
        correctness = self.write_pass(identity, "thermo-nuclear-review")
        quality = self.write_pass(identity, "thermo-nuclear-code-quality-review")
        try:
            code = review_gate.record(
                Namespace(
                    repo=str(self.repo),
                    freeze=str(self.repo / ".omp" / "review-freeze.json"),
                    output=None,
                    scope="substantive",
                    autoreview_json=autoreview,
                    autoreview_exit=0,
                    thermo_correctness_json=correctness,
                    thermo_quality_json=quality,
                )
            )
            return subprocess.CompletedProcess([], code, "", "")
        except (review_gate.GateError, OSError, ValueError) as error:
            return subprocess.CompletedProcess([], 1, "", str(error))


    def protected_update(self, old_oid: str, new_oid: str) -> str:
        return f"refs/heads/feature {new_oid} refs/heads/master {old_oid}\n"

    def test_exact_clean_range_success(self) -> None:
        (self.repo / "app.py").write_text('def result():\n    return "reviewed"\n')
        new_oid = self.commit("reviewed change", "app.py")
        frozen = self.freeze(self.base_oid, new_oid)
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        recorded = self.record_clean()
        self.assertEqual(recorded.returncode, 0, recorded.stderr)
        verified = self.run_command(sys.executable, str(GATE), "hook", input_text=self.protected_update(self.base_oid, new_oid))
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertIn("frozen Git range", verified.stdout)

    def test_verify_requires_gate_owned_pass_artifacts(self) -> None:
        (self.repo / "app.py").write_text("result = 1\n")
        new_oid = self.commit("reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        identity = self.identity()
        autoreview = self.write_pass(identity, "autoreview")
        outside = self.repo / "autoreview-copy.json"
        outside.write_bytes(autoreview.read_bytes())
        with self.assertRaisesRegex(review_gate.GateError, "gate-owned"):
            review_gate.record(
                Namespace(
                    repo=str(self.repo),
                    freeze=str(self.repo / ".omp" / "review-freeze.json"),
                    output=None,
                    scope="substantive",
                    autoreview_json=outside,
                    autoreview_exit=0,
                    thermo_correctness_json=self.write_pass(identity, "thermo-nuclear-review"),
                    thermo_quality_json=self.write_pass(identity, "thermo-nuclear-code-quality-review"),
                )
            )

    def test_verify_rejects_pass_artifact_drift(self) -> None:
        (self.repo / "app.py").write_text("result = 1\n")
        new_oid = self.commit("reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        self.assertEqual(self.record_clean().returncode, 0)
        pass_path = self.repo / ".omp" / "review-passes" / "autoreview.json"
        pass_path.write_text(pass_path.read_text() + "\n", encoding="utf-8")
        blocked = self.run_command(sys.executable, str(GATE), "verify", "--old-oid", self.base_oid, "--new-oid", new_oid)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("pass artifact changed", blocked.stderr)

    def rewrite_pass_worker_digest(self, reviewer: str, field: str) -> None:
        pass_path = self.repo / ".omp" / "review-passes" / f"{reviewer}.json"
        pass_document = json.loads(pass_path.read_text(encoding="utf-8"))
        pass_document["worker"][field] = "sha256:" + "0" * 64
        pass_path.write_text(json.dumps(pass_document), encoding="utf-8")
        receipt_path = self.repo / ".omp" / "review-receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        index = next(index for index, item in enumerate(receipt["reviewers"]) if item["reviewer"] == reviewer)
        receipt["reviewers"][index] = {
            **pass_document,
            "pass_artifact": {
                "path": f".omp/review-passes/{reviewer}.json",
                "sha256": review_gate._sha256_bytes(pass_path.read_bytes()),
            },
        }
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    def test_verify_rehashes_worker_executable_and_payload(self) -> None:
        (self.repo / "app.py").write_text("result = 1\n")
        new_oid = self.commit("reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        self.assertEqual(self.record_clean().returncode, 0)
        self.rewrite_pass_worker_digest("autoreview", "executable_sha256")
        blocked_executable = self.run_command(sys.executable, str(GATE), "verify", "--old-oid", self.base_oid, "--new-oid", new_oid)
        self.assertNotEqual(blocked_executable.returncode, 0)
        self.assertIn("executable_sha256", blocked_executable.stderr)
        self.assertEqual(self.record_clean().returncode, 0)
        self.rewrite_pass_worker_digest("thermo-nuclear-review", "payload_sha256")
        blocked_payload = self.run_command(sys.executable, str(GATE), "verify", "--old-oid", self.base_oid, "--new-oid", new_oid)
        self.assertNotEqual(blocked_payload.returncode, 0)
        self.assertIn("payload_sha256", blocked_payload.stderr)

    def test_external_repo_resolves_workers_at_gate_root(self) -> None:
        worker = self.worker_for("autoreview")
        document = {"worker": worker, "raw_report": {}}
        audited, _ = review_gate._audit_worker(
            document,
            "external review pass",
            self.repo / "external-repo",
            "autoreview",
        )
        self.assertEqual(audited["executable"], worker["executable"])
        self.assertEqual(audited["payload"], worker["payload"])

    def test_public_record_and_worker_overrides_are_rejected(self) -> None:
        record = self.run_command(sys.executable, str(GATE), "record")
        self.assertNotEqual(record.returncode, 0)
        self.assertIn("invalid choice", record.stderr)
        run = self.run_command(sys.executable, str(GATE), "run", "--autoreview-bin", "/tmp/fake")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("unrecognized arguments", run.stderr)

    def test_pathspec_magic_filename_cannot_hide_dirty_frozen_path(self) -> None:
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        (self.repo / ":(exclude)app.py").write_text("literal path\n", encoding="utf-8")
        self.assertEqual(self.run_command("git", "add", "-A").returncode, 0)
        committed = self.run_command("git", "commit", "--quiet", "-m", "literal pathspec")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        new_oid = self.git_oid("HEAD")
        (self.repo / "app.py").write_text("value = 2\n", encoding="utf-8")
        blocked = self.freeze(self.base_oid, new_oid)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("clean worktree", blocked.stderr)

    def test_autoreview_uses_only_immutable_packet_datasets(self) -> None:
        identity = {
            "repository": "test/repository",
            "old_oid": ZERO_OID,
            "new_oid": self.base_oid,
            "commits": [self.base_oid],
            "paths": ["README.md"],
            "bundle_digest": "sha256:" + "0" * 64,
        }
        packet = self.repo / review_runner.PACKET_DIR
        packet.mkdir()
        for name in ("freeze.json", "evidence.json", "bundle.review.000.diff"):
            (packet / name).write_text("{}\n", encoding="utf-8")
        report = (
            '{"findings":[],"actionable_findings":0,"overall_correctness":"patch is correct",'
            '"change_summary":"no change","interface_effects":[]}'
        )
        with patch.object(
            review_runner,
            "_run_process",
            side_effect=[(0, report, ""), (0, '{"findings":[],"actionable_findings":0,"overall_correctness":"patch is correct"}', "")],
        ) as run_process:
            result = review_runner._autoreview_pass(identity, self.repo, 30, self.repo, TEST_WORKER)
        chunk_command = run_process.call_args_list[0].args[0]
        integration_command = run_process.call_args_list[1].args[0]
        self.assertEqual(result["status"], "clean")
        self.assertEqual(run_process.call_count, 2)
        self.assertEqual(chunk_command[chunk_command.index("--mode") + 1], "local")
        self.assertNotIn("--base", chunk_command)
        self.assertNotIn("--commit", chunk_command)
        self.assertIn(f"{review_runner.PACKET_DIR}/bundle.review.000.diff", chunk_command)
        self.assertNotIn(f"{review_runner.PACKET_DIR}/bundle.diff", chunk_command)
        self.assertIn(f"{review_runner.PACKET_DIR}/autoreview.integration.json", integration_command)

    def test_autoreview_runs_each_bounded_dataset_and_aggregates_findings(self) -> None:
        identity = {
            "repository": "test/repository",
            "old_oid": ZERO_OID,
            "new_oid": self.base_oid,
            "commits": [self.base_oid],
            "paths": ["README.md"],
            "bundle_digest": "sha256:" + "0" * 64,
        }
        packet = self.repo / review_runner.PACKET_DIR
        packet.mkdir()
        for name in ("freeze.json", "evidence.json", "bundle.review.000.diff", "bundle.review.001.diff"):
            (packet / name).write_text("{}\n", encoding="utf-8")
        clean = (
            '{"findings":[],"actionable_findings":0,"overall_correctness":"patch is correct",'
            '"change_summary":"no change","interface_effects":[]}'
        )
        finding = (
            '{"findings":[{"title":"bug"}],"actionable_findings":1,'
            '"overall_correctness":"patch is incorrect","change_summary":"changed API",'
            '"interface_effects":["caller contract"]}'
        )
        integration = '{"findings":[],"actionable_findings":0,"overall_correctness":"patch is correct"}'
        with patch.object(
            review_runner,
            "_run_process",
            side_effect=[(0, clean, ""), (1, finding, ""), (0, integration, "")],
        ) as run_process:
            result = review_runner._autoreview_pass(identity, self.repo, 30, self.repo, TEST_WORKER)
        self.assertEqual(run_process.call_count, 3)
        self.assertEqual(result["status"], "findings")
        self.assertEqual(result["actionable_findings"], 1)
        self.assertEqual(result["raw_report"]["findings"][0]["dataset"], "bundle.review.001.diff")
        self.assertEqual(result["raw_report"]["integration"]["report"]["findings"], [])

    def test_autoreview_datasets_compact_deletions_and_bound_large_files(self) -> None:
        deleted = (
            b"diff --git a/removed.txt b/removed.txt\n"
            b"deleted file mode 100644\n"
            b"index 1111111..0000000\n"
            b"--- a/removed.txt\n"
            b"+++ /dev/null\n"
            b"@@ -1,2 +0,0 @@\n"
            b"-secret body one\n"
            b"-secret body two\n"
        )
        large_header = (
            b"diff --git a/large.txt b/large.txt\n"
            b"new file mode 100644\n"
            b"index 0000000..2222222\n"
            b"--- /dev/null\n"
            b"+++ b/large.txt\n"
            b"@@ -0,0 +1,4000 @@\n"
        )
        chunks = review_runner._dataset_chunks(deleted + large_header + (b"+bounded review line\n" * 10_000))
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= review_runner.AUTOREVIEW_DATASET_BYTES for chunk in chunks))
        combined = b"".join(chunks)
        self.assertNotIn(b"secret body", combined)
        self.assertIn(b"Entire file deleted; 2 removed lines omitted", combined)
        self.assertTrue(all(chunk.startswith(b"diff --git ") for chunk in chunks))

    def test_autoreview_datasets_redact_values_without_hiding_safe_code(self) -> None:
        diff = (
            b"diff --git a/activity.ts b/activity.ts\n"
            b"index 1111111..2222222 100644\n"
            b"--- a/activity.ts\n"
            b"+++ b/activity.ts\n"
            b"@@ -1 +1,2 @@\n"
            b'-const value = "before";\n'
            b'+const safe = summarizeToolActivity("fetch", "https://example.com/path");\n'
            b'+const privateValue = "https://user:pass@example.com/path?token=secret";\n'
        )
        combined = b"".join(review_runner._dataset_chunks(diff))
        self.assertIn(b"summarizeToolActivity", combined)
        self.assertIn(b"https://user:redacted@example.com/path?token=secret", combined)
        self.assertNotIn(b"user:pass", combined)
        scanner = review_runner._autoreview_security()
        self.assertFalse(scanner.secret_text_risk(combined.decode("utf-8"), javascript_dialect="typescript"))

    def test_autoreview_datasets_remove_secret_values_before_annotation(self) -> None:
        secret = b"ghp_" + (b"A" * 40)
        diff = (
            b"diff --git a/example.env b/example.env\n"
            b"new file mode 100644\n"
            b"--- /dev/null\n"
            b"+++ b/example.env\n"
            b"@@ -0,0 +1 @@\n"
            b"+GITHUB_TOKEN="
            + secret
            + b"\n"
        )
        combined = b"".join(review_runner._dataset_chunks(diff))
        self.assertNotIn(secret, combined)
        self.assertIn(b"GITHUB_TOKEN=redacted", combined)

    def test_thermo_worker_runs_headless_and_read_only(self) -> None:
        identity = {
            "repository": "test/repository",
            "old_oid": self.base_oid,
            "new_oid": self.base_oid,
            "commits": [],
            "paths": [],
            "bundle_digest": "sha256:" + "0" * 64,
        }
        packet = self.repo / review_runner.PACKET_DIR
        packet.mkdir()
        for name in ("freeze.json", "evidence.json", "bundle.review.000.diff"):
            (packet / name).write_text("{}\n", encoding="utf-8")
        def run_thermo(command: list[str], cwd: Path, timeout: int) -> tuple[int, str, str]:
            staged = cwd / review_runner.PACKET_DIR
            self.assertNotEqual(cwd, self.repo)
            self.assertTrue((staged / "review-skill.md").is_file())
            self.assertEqual(staged.stat().st_mode & 0o777, 0o555)
            self.assertEqual((staged / "review-skill.md").stat().st_mode & 0o777, 0o444)
            self.assertFalse((cwd / "app.py").exists())
            return 0, '{"findings":[]}', ""

        with patch.object(
            review_runner,
            "_run_process",
            side_effect=run_thermo,
        ) as run_process:
            result = review_runner._thermo_pass(
                identity,
                "thermo-nuclear-review",
                Path("/usr/bin/true"),
                self.repo,
                30,
                TEST_WORKER,
            )
        command = run_process.call_args.args[0]
        self.assertEqual(result["status"], "clean")
        self.assertIn("--trust", command)
        self.assertEqual(command[command.index("--mode") + 1], "ask")

    def test_thermo_parse_failure_preserves_bounded_worker_output(self) -> None:
        identity = {
            "repository": "test/repository",
            "old_oid": self.base_oid,
            "new_oid": self.base_oid,
            "commits": [],
            "paths": [],
            "bundle_digest": "sha256:" + "0" * 64,
        }
        packet = self.repo / review_runner.PACKET_DIR
        packet.mkdir()
        for name in ("freeze.json", "evidence.json", "bundle.review.000.diff"):
            (packet / name).write_text("{}\n", encoding="utf-8")
        with patch.object(review_runner, "_run_process", return_value=(0, "not-json", "worker warning")):
            result = review_runner._thermo_pass(
                identity,
                "thermo-nuclear-review",
                Path("/usr/bin/true"),
                self.repo,
                30,
                TEST_WORKER,
            )
        self.assertEqual(result["status"], "findings")
        self.assertEqual(result["raw_report"]["stdout"], "not-json")
        self.assertEqual(result["raw_report"]["stderr"], "worker warning")

    def test_missing_old_object_fails_closed(self) -> None:
        (self.repo / "app.py").write_text('def result():\n    return "changed"\n')
        new_oid = self.commit("change", "app.py")
        missing_old = "1" * 40
        blocked = self.run_command(sys.executable, str(GATE), "hook", input_text=self.protected_update(missing_old, new_oid))
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("git", blocked.stderr)


    def test_hook_trivial_range_fails_before_expensive_review_with_waiver_command(self) -> None:
        (self.repo / "README.md").write_text("# revised documentation\n", encoding="utf-8")
        new_oid = self.commit("docs", "README.md")
        blocked = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            input_text=self.protected_update(self.base_oid, new_oid),
        )
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("trivial review range", blocked.stderr)
        self.assertIn("waive", blocked.stderr)
        self.assertIn("--actor review-gate@example.test", blocked.stderr)
        self.assertIn("--reason", blocked.stderr)

    def test_pushed_tree_differs_from_reviewed_range(self) -> None:
        (self.repo / "app.py").write_text('def result():\n    return "reviewed"\n')
        reviewed_oid = self.commit("reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, reviewed_oid).returncode, 0)
        self.assertEqual(self.record_clean().returncode, 0)

        blob = self.run_command("git", "hash-object", "-w", "--stdin", input_text='def result():\n    return "backdoor"\n').stdout.strip()
        self.assertEqual(len(blob), 40)
        tree_lines = self.run_command("git", "ls-tree", self.base_oid).stdout.splitlines()
        tree_lines = [f"100644 blob {blob}\tapp.py" if line.endswith("\tapp.py") else line for line in tree_lines]
        tree = self.run_command("git", "mktree", input_text="\n".join(tree_lines) + "\n").stdout.strip()
        pushed_oid = self.run_command(
            "git",
            "commit-tree",
            tree,
            "-p",
            self.base_oid,
            "-m",
            "unreviewed tree",
        ).stdout.strip()
        self.assertEqual(len(pushed_oid), 40)
        blocked = self.run_command(sys.executable, str(GATE), "hook", input_text=self.protected_update(self.base_oid, pushed_oid))
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("clean worktree", blocked.stderr)

    def test_edit_after_review_before_record_fails_closed(self) -> None:
        (self.repo / "app.py").write_text('def result():\n    return "reviewed"\n')
        new_oid = self.commit("reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        identity = self.identity()
        self.write_pass(identity, "thermo-nuclear-review")
        self.write_pass(identity, "thermo-nuclear-code-quality-review")
        (self.repo / "app.py").write_text('def result():\n    return "edited after review"\n')
        recorded = self.record_clean(identity)
        self.assertNotEqual(recorded.returncode, 0)
        self.assertIn("clean worktree", recorded.stderr)

    # "testing_" stays discoverable without matching TruffleHog's Lob test-key detector.
    def testing_bundle_digest_tampering_is_rejected(self) -> None:
        (self.repo / "README.md").write_text("# Revised documentation\n", encoding="utf-8")
        new_oid = self.commit("documentation", "README.md")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        freeze_path = self.repo / ".omp" / "review-freeze.json"
        document = json.loads(freeze_path.read_text(encoding="utf-8"))
        document["bundle_digest"] = "sha256:" + "0" * 64
        freeze_path.write_text(json.dumps(document), encoding="utf-8")

        blocked = self.record_clean()
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("bundle_digest", blocked.stderr)

    def test_frozen_identity_rejects_mismatched_reviewer_envelope(self) -> None:
        (self.repo / "app.py").write_text('def result():\n    return "first"\n', encoding="utf-8")
        first = self.commit("first reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, first).returncode, 0)
        first_identity = self.identity()

        (self.repo / "settings.yaml").write_text("mode: second\n", encoding="utf-8")
        second = self.commit("second unreviewed change", "settings.yaml")
        second_freeze = self.repo / ".omp" / "second-freeze.json"
        frozen = self.run_command(
            sys.executable,
            str(GATE),
            "freeze",
            "--output",
            str(second_freeze),
            "--old-oid",
            first,
            "--new-oid",
            second,
        )
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        second_identity = json.loads(second_freeze.read_text(encoding="utf-8"))

        autoreview = self.write_pass(first_identity, "autoreview")
        correctness = self.write_pass(second_identity, "thermo-nuclear-review")
        quality = self.write_pass(first_identity, "thermo-nuclear-code-quality-review")
        with self.assertRaises(review_gate.GateError) as error:
            review_gate.record(
                Namespace(
                    repo=str(self.repo),
                    freeze=str(self.repo / ".omp" / "review-freeze.json"),
                    output=None,
                    scope="substantive",
                    autoreview_json=autoreview,
                    autoreview_exit=0,
                    thermo_correctness_json=correctness,
                    thermo_quality_json=quality,
                )
            )
        self.assertIn("review pass", str(error.exception))
        self.assertIn("match", str(error.exception))

    def test_receipt_for_one_git_range_cannot_authorize_another(self) -> None:
        (self.repo / "app.py").write_text('def result():\n    return "first"\n', encoding="utf-8")
        first = self.commit("first reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, first).returncode, 0)
        self.assertEqual(self.record_clean().returncode, 0)

        (self.repo / "settings.yaml").write_text("mode: second\n", encoding="utf-8")
        second = self.commit("second change", "settings.yaml")
        blocked = self.run_command(
            sys.executable,
            str(GATE),
            "verify",
            "--old-oid",
            first,
            "--new-oid",
            second,
        )
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("review receipt", blocked.stderr)
        self.assertIn("committed-range bundle", blocked.stderr)

    def test_add_then_delete_secret_remains_in_bundle(self) -> None:
        (self.repo / "secret.env").write_text("TOKEN=never-release\n")
        added_oid = self.commit("add secret", "secret.env")
        (self.repo / "secret.env").unlink()
        deleted_oid = self.commit("remove secret", "secret.env")
        frozen = self.freeze(self.base_oid, deleted_oid)
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        identity = self.identity()
        self.assertIn("secret.env", identity["paths"])
        self.assertIn(added_oid, identity["commits"])
        self.assertIn(deleted_oid, identity["commits"])
        self.assertEqual(self.record_clean(identity).returncode, 0)
        verified = self.run_command(sys.executable, str(GATE), "hook", input_text=self.protected_update(self.base_oid, deleted_oid))
        self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_new_protected_ref_traverses_complete_history(self) -> None:
        (self.repo / "app.py").write_text('def result():\n    return "first"\n')
        first = self.commit("first introduced commit", "app.py")
        (self.repo / "README.md").write_text("# second\n")
        tip = self.commit("second introduced commit", "README.md")
        frozen = self.freeze(ZERO_OID, tip)
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        identity = self.identity()
        self.assertIn(first, identity["commits"])
        self.assertIn("app.py", identity["paths"])
        self.assertNotIn(first, identity["paths"])
        self.assertEqual(self.record_clean(identity).returncode, 0)
        verified = self.run_command(sys.executable, str(GATE), "hook", input_text=self.protected_update(ZERO_OID, tip))
        self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_policy_roots_cannot_use_trivial_waiver(self) -> None:
        previous = self.base_oid
        policy_paths = (
            ("global/skills/local/guide.md", "# Skill policy\n"),
            ("global/references/quality.md", "# Reference policy\n"),
            ("global/agents/reviewer.md", "# Agent policy\n"),
            ("AGENTS.md", "# Root agent policy\n"),
            ("RULES.md", "# Root rules\n"),
            ("docs/agents.md", "# Case-folded agent policy\n"),
            ("docs/skill.md", "# Case-folded skill policy\n"),
        )
        for relative, content in policy_paths:
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            new_oid = self.commit(f"policy change: {relative}", relative)
            frozen = self.freeze(previous, new_oid)
            self.assertEqual(frozen.returncode, 0, frozen.stderr)
            waived = self.run_command(
                sys.executable,
                str(GATE),
                "waive",
                "--actor",
                "review-gate@example.test",
                "--reason",
                "Documentation-only prose change; no executable behavior changed.",
            )
            self.assertNotEqual(waived.returncode, 0)
            self.assertIn("inert prose", waived.stderr)
            previous = new_oid

    def test_trivial_waiver_requires_explicit_receipt(self) -> None:
        (self.repo / "README.md").write_text("# Revised documentation\n", encoding="utf-8")
        new_oid = self.commit("documentation", "README.md")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        waived = self.run_command(
            sys.executable,
            str(GATE),
            "waive",
            "--actor",
            "review-gate@example.test",
            "--reason",
            "Documentation-only prose change; no executable behavior changed.",
        )
        self.assertEqual(waived.returncode, 0, waived.stderr)
        verified = self.run_command(sys.executable, str(GATE), "verify")
        self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_committed_range_verification_ignores_uncommitted_worktree_edits(self) -> None:
        (self.repo / "README.md").write_text("# Revised documentation\n", encoding="utf-8")
        new_oid = self.commit("documentation", "README.md")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        waived = self.run_command(
            sys.executable,
            str(GATE),
            "waive",
            "--actor",
            "review-gate@example.test",
            "--reason",
            "Documentation-only prose change; no executable behavior changed.",
        )
        self.assertEqual(waived.returncode, 0, waived.stderr)
        (self.repo / "README.md").write_text("# Changed after commit\n", encoding="utf-8")
        verified = self.run_command(sys.executable, str(GATE), "verify")
        self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_standalone_verify_rejects_stale_head(self) -> None:
        (self.repo / "README.md").write_text("# Reviewed\n", encoding="utf-8")
        reviewed = self.commit("reviewed documentation", "README.md")
        self.assertEqual(self.freeze(self.base_oid, reviewed).returncode, 0)
        waived = self.run_command(
            sys.executable,
            str(GATE),
            "waive",
            "--actor",
            "review-gate@example.test",
            "--reason",
            "Documentation-only prose change; no executable behavior changed.",
        )
        self.assertEqual(waived.returncode, 0, waived.stderr)
        (self.repo / "settings.yaml").write_text("mode: stale\n", encoding="utf-8")
        self.commit("unreviewed follow-up", "settings.yaml")
        stale = self.run_command(sys.executable, str(GATE), "verify")
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("stale", stale.stderr)

    def test_gitattributes_is_substantive_for_waiver_classification(self) -> None:
        (self.repo / ".gitattributes").write_text("*.py -diff\n", encoding="utf-8")
        new_oid = self.commit("change diff policy", ".gitattributes")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        waived = self.run_command(
            sys.executable,
            str(GATE),
            "waive",
            "--actor",
            "review-gate@example.test",
            "--reason",
            "Configuration-only change with no executable behavior changed.",
        )
        self.assertNotEqual(waived.returncode, 0)
        self.assertIn("inert prose", waived.stderr)

    def test_identical_protected_ranges_are_deduplicated(self) -> None:
        (self.repo / "app.py").write_text("result = 1\n", encoding="utf-8")
        new_oid = self.commit("reviewed change", "app.py")
        self.assertEqual(self.freeze(self.base_oid, new_oid).returncode, 0)
        self.assertEqual(self.record_clean().returncode, 0)
        updates = (
            f"refs/heads/feature {new_oid} refs/heads/master {self.base_oid}\n"
            f"refs/heads/feature {new_oid} refs/heads/main {self.base_oid}\n"
        )
        verified = self.run_command(sys.executable, str(GATE), "hook", input_text=updates)
        self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_first_feature_push_runs_from_local_default_without_remote_head(self) -> None:
        self.run_command("git", "branch", "main", self.base_oid)
        (self.repo / "app.py").write_text("result = 1\n", encoding="utf-8")
        new_oid = self.commit("feature change", "app.py")
        called: list[tuple[str, str]] = []

        def ensure(_args: Namespace, _repo: Path, old_oid: str, tip: str) -> None:
            called.append((old_oid, tip))

        with patch.object(review_gate, "_ensure_review", side_effect=ensure), patch.object(
            review_gate, "verify", return_value=0
        ), patch("sys.stdin", io.StringIO(f"refs/heads/feature {new_oid} refs/heads/feature {ZERO_OID}\n")):
            result = review_gate.hook(
                Namespace(repo=str(self.repo), receipt=None, old_oid=None, new_oid=None, remote="origin")
            )
        self.assertEqual(result, 0)
        self.assertEqual(called, [(self.base_oid, new_oid)])

    def test_malformed_input_feature_skip_and_protected_delete(self) -> None:
        tag = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            input_text="refs/heads/feature not-an-oid refs/tags/v1 not-an-oid\n",
        )
        self.assertEqual(tag.returncode, 0, tag.stderr)
        feature_delete = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            input_text=f"refs/heads/feature {ZERO_OID} refs/heads/feature {self.base_oid}\n",
        )
        self.assertEqual(feature_delete.returncode, 0, feature_delete.stderr)
        malformed = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            input_text="refs/heads/feature 1111111111111111111111111111111111111111 refs/heads/master\n",
        )
        self.assertNotEqual(malformed.returncode, 0)
        protected_delete = self.run_command(
            sys.executable,
            str(GATE),
            "hook",
            input_text=f"refs/heads/feature {ZERO_OID} refs/heads/master {self.base_oid}\n",
        )
        self.assertNotEqual(protected_delete.returncode, 0)
        self.assertIn("delete", protected_delete.stderr)


if __name__ == "__main__":
    unittest.main()
