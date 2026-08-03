from __future__ import annotations

import runpy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

CHECK = runpy.run_path(str(BIN_DIR / "check"))
check_model_selector = CHECK["check_model_selector"]
check_model_routes = CHECK["check_model_routes"]
check_task_settings = CHECK["check_task_settings"]
check_retired_skill_names = CHECK["check_retired_skill_names"]


class DispatchContractTests(unittest.TestCase):
    def _settings(self, text: str) -> Path:
        directory = tempfile.TemporaryDirectory(prefix="dispatch-contract-")
        self.addCleanup(directory.cleanup)
        settings = Path(directory.name) / "config.yml"
        settings.write_text(text)
        return settings

    def test_current_global_routes_and_task_settings_are_valid(self) -> None:
        settings = ROOT / "global" / "config.yml"
        check_model_routes(settings)
        check_task_settings(settings)

    def test_valid_route_choices_are_not_preference_pinned(self) -> None:
        settings = self._settings(
            "modelRoles:\n"
            "  smol: provider/compact:medium\n"
            "  default: provider/general:max\n"
            "retry:\n"
            "  fallbackChains:\n"
            "    smol:\n"
            "      - provider/backup:low\n"
            "    default:\n"
            "      - provider/other:xhigh\n"
            "task:\n"
            "  maxRecursionDepth: 1\n"
            "  maxConcurrency: 3\n"
            "  disabledAgents:\n"
            "    - bundled-agent\n"
        )

        check_model_routes(settings)
        check_task_settings(settings)

    def test_route_roles_require_matching_fallback_roles(self) -> None:
        settings = self._settings(
            "modelRoles:\n"
            "  default: provider/general:high\n"
            "retry:\n"
            "  fallbackChains:\n"
            "    other:\n"
            "      - provider/backup:high\n"
        )

        with self.assertRaises(SystemExit):
            check_model_routes(settings)

    def test_task_settings_reject_duplicate_disabled_agents(self) -> None:
        settings = self._settings(
            "task:\n"
            "  maxRecursionDepth: 2\n"
            "  maxConcurrency: 4\n"
            "  disabledAgents:\n"
            "    - task\n"
            "    - task\n"
        )

        with self.assertRaises(SystemExit):
            check_task_settings(settings)

    def test_retired_quality_skill_names_cannot_return(self) -> None:
        with self.assertRaises(SystemExit):
            check_retired_skill_names({"quality", "quality-tests"})

        check_retired_skill_names({"quality", "deliver", "research"})


    def test_model_selectors_reject_invalid_shape(self) -> None:
        with self.assertRaises(SystemExit):
            check_model_selector("agent builder", "missing-provider")

        check_model_selector("agent builder", "provider/model:max")
        check_model_selector("agent builder fallback", "other-provider/other-model")


if __name__ == "__main__":
    unittest.main()
