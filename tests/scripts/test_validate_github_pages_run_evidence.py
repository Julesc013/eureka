from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_github_pages_run_evidence.py"


class GitHubPagesRunEvidenceValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("workflow_upload_path: site/dist", completed.stdout)
        self.assertIn("overall_decision: failed", completed.stdout)
        self.assertIn("success_claim_allowed: False", completed.stdout)

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
        self.assertEqual(payload["report_id"], "github_pages_run_evidence_v0")
        self.assertEqual(payload["workflow_upload_path"], "site/dist")
        self.assertEqual(payload["overall_decision"], "failed")
        self.assertFalse(payload["success_claim_allowed"])


if __name__ == "__main__":
    unittest.main()
