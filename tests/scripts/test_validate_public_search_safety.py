from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_public_search_safety.py"


class PublicSearchSafetyValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("first_allowed_mode: local_index_only", completed.stdout)
        self.assertIn("telemetry_default: off", completed.stdout)

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
        self.assertEqual(
            payload["safety_policy_id"], "eureka-public-search-safety-abuse-guard-v0"
        )
        self.assertEqual(payload["allowed_modes"], ["local_index_only"])
        self.assertIn("live_probe", payload["disabled_modes"])
        self.assertEqual(payload["max_query_length"], 160)
        self.assertEqual(payload["max_result_limit"], 25)


if __name__ == "__main__":
    unittest.main()
