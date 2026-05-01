from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_static_deployment_evidence.py"


class StaticDeploymentEvidenceValidatorTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Static deployment evidence validation", completed.stdout)
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("artifact_root: site/dist", completed.stdout)

    def test_validator_json_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["report_id"], "static_deployment_evidence_v0")
        self.assertEqual(payload["artifact_root"], "site/dist")
        self.assertFalse(payload["deployment_verified"])
        self.assertFalse(payload["deployment_success_claimed"])
        self.assertEqual(payload["errors"], [])


if __name__ == "__main__":
    unittest.main()
