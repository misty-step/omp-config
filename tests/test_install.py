from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))


def _load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    if spec is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


INSTALL = _load_module("omp_install_for_tests", BIN_DIR / "install")
CHECK = _load_module("omp_check_for_tests", BIN_DIR / "check")


class InstallHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="omp-install-test-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self._run_git("init", "--quiet")
        self._run_git("config", "user.name", "Install Test")
        self._run_git("config", "user.email", "install@example.test")
        self._run_git("config", "core.hooksPath", str(self.root / "default-hooks"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def _active_hooks(self) -> Path:
        raw = self._run_git("rev-parse", "--git-path", "hooks").stdout.strip()
        path = Path(raw)
        if not path.is_absolute():
            path = self.repo / path
        return path.resolve()

    def _run_install(self, agent_dir: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PI_CODING_AGENT_DIR"] = str(agent_dir)
        return subprocess.run(
            [sys.executable, str(BIN_DIR / "install"), "--project", str(self.repo)],
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def _fake_gate(self, agent_dir: Path, log: Path) -> None:
        hooks = agent_dir / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "review-gate.py").write_text(
            "import os\n"
            "import sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['OMP_TEST_LOG']).open('a', encoding='utf-8').write('gate\\n')\n"
            "sys.stdin.read()\n"
            "raise SystemExit(int(os.environ.get('OMP_TEST_GATE_EXIT', '0')))\n",
            encoding="utf-8",
        )

    def _foreign_hook(self, hooks: Path) -> Path:
        hooks.mkdir(parents=True, exist_ok=True)
        foreign = hooks / "pre-push"
        foreign.write_text(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "import sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['OMP_TEST_LOG']).open('a', encoding='utf-8').write('foreign\\n')\n"
            "sys.stdin.read()\n"
            "raise SystemExit(int(os.environ.get('OMP_TEST_FOREIGN_EXIT', '0')))\n",
            encoding="utf-8",
        )
        foreign.chmod(0o755)
        return foreign

    def test_absolute_core_hooks_path_installs_at_git_active_path(self) -> None:
        active = self.root / "absolute-hooks"
        self._run_git("config", "core.hooksPath", str(active))
        result = self._run_install(self.root / "agent")
        self.assertEqual(result.returncode, 0, result.stderr)
        hook = active / "pre-push"
        self.assertTrue(hook.is_file())
        self.assertFalse((self.repo / ".git" / "hooks" / "pre-push").exists())
        self.assertIn(INSTALL.MANAGED_MARKER.encode(), hook.read_bytes())

    def test_relative_core_hooks_path_installs_at_git_active_path(self) -> None:
        self._run_git("config", "core.hooksPath", "relative-hooks")
        result = self._run_install(self.root / "agent")
        self.assertEqual(result.returncode, 0, result.stderr)
        hook = self.repo / "relative-hooks" / "pre-push"
        self.assertTrue(hook.is_file())
        self.assertIn(INSTALL.MANAGED_MARKER.encode(), hook.read_bytes())

    def test_managed_hook_ignores_runtime_projection_override(self) -> None:
        agent = self.root / "agent"
        canonical_log = self.root / "canonical.log"
        self._fake_gate(agent, canonical_log)
        INSTALL.install_review_hook(self.repo, agent)
        hook = self._active_hooks() / "pre-push"

        malicious = self.root / "malicious-agent" / "hooks"
        malicious.mkdir(parents=True)
        malicious_log = self.root / "malicious.log"
        (malicious / "review-gate.py").write_text(
            "from pathlib import Path\n"
            f"Path({str(malicious_log)!r}).write_text('malicious\\n', encoding='utf-8')\n"
            "raise SystemExit(37)\n",
            encoding="utf-8",
        )

        environment = os.environ.copy()
        environment["OMP_TEST_LOG"] = str(canonical_log)
        environment["PI_CODING_AGENT_DIR"] = str(malicious.parent)
        result = subprocess.run(
            [str(hook)],
            cwd=self.repo,
            input="refs/heads/feature 1 refs/heads/feature 0\n",
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(canonical_log.read_text(encoding="utf-8").splitlines(), ["gate"])
        self.assertFalse(malicious_log.exists())
        hook_bytes = hook.read_bytes()
        self.assertIn(str((agent / "hooks" / "review-gate.py").resolve()).encode(), hook_bytes)
        self.assertNotIn(b"PI_CODING_AGENT_DIR", hook_bytes)

    def test_foreign_hook_runs_before_gate_and_failure_stops_gate(self) -> None:
        agent = self.root / "agent"
        log = self.root / "order.log"
        self._fake_gate(agent, log)
        hooks = self._active_hooks()
        foreign = self._foreign_hook(hooks)
        foreign_bytes = foreign.read_bytes()
        INSTALL.install_review_hook(self.repo, agent)
        backup = hooks / INSTALL.FOREIGN_HOOK_NAME
        self.assertEqual(backup.read_bytes(), foreign_bytes)
        environment = os.environ.copy()
        environment["OMP_TEST_LOG"] = str(log)
        environment["PI_CODING_AGENT_DIR"] = str(agent)
        allowed = subprocess.run(
            [str(hooks / "pre-push"), "origin", "url"],
            cwd=self.repo,
            input="refs/heads/feature 1 refs/heads/feature 0\n",
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["foreign", "gate"])

        log.write_text("", encoding="utf-8")
        environment["OMP_TEST_GATE_EXIT"] = "29"
        gate_failed = subprocess.run(
            [str(hooks / "pre-push")],
            cwd=self.repo,
            input="refs/heads/feature 1 refs/heads/feature 0\n",
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(gate_failed.returncode, 29, gate_failed.stderr)
        self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["foreign", "gate"])

        log.write_text("", encoding="utf-8")
        environment["OMP_TEST_GATE_EXIT"] = "0"
        environment["OMP_TEST_FOREIGN_EXIT"] = "23"
        blocked = subprocess.run(
            [str(hooks / "pre-push")],
            cwd=self.repo,
            input="refs/heads/feature 1 refs/heads/feature 0\n",
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(blocked.returncode, 23, blocked.stderr)
        self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["foreign"])

    def test_non_executable_foreign_hook_is_preserved_warned_and_skipped(self) -> None:
        agent = self.root / "agent"
        log = self.root / "nonexec.log"
        self._fake_gate(agent, log)
        hooks = self._active_hooks()
        foreign = self._foreign_hook(hooks)
        foreign.chmod(0o644)
        INSTALL.install_review_hook(self.repo, agent)
        backup = hooks / INSTALL.FOREIGN_HOOK_NAME
        self.assertEqual(backup.stat().st_mode & 0o777, 0o644)
        environment = os.environ.copy()
        environment["OMP_TEST_LOG"] = str(log)
        result = subprocess.run(
            [str(hooks / "pre-push"), "origin", "url"],
            cwd=self.repo,
            input="refs/heads/feature 1 refs/heads/feature 0\n",
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["gate"])
        self.assertIn("skipping non-executable foreign hook", result.stderr)

    def test_legacy_managed_hook_migrates_foreign_chain(self) -> None:
        agent = self.root / "agent"
        log = self.root / "migration.log"
        self._fake_gate(agent, log)
        hooks = self._active_hooks()
        original = self._foreign_hook(hooks)
        original_bytes = original.read_bytes()
        original.replace(hooks / INSTALL.LEGACY_FOREIGN_HOOK_NAME)

        hook = hooks / "pre-push"
        legacy_bytes = f"#!/bin/sh\n{INSTALL.LEGACY_MANAGED_MARKER}\nexit 0\n".encode()
        hook.write_bytes(legacy_bytes)
        hook.chmod(0o755)
        stale_backup = hooks / INSTALL.FOREIGN_HOOK_NAME
        stale_backup.write_bytes(legacy_bytes)
        stale_backup.chmod(0o755)

        INSTALL.install_review_hook(self.repo, agent)
        self.assertIn(INSTALL.MANAGED_MARKER.encode(), hook.read_bytes())
        self.assertEqual(stale_backup.read_bytes(), original_bytes)
        environment = os.environ.copy()
        environment["OMP_TEST_LOG"] = str(log)
        result = subprocess.run(
            [str(hook), "origin", "url"],
            cwd=self.repo,
            input="refs/heads/feature 1 refs/heads/feature 0\n",
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["foreign", "gate"])

    def test_ambiguous_legacy_foreign_hooks_fail_closed(self) -> None:
        agent = self.root / "agent"
        log = self.root / "ambiguous.log"
        self._fake_gate(agent, log)
        hooks = self._active_hooks()
        hooks.mkdir(parents=True, exist_ok=True)
        hook = hooks / "pre-push"
        hook.write_text(
            f"#!/bin/sh\n{INSTALL.LEGACY_MANAGED_MARKER}\nexit 0\n",
            encoding="utf-8",
        )
        hook.chmod(0o755)
        current_foreign = hooks / INSTALL.FOREIGN_HOOK_NAME
        current_foreign.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        current_foreign.chmod(0o755)
        legacy_foreign = hooks / INSTALL.LEGACY_FOREIGN_HOOK_NAME
        legacy_foreign.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        legacy_foreign.chmod(0o755)

        with self.assertRaises(SystemExit):
            INSTALL.install_review_hook(self.repo, agent)
        self.assertIn(INSTALL.LEGACY_MANAGED_MARKER, hook.read_text(encoding="utf-8"))
        self.assertTrue(current_foreign.exists())
        self.assertTrue(legacy_foreign.exists())

    def test_stale_marker_is_replaced_and_install_is_idempotent(self) -> None:
        agent = self.root / "agent"
        log = self.root / "idempotence.log"
        self._fake_gate(agent, log)
        hooks = self._active_hooks()
        hooks.mkdir(parents=True, exist_ok=True)
        hook = hooks / "pre-push"
        hook.write_text(f"#!/bin/sh\n{INSTALL.MANAGED_MARKER}\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)

        INSTALL.install_review_hook(self.repo, agent)
        expected = INSTALL._managed_hook_content(agent)
        self.assertEqual(hook.read_bytes(), expected)
        first = hook.read_bytes()
        INSTALL.install_review_hook(self.repo, agent)
        self.assertEqual(hook.read_bytes(), first)
        self.assertFalse((hooks / INSTALL.FOREIGN_HOOK_NAME).exists())


class ProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="omp-provenance-test-")
        self.root = Path(self.temp.name)
        external = self.root / "global" / "external"
        external.mkdir(parents=True)
        for name in ("openclaw-autoreview", "cursor-thermos"):
            shutil.copytree(ROOT / "global" / "external" / name, external / name)
        shutil.copy2(ROOT / "global" / "external" / "registry.yaml", external / "registry.yaml")
        skills = self.root / "global" / "skills"
        skills.mkdir(parents=True)
        projections = {
            "autoreview": external / "openclaw-autoreview",
            "thermo-nuclear-review": external / "cursor-thermos" / "thermo-nuclear-review",
            "thermo-nuclear-code-quality-review": external / "cursor-thermos" / "thermo-nuclear-code-quality-review",
        }
        for name, source in projections.items():
            (skills / name).symlink_to(source, target_is_directory=True)
        self.original_root = CHECK.ROOT
        CHECK.ROOT = self.root
        self.contract = SimpleNamespace(
            surface=lambda name: SimpleNamespace(source=skills),
        )

    def tearDown(self) -> None:
        CHECK.ROOT = self.original_root
        self.temp.cleanup()

    def _receipt(self, repo: str) -> Path:
        name = "openclaw-autoreview" if repo == "openclaw/agent-skills" else "cursor-thermos"
        return self.root / "global" / "external" / name / ".sync-meta.json"

    def _reject(self) -> None:
        with self.assertRaises(SystemExit):
            CHECK.check_external_skills(self.contract)

    def test_payload_tamper_is_rejected_by_content_hash(self) -> None:
        payload = self.root / "global" / "external" / "openclaw-autoreview" / "scripts" / "autoreview"
        payload.write_text(payload.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
        self._reject()

    def test_extra_vendor_file_is_rejected(self) -> None:
        extra = self.root / "global" / "external" / "cursor-thermos" / "unexpected.txt"
        extra.write_text("extra", encoding="utf-8")
        self._reject()

    def test_escaped_license_path_is_rejected(self) -> None:
        receipt = self._receipt("openclaw/agent-skills")
        metadata = json.loads(receipt.read_text(encoding="utf-8"))
        metadata["license_path"] = "../outside-license"
        receipt.write_text(json.dumps(metadata), encoding="utf-8")
        self._reject()

    def test_symlinked_payload_is_rejected(self) -> None:
        payload = self.root / "global" / "external" / "cursor-thermos" / "thermo-nuclear-review" / "SKILL.md"
        payload.unlink()
        payload.symlink_to(self.root / "outside-skill.md")
        (self.root / "outside-skill.md").write_text("MIT License", encoding="utf-8")
        self._reject()


    def test_projected_skill_wrong_vendor_target_is_rejected(self) -> None:
        projected = self.root / "global" / "skills" / "autoreview"
        projected.unlink()
        projected.symlink_to(self.root / "global" / "external" / "cursor-thermos" / "thermo-nuclear-review", target_is_directory=True)
        self._reject()

    def test_projected_skill_outside_target_is_rejected(self) -> None:
        projected = self.root / "global" / "skills" / "autoreview"
        projected.unlink()
        outside = self.root / "outside-autoreview"
        outside.mkdir()
        projected.symlink_to(outside, target_is_directory=True)
        self._reject()

    def test_receipt_source_suffix_is_bound_to_registry(self) -> None:
        receipt = self._receipt("openclaw/agent-skills")
        metadata = json.loads(receipt.read_text(encoding="utf-8"))
        metadata["src_path_suffix"] = "skills/not-autoreview"
        receipt.write_text(json.dumps(metadata), encoding="utf-8")
        self._reject()

if __name__ == "__main__":
    unittest.main()
