from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_local_cache_privacy_policy.py"


class ValidateLocalCachePrivacyPolicyScriptTestCase(unittest.TestCase):
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
        self.assertIn("no_telemetry_implemented: True", result.stdout)

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
        self.assertEqual(payload["privacy_default"], "local_private_off_by_default")
        self.assertTrue(payload["no_cache_runtime_implemented"])
        self.assertTrue(payload["no_private_ingestion_implemented"])
        self.assertTrue(payload["no_telemetry_implemented"])
        self.assertTrue(payload["no_accounts_implemented"])
        self.assertTrue(payload["no_cloud_sync_implemented"])


if __name__ == "__main__":
    unittest.main()
