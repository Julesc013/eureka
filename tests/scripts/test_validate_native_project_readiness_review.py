from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_native_project_readiness_review.py"


class ValidateNativeProjectReadinessReviewScriptTestCase(unittest.TestCase):
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
        self.assertIn(
            "decision: ready_for_minimal_project_skeleton_after_human_approval",
            result.stdout,
        )

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
        self.assertEqual(
            payload["decision"],
            "ready_for_minimal_project_skeleton_after_human_approval",
        )
        self.assertEqual(payload["first_candidate_lane"], "windows_7_x64_winforms_net48")
        self.assertTrue(payload["human_approval_required"])
        self.assertEqual(payload["project_file_count"], 0)


if __name__ == "__main__":
    unittest.main()

