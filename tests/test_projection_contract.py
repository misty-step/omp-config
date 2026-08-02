from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT / "bin") not in sys.path:
    sys.path.insert(0, str(ROOT / "bin"))

from config_contract import load_contract, require_projection


class ProjectionContractTests(unittest.TestCase):
    def test_review_runtime_surfaces_include_all_six_python_modules(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-projection-") as temporary:
            contract = load_contract(ROOT, projection_root=Path(temporary) / "agent")
            for surface in contract.surfaces:
                surface.target.parent.mkdir(parents=True, exist_ok=True)
                surface.target.symlink_to(surface.source, target_is_directory=surface.kind == "directory")
            require_projection(contract)
            expected = {
                "review_gate_binary": "bin/review_gate.py",
                "review_runner_binary": "bin/review_runner.py",
                "review_common_binary": "bin/review_common.py",
                "review_bundle_binary": "bin/review_bundle.py",
                "review_packet_binary": "bin/review_packet.py",
                "review_receipt_binary": "bin/review_receipt.py",
            }
            self.assertEqual(len(contract.surfaces), 22)
            for name, relative in expected.items():
                surface = contract.surface(name)
                self.assertEqual(surface.source, ROOT / relative)
                self.assertEqual(surface.target_rel, Path(relative))
                self.assertTrue(surface.target.is_file())
                self.assertEqual(surface.target.resolve(), surface.source)
        self.assertIn(Path("bin"), contract.excluded_runtime_state)



    def test_projected_hook_imports_sibling_bin_surface(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-hook-projection-") as temporary:
            agent = Path(temporary) / "agent"
            hooks = agent / "hooks"
            binaries = agent / "bin"
            hooks.mkdir(parents=True)
            binaries.mkdir()
            shutil.copy2(ROOT / "global" / "hooks" / "review-gate.py", hooks / "review-gate.py")
            marker = Path(temporary) / "marker"
            (binaries / "review_gate.py").write_text(
                "from pathlib import Path\n"
                f"def main(args):\n    Path({str(marker)!r}).write_text('sibling', encoding='utf-8')\n    return 0\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(hooks / "review-gate.py"), "hook"],
                cwd=temporary,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "sibling")

    def test_projected_claude_hook_imports_sibling_safety_package(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-claude-hook-projection-") as temporary:
            agent = Path(temporary) / "agent"
            hooks = agent / "hooks"
            hooks.mkdir(parents=True)
            shutil.copy2(ROOT / "global" / "hooks" / "claude-safety.py", hooks / "claude-safety.py")
            shutil.copytree(ROOT / "global" / "lib" / "claude_safety", agent / "lib" / "claude_safety")
            result = subprocess.run(
                [sys.executable, str(hooks / "claude-safety.py"), "claude-hook", "time-context"],
                cwd=temporary,
                input="{}",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"result":"continue"', result.stdout)


if __name__ == "__main__":
    unittest.main()
