from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_static_artifact_promotion_review.py"


class StaticArtifactPromotionReviewValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("active_static_artifact: site/dist", completed.stdout)
        self.assertIn("github_actions_status: unverified", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["decision"], "conditionally_promoted_pending_github_actions_evidence")
        self.assertEqual(payload["active_static_artifact"], "site/dist")
        self.assertEqual(payload["workflow_upload_path"], "site/dist")


if __name__ == "__main__":
    unittest.main()
