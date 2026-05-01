from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_post_p50_remediation.py"


class ValidatePostP50RemediationScriptTestCase(unittest.TestCase):
    def test_validator_passes_plain(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("post-p50 remediation validation passed", completed.stdout)

    def test_validator_json_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["check_id"], "post_p50_remediation_v0")
        self.assertEqual(payload["required_item_count"], 11)
        self.assertEqual(payload["errors"], [])


if __name__ == "__main__":
    unittest.main()
