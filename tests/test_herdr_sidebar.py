from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HerdrSidebarOwnershipTests(unittest.TestCase):
    def test_installed_herdr_extension_is_declared_and_projected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="omp-herdr-sidebar-test-") as temp:
            agent_dir = Path(temp)
            extension = agent_dir / "extensions" / "herdr-sidebar.ts"
            extension.parent.mkdir()
            extension.write_text("user-owned herdr extension\n")
            env = {**os.environ, "PI_CODING_AGENT_DIR": str(agent_dir)}

            install = subprocess.run(
                [str(ROOT / "bin" / "install")],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            self.assertTrue(extension.is_symlink())
            self.assertEqual(extension.resolve(), (ROOT / "global/extensions/herdr-sidebar.ts").resolve())

            check = subprocess.run(
                [str(ROOT / "bin" / "check"), "--installed"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertNotIn("foreign-writer audit", check.stderr + check.stdout)


if __name__ == "__main__":
    unittest.main()
