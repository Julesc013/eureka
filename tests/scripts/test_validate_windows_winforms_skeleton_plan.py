from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_windows_winforms_skeleton_plan.py"


class ValidateWindowsWinFormsSkeletonPlanScriptTestCase(unittest.TestCase):
    def test_plain_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status: valid", result.stdout)
        self.assertIn("lane_id: windows_7_x64_winforms_net48", result.stdout)
        self.assertIn("native_project_files: 0", result.stdout)

    def test_json_validator_passes_and_parses(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["lane_id"], "windows_7_x64_winforms_net48")
        self.assertEqual(payload["proposed_project_path"], "clients/windows/winforms-net48/")
        self.assertEqual(payload["proposed_namespace"], "Eureka.Clients.Windows.WinForms")
        self.assertTrue(payload["human_approval_required"])
        self.assertEqual(payload["native_project_file_count"], 0)


if __name__ == "__main__":
    unittest.main()

