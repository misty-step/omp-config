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

from config_contract import load_contract


class ProjectionContractTests(unittest.TestCase):
    def test_review_gate_binaries_are_declared_projection_surfaces(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-projection-") as temporary:
            contract = load_contract(ROOT, projection_root=Path(temporary) / "agent")
        self.assertEqual(len(contract.surfaces), 18)
        self.assertEqual(contract.surface("review_gate_binary").target_rel, Path("bin/review_gate.py"))
        self.assertEqual(contract.surface("review_runner_binary").target_rel, Path("bin/review_runner.py"))
        self.assertEqual(contract.surface("review_gate_hook").target_rel, Path("hooks/review-gate.py"))
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


if __name__ == "__main__":
    unittest.main()
