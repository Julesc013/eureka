from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_public_search_safety_evidence.py"


class ValidatePublicSearchSafetyEvidenceScriptTest(unittest.TestCase):
    def test_plain_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("blocked_request_count: 32", completed.stdout)

    def test_json_validator_passes_and_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["report_id"], "public_search_safety_evidence_v0")
        self.assertEqual(payload["safe_query_count"], 4)
        self.assertEqual(payload["blocked_request_count"], 32)
        self.assertIn("local_path", payload["forbidden_categories"])
        self.assertIn("url_fetch", payload["forbidden_categories"])


if __name__ == "__main__":
    unittest.main()
